from gold.util.CustomExceptions import InvalidRunSpecException
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import PickleStaticFile
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.ProcTrackOptions import ProcTrackOptions
from quick.gwas.GwasResults import EnrichmentGwasResults, HypothesisTestingGwasResults
from quick.gwas.MultiGwasResults import MultiGwasResults
from quick.webtools.GeneralGuiTool import GeneralGuiTool


#TEMP_NUM_BATCH_RUNS_SO_FAR = 0


def directGetTestResults(diseaseTrack, refTrackLeaf, refTrackBase, kernelType, kernelParam, refTrackCoverageFunction, nullmodel, mcDepth='high', useCache=True, printProgress=False):
    RETRIEVE_FROM_CACHE = useCache
    STORE_TO_CACHE = useCache
    if mcDepth=='high':
        mcParams = 'fdrThreshold=1.0,globalPvalThreshold=0.00002,maxSamples=50000,numResamplings=100,numSamplesPerChunk=50,mThreshold=20,fdrCriterion=simultaneous'
    elif mcDepth=='relatively high':
        mcParams = 'fdrThreshold=1.0,globalPvalThreshold=0.0001,maxSamples=10000,numResamplings=100,numSamplesPerChunk=50,mThreshold=20,fdrCriterion=simultaneous'
    elif mcDepth=='moderate':
        mcParams = 'fdrThreshold=1.0,globalPvalThreshold=0.001,maxSamples=1000,numResamplings=50,numSamplesPerChunk=50,mThreshold=10,fdrCriterion=simultaneous'
    elif mcDepth=='low':
        mcParams = 'fdrThreshold=1.0,globalPvalThreshold=1.0,maxSamples=10,numResamplings=10,numSamplesPerChunk=10,mThreshold=20,fdrCriterion=simultaneous'
    elif mcDepth=='extremely low':
        mcParams = 'fdrThreshold=1.0,globalPvalThreshold=1.0,maxSamples=2,numResamplings=2,numSamplesPerChunk=10,mThreshold=20,fdrCriterion=simultaneous'
    else:
        raise
    
    if kernelType=='gaussian':
        kernelParamAssignment = ',kernelStdev=%s'%kernelParam
        spreadParamAssignment = ',spreadParam=%s'%kernelParam
    elif kernelType=='divideByOffset':
        kernelParamAssignment = ',minimumOffsetValue=%s'%kernelParam
        spreadParamAssignment = ',spreadParam=%s'%kernelParam
    elif kernelType=='binSizeNormalized':
        kernelParamAssignment = ''
        spreadParamAssignment = ''
    elif kernelType=='catCoverageNormalized':
        kernelParamAssignment = ''
        spreadParamAssignment = ''
    elif kernelType=='binSizeNormalizedV2':
        kernelParamAssignment = ''
        spreadParamAssignment = ''
        assert nullmodel in ['RandomGenomeLocationTrack_','PermutedSegsAndSampledIntersegsTrack_'] #with last option, the end result would be about the same in the corresponding three track version..
        nullmodel = 'RandomGenomeLocationTrack_'
    elif kernelType=='binSizeNormalizedV3':
        kernelParamAssignment = ''
        spreadParamAssignment = ''
    elif kernelType=='uniform':
        kernelParamAssignment = ''
        spreadParamAssignment = ''
    else:
        raise #RuntimeError('unre'

    #if nullmodel=='SegsSampledByDistanceToReferenceTrack_':
    #    exonRefTrack = ',trackNameIntensity=Genes and gene subsets^Exons^Ensembl exons'
    #else:
    #    exonRefTrack = ''
    import urllib
    if kernelType == 'binSizeNormalizedV2':
        batchText ='''
@TraitBins = %s
@TN1=%s:%s
@TN2=%s
@rawStat=rawStatistic=DiffRelCoverageMainValueStat
@assump=assumptions=%s
@randParams=randomSeed=Random,tail=more,@assump
@mcParams=%s
@conv=tf1=TrivialFormatConverter,tf2=TrivialFormatConverter
@kernelParams=kernelType=binSizeNormalized
hg19|track|@TraitBins|@TN1|@TN2|RandomizationManagerStat(@rawStat,globalSource=userbins,@mcParams,@randParams,@conv,@kernelParams,includeFullNullDistribution=yes)
''' % (urllib.quote(diseaseTrack), refTrackBase, refTrackLeaf, refTrackBase,nullmodel,mcParams,kernelType, spreadParamAssignment, kernelParamAssignment)
    else:
        batchText ='''
@TN1= %s
@TN2s=%s:%s
@extraTracks=%s
@binning=__chrArms__|*
@rawStat=rawStatistic=ThreeTrackT2inT1vsT3inT1KernelVersionStat
@assump=assumptions=%s
@randParams=randomSeed=Random,tail=more,@assump
@mcParams=%s
@conv=tf1=TrivialFormatConverter,tf2=TrivialFormatConverter
@kernelParams=kernelType=%s%s%s
hg19|@binning|@TN1|@TN2s|RandomizationManagerStat(@rawStat,globalSource=userbins,@mcParams,@randParams,@conv,extraTracks=@extraTracks,@kernelParams,silentProgress=yes)
''' % (diseaseTrack, refTrackBase, refTrackLeaf, refTrackCoverageFunction,nullmodel,mcParams,kernelType, spreadParamAssignment, kernelParamAssignment)
#    '''
#@bins=%s
#@TNs=%s:%s
#@TNunion=%s
#hg19|track|@bins|@TNs|@TNunion|DiffRelCoverageStat(globalSource=chrs,tf1=TrivialFormatConverter,tf2=TrivialFormatConverter,withOverlaps=yes,kernelType=%s%s)
#''' % (diseaseTrack, refTrackBase, refTrackLeaf, refTrackBase,kernelType, kernelParamAssignment)
    #print 'BATCHLINE: <br>', batchText

    import hashlib
    hashName = hashlib.sha1(batchText).hexdigest()
    sf = PickleStaticFile(['files','Caches','Tool7',hashName])
        

    if RETRIEVE_FROM_CACHE and sf.fileExists():
        print ',',
        #print 'Retrieving batch result (%s): %s' % (sf.getDiskPath(), batchText)
        #return shelf[batchText]
        return sf.loadPickledObject()
    else:
        print '.',
        #print 'Running batch: ', batchText
        #shelf.close()
        batchLines = batchText.split('\n')
        from quick.application.GalaxyInterface import GalaxyInterface
        res = GalaxyInterface.runBatchLines(batchLines, username='geirkjetil@gmail.com', printResults=False, printProgress = printProgress)[0]
        #print 'Running batchLines (%s): %s<br>Getting result: %s<br>' % ('', batchLines, res) #TEMP_NUM_BATCH_RUNS_SO_FAR
        res.batchText = batchText
        if STORE_TO_CACHE:
            sf.storePickledObject(res)
        return res

def directGetEnrichment(diseaseTrack, refTrackLeaf, refTrackBase, kernelType, kernelParam, useCache=True, printProgress=False):
    RETRIEVE_FROM_CACHE = useCache
    STORE_TO_CACHE = useCache
    if kernelType=='gaussian':
        kernelParamAssignment = ',kernelStdev=%s'%kernelParam
    elif kernelType=='divideByOffset':
        kernelParamAssignment = ',minimumOffsetValue=%s'%kernelParam
    elif kernelType=='binSizeNormalized':
        kernelParamAssignment = ''
    elif kernelType=='catCoverageNormalized':
        kernelParamAssignment = ''
    elif kernelType=='uniform':
        kernelParamAssignment = ''
    else:
        raise #RuntimeError('unre'
    batchText = '''
@bins=%s
@TNs=%s:%s
@TNunion=%s
hg19|track|@bins|@TNs|@TNunion|DiffRelCoverageStat(globalSource=chrs,tf1=TrivialFormatConverter,tf2=TrivialFormatConverter,withOverlaps=yes,kernelType=%s%s)
''' % (diseaseTrack, refTrackBase, refTrackLeaf, refTrackBase,kernelType, kernelParamAssignment)
    #print 'BATCHLINE: <br>', batchText
    import hashlib
    hashName = hashlib.sha1(batchText).hexdigest()
    sf = PickleStaticFile(['files','Caches','Tool7',hashName])
    #shelf = shelve.open(sf.getDiskPath(True))
    #if batchText in shelf:    
    if RETRIEVE_FROM_CACHE and sf.fileExists():
        print ',',
        #print 'Retrieving batch result (%s): %s' % (sf.getDiskPath(), batchText)
        #return shelf[batchText]
        return sf.loadPickledObject()
    else:
        print '.',
        #print 'Running batch: ', batchText
        #shelf.close()
        batchLines = batchText.split('\n')
        from quick.application.GalaxyInterface import GalaxyInterface
        res = GalaxyInterface.runBatchLines(batchLines, username='geirkjetil@gmail.com', printResults=False, printProgress = printProgress)[0]
    #global TEMP_NUM_BATCH_RUNS_SO_FAR
    #print 'Running batchLines (%s): %s<br>Getting result: %s<br>' % (TEMP_NUM_BATCH_RUNS_SO_FAR, batchLines, res)
    #TEMP_NUM_BATCH_RUNS_SO_FAR += 1
        #shelf = shelve.open(sf.getDiskPath(True))
        #shelf[batchText] = res
        #shelf.close()
        res.batchText = batchText
        if STORE_TO_CACHE:
            sf.storePickledObject(res)
        return res
        

class AnalyzeFunctionalGenomicsOfGwasTracks(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Analyze functional genomics of multiple GWAS tracks"

    @staticmethod
    def getInputBoxNames():
        return ['Genome','GWAS Source','Select disease catalog','Flank size','Reference data','Normalization','Type of analysis','Kernel type','Kernel parameter', 'Null model', 'Level of result details', 'MC sampling depth', 'Include compiled local result tables', 'Reference track selection', 'Select single reference track', 'Use cache', 'Print detailed progress', 'Supply prior coloring'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]
        #Should insert a 'Select track' to handle GWAS from history..

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod    
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()
        return '__genome__'
        #return ['hg19']

    @staticmethod    
    def getOptionsBox2(prevChoices): # Alternatively: getOptionsBoxKey1()
        return ['Prepared catalogues','Custom track']

    @staticmethod    
    def getInfoForOptionsBox2(prevChoices):
        return '<b>Prepared catalogues</b>'

    @staticmethod    
    def getInfoForOptionsBox3(prevChoices):
        return 'WTF ??'

    @staticmethod    
    def getOptionsBox3(prevChoices): # Alternatively: getOptionsBoxKey1()
        if prevChoices[-2]=='Prepared catalogues':   
            return ['GiulioNewGwas','GiulioAllGwas','GiulioMay13Gwas', 'SmallTest']
        elif prevChoices[-2] not in ['', None]:
            return '__track__'
    
    @staticmethod    
    def getOptionsBox4(prevChoices): # Alternatively: getOptionsBoxKey1()
        if prevChoices[-2] == 'GiulioMay13Gwas':
            return ['Linkage regions']
        elif prevChoices[-2] == 'SmallTest':
            return ['SmallTest']
        else:
            return ['SNPs','2kb','10kb','25kb','50kb']
    
    @staticmethod    
    def getOptionsBox5(prevChoices): # Alternatively: getOptionsBoxKey2()
        '''
        See getOptionsBox1().
        
        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        #return ['DHS','Chromatin','H3K4me3','TF'] #'QuickTest'
        return ['DHS','H3K4me3','Chromatin state 1-AP','Chromatin state 4-SE','Chromatin state 5-SE'] 
        
    @staticmethod    
    def getOptionsBox6(prevChoices):
        return ['BinaryCoverage','CoverageDepth']

    @staticmethod    
    def getOptionsBox7(prevChoices):
        return ['Enrichment','Testing']


    @staticmethod    
    def getOptionsBox8(prevChoices):
        return ['uniform','binSizeNormalized','catCoverageNormalized','binSizeNormalizedV2','binSizeNormalizedV3','gaussian','divideByOffset']

    @staticmethod    
    def getOptionsBox9(prevChoices):
        if prevChoices[-2] in ['gaussian','divideByOffset']:
            return ''

    @staticmethod    
    def getOptionsBox10(prevChoices):
        if prevChoices[-4] == 'Testing':
            return ['Sample disease regions uniformly', 'Sample disease regions with preserved inter-region spacings','Sample disease regions with preserved distance to nearest exon']

    @staticmethod    
    def getOptionsBox11(prevChoices):
        return ['Include links to full underlying results','Only produce main result values']

    @staticmethod    
    def getOptionsBox12(prevChoices):
        if prevChoices[-6] == 'Testing':
            return ['low','moderate','relatively high','high','extremely low']

    @staticmethod    
    def getOptionsBox13(prevChoices):        
        return ['no','yes']

    @staticmethod    
    def getOptionsBox14(prevChoices):        
        return ['Use all reference tracks','Select single reference track', 'Select a range among all reference tracks']

    @staticmethod    
    def getOptionsBox15(prevChoices):
        if prevChoices[-2]=='Select single reference track':
            assert prevChoices[4]=='DHS'
            genome = prevChoices[0]
            tn = 'Private:GK:Psych:DHSs'.split(':')
            return ProcTrackOptions.getSubtypes(genome, tn, True)
        elif prevChoices[-2]=='Select a range among all reference tracks':
            return ''
        
    @staticmethod    
    def getOptionsBox16(prevChoices):
        return ['yes','no']

    @staticmethod    
    def getOptionsBox17(prevChoices):
        return ['no','yes']
    
    
    @staticmethod    
    def getOptionsBox18(prevChoices):
        return '__history__', 'tabular'
    
    @staticmethod
    def getDemoSelections():
        return ['hg19','Prepared catalogues','GiulioNewGwas','2kb','H3K4me3','CoverageDepth','Enrichment','uniform','','','','Only produce main result values']
        #['Genome','GWAS Source','Select disease catalog','Flank size','Reference data','Normalization','Type of analysis','Kernel type','Kernel parameter', 'Null model', 'Level of result details']

    @staticmethod    
    def execute(choices, galaxyFn=None, username=''):
        #setupDebugModeAndLogging()
        from time import time
        startTime=time()        
        print HtmlCore().begin()
        print '<pre>'        
        genome = choices[0]
        #assert genome=='hg19'
        flankSize=choices[3]
        
        if choices[1]=='Prepared catalogues':
            if choices[2]=='GiulioNewGwas':
                gwasTnBase = 'Private:GK:NewGwasBase'.split(':')
            elif choices[2]=='GiulioAllGwas':
                gwasTnBase = 'Private:GK:AllGiulioGwasSnpsAsOf9feb13'.split(':')
            elif choices[2]=='GiulioMay13Gwas':
                gwasTnBase = 'Private:GK:Gwas:GiulioMay13'.split(':')                
            elif choices[2]=='SmallTest':
                gwasTnBase = 'Private:GK:Gwas'.split(':')
            else:
                raise
            
            gwasTnBase += [flankSize]
            
        elif choices[1] == 'Custom track':
            gwasTnBase = choices[2].split(':')
            assert flankSize=='SNPs'
        else:
            assert False, choices[1]
        referenceTrackSource = choices[4]
        normalization = choices[5]
        assert normalization == 'CoverageDepth'
        analysisType = choices[6]
        if analysisType == 'Enrichment':
            ResultClass = EnrichmentGwasResults
        elif analysisType == 'Testing':
            ResultClass = HypothesisTestingGwasResults
            nullmodelMapping = dict(zip(['Sample disease regions uniformly', 'Sample disease regions with preserved inter-region spacings', 'Sample disease regions with preserved distance to nearest exon'], ['PermutedSegsAndSampledIntersegsTrack_','PermutedSegsAndIntersegsTrack_', 'SegsSampledByDistanceToReferenceTrack_,trackNameIntensity=Genes and gene subsets^Exons^Ensembl exons']))        
            nullmodel = nullmodelMapping[choices[9]]
            assert nullmodel in ['PermutedSegsAndSampledIntersegsTrack_','PermutedSegsAndIntersegsTrack_','SegsSampledByDistanceToReferenceTrack_,trackNameIntensity=Genes and gene subsets^Exons^Ensembl exons']
        else:
            raise
        
        kernelType = choices[7]
        kernelParam = choices[8]

        if choices[10] == 'Include links to full underlying results':
            includeDetailedResults = True
        elif choices[10] == 'Only produce main result values':
            includeDetailedResults = False
        else:
            raise InvalidRunSpecException('Did not understand option: %s' % choices[12])
        
        mcDepth = choices[11]        

        if choices[12] == 'yes':
            includeLocalResults = True
        elif choices[12] == 'no':
            includeLocalResults  = False
        else:
            raise InvalidRunSpecException('Did not understand option: %s' % choices[12])

        if choices[15] == 'yes':
            useCache = True
        elif choices[15] == 'no':
            useCache = False
        else:
            raise InvalidRunSpecException('Did not understand option: %s' % choices[15])

        if choices[16] == 'yes':
            printProgress = True
        elif choices[16] == 'no':
            printProgress= False
        else:
            raise InvalidRunSpecException('Did not understand option: %s' % choices[16])
        
        from quick.application.GalaxyInterface import GalaxyInterface
        #print GalaxyInterface.getHtmlForToggles()
        #print GalaxyInterface.getHtmlBeginForRuns()
        #from quick.webtools.GwasAPI import getEnrichmentValues
        print 'Progress: '
        #print 'base: ',gwasTnBase
        #print 'leaves: ',GalaxyInterface.getSubTrackNames(genome, gwasTnBase,deep=False, username=username)
        disRes = MultiGwasResults()
        from gold.application.HyperBrowserCLI import getSubTrackLeafTerms
        from quick.application.ProcTrackOptions import ProcTrackOptions

        #for gwasTrackLeaf in GalaxyInterface.getSubTrackNames(genome, gwasTnBase,deep=False, username=username)[0]:
        allDiseases = getSubTrackLeafTerms(genome, gwasTnBase, username=username)
        if len(allDiseases)==0:
            assert ProcTrackOptions.isValidTrack(genome, gwasTnBase, GalaxyInterface.userHasFullAccess(username)), 'Genome: %s, TN: %s, Access: %s' % (genome, gwasTnBase, GalaxyInterface.userHasFullAccess(username))
            allDiseases = gwasTnBase[-1:]
            gwasTnBase = gwasTnBase[:-1]
            
        for disease in allDiseases:
            #print 'Leaf:',gwasTrackLeaf[0]
            #if not gwasTrackLeaf[0] in ['11 - Height.txt']:
            #if not disease in ['1 - Alzheimer.txt','10 - Graves.txt']:#['Malaria','UC']:
            #    print 'IGNORING: ', gwasTrackLeaf[0]
            #    continue
            
            #if gwasTrackLeaf in [[],None] or gwasTrackLeaf[0]=='-- All subtypes --':
                #continue
                            
            #gwasTn = ':'.join(gwasTnBase + [gwasTrackLeaf[0]])
            gwasTn = ':'.join(gwasTnBase + [disease])
            #print 'Running API: ', "$getEnrichmentValues(%s, '%s', '%s')" % ([gwasTn], referenceTrackSource, normalization)
            #enrichmentsDict = getEnrichmentValues([gwasTn], referenceTrackSource, normalization)#, ['114 - Brain_Mid_Frontal_Lobe.txt','134 - Rectal_Smooth_Muscle.txt'])
            #assert len(enrichmentsDict.values())==1
            #enrichments = enrichmentsDict.values()[0]
            
            #if gwasTrackLeaf[0] in ['Malaria','UC']:
            #print 'HERE IS WHAT I GOT: ',enrichmentsDict
            #print 'ENR: ',enrichments
            #print 'One: ', (enrichments.values()[0])['enrichment']['13 - CD4'].getGlobalResult()
            #assert 'enrichment' in (enrichments.values()[0]), (enrichments.values()[0])
            #disRes[gwasTrackLeaf[0]] = (enrichments.values()[0])['enrichment']
            #disRes[gwasTrackLeaf[0]] = (enrichments.values()[0])
            #disease = gwasTrackLeaf[0]
            #disRes[disease] = [x.getGlobalResult() for x in enrichments]
            #print 'DISres: ', disRes[gwasTrackLeaf[0]]
            #from quick.util.CommonFunctions import extractIdFromGalaxyFn
            
            res = ResultClass(gwasId=disease,verbose=True,galaxyFn=galaxyFn)
            #referenceSubTypes = enrichments.keys()
            #referenceSubTypes = [x[0] for x in GalaxyInterface.getSubTrackNames(genome, 'Private:GK:Psych:DHSs'.split(':'), deep=False, username=username)[0] if not x[0] == '-- All subtypes --']
            if referenceTrackSource=='H3K4me3':
                refTrackBase = 'Private:GK:Psych:H3K4me3'
                refTrackCoverageFunction = 'Private^GK^Psych^H3K4me3CoverageTrack'
            elif referenceTrackSource=='DHS':
                refTrackBase = 'Private:GK:Psych:DHSs'
                refTrackCoverageFunction = 'Private^GK^Psych^DHSCoverageTrack'
            elif referenceTrackSource=='Chromatin state 1-AP':
                refTrackBase = 'Private:Anders:Chromatin State Segmentation:1_Active_Promoter'
                refTrackCoverageFunction = 'Private^GWAS^Chromatin^CoverageFunctionTracks^1_Active_PromoterV2'
            elif referenceTrackSource=='Chromatin state 4-SE':
                refTrackBase = 'Private:Anders:Chromatin State Segmentation:4_Strong_Enhancer'
                refTrackCoverageFunction = 'Private^GWAS^Chromatin^CoverageFunctionTracks^4_Strong_Enhancer'
            elif referenceTrackSource=='Chromatin state 5-SE':
                refTrackBase = 'Private:Anders:Chromatin State Segmentation:5_Strong_Enhancer'
                refTrackCoverageFunction = 'Private^GWAS^Chromatin^CoverageFunctionTracks^5_Strong_Enhancer'
            else:
                raise
            refTrackSelectType = choices[13]
            
            allReferenceTracks = [x[0] for x in GalaxyInterface.getSubTrackNames(genome, refTrackBase.split(':'), deep=False, username=username)[0] if not x[0] == '-- All subtypes --']
            if refTrackSelectType == 'Use all reference tracks':
                referenceSubTypes = allReferenceTracks
            elif refTrackSelectType == 'Select single reference track':
                referenceSubTypes = [choices[14]]
                assert referenceSubTypes[0] in allReferenceTracks
            elif refTrackSelectType == 'Select a range among all reference tracks':
                try:
                    firstRefTrack, lastRefTrack = choices[14].split('-')
                    referenceSubTypes = allReferenceTracks[int(firstRefTrack): int(lastRefTrack)+1]
                    print 'Analyzing %s among a total of %s reference tracks' % (choices[14], len(allReferenceTracks))
                except Exception:
                    print 'Range format should be e.g. "15-18".'
                    raise
            else:
                raise
            
            for referenceSubType in referenceSubTypes:
                #if not referenceSubType in ['107 - Adult_Kidney.txt','106 - Adipose_Nuclei.txt']:
                #    #print 'IGNORING: ',referenceSubType
                #    continue
                #
                if analysisType == 'Enrichment':
                    res[referenceSubType] = directGetEnrichment(gwasTn, referenceSubType,refTrackBase,kernelType, kernelParam, useCache, printProgress)
                elif analysisType == 'Testing':
                    res[referenceSubType] = directGetTestResults(gwasTn, referenceSubType,refTrackBase,kernelType, kernelParam, refTrackCoverageFunction, nullmodel, mcDepth, useCache, printProgress)
                else:
                    raise
                
                #print disease, referenceSubType, res[referenceSubType]
                #print "ENR: ",enrichments
                #res[referenceSubType] = enrichments[referenceSubType]
            disRes[disease] = res

        #for disease in disRes:
        #    print 'D FULL %s:' %disease, disRes[disease]
        #    print 'D DICTS %s:'%disease, disRes[disease].getAllGlobalResultDicts()
        #    print 'DISEASE %s:'%disease, disRes[disease].getAllGlobalResults()
        print 'Total run time (excluding figure generation): %i seconds.' % (time()-startTime)
        print '</pre>'
        #print GalaxyInterface.getHtmlBeginForRuns()
        
        print '<h1>Results</h1>'
        if len(allDiseases)>1:
            try:
                heatMapLink = disRes.getLinkToClusteredHeatmap('Heatmap', galaxyFn)
                print '<h3>Heatmap</h3>', heatMapLink#, '<br>'
            except:
                print '<p>Creation of heatmap failed</p>'
        tableOutput = disRes.getHtmlResultsTable(includeDetailedResults)
        print '<h3>Results table</h3>', tableOutput

        if choices[-1]:
            print '<h3>Prior coloring table</h3>'
            colorFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[-1].split(':'))
            print disRes.getColoredSortedReferencesTable(colorFn)
            
        if includeLocalResults:
            print '<h3>Local results</h3>'
            print disRes.getLinksToAllLocalHtmlResultsTables(galaxyFn)
        #rows = disRes.values()[0].keys()
        #
        #for row in rows:
        #    for col in disRes.keys():
        #        if disRes[col][row].getGlobalResult() is None:
        #            print 'MISSING GLOBAL RES: ', col,row,disRes[col][row]
        #core = HtmlCore()
        #core.tableHeader(['-']+disRes.keys(), sortable = True)
        #assert len(disRes)>0, 'No gwas Dataset found, i.e. no subtrack found for ' + gwasTnBase
        #print "ALLrows: ", rows
        #print "AllCols: ", 
        #for row in rows:
        #    #print "ROW: ", 
        #    #core.tableLine([row] + [disRes[col][row].getGlobalResult().get('Result') if (disRes[col][row].getGlobalResult() is not None) else "MISSING" for col in disRes.keys()])
        #    core.tableLine([row] + [disRes[col][row].get('Result') if (disRes[col][row] is not None) else "MISSING" for col in disRes.keys()])
        #core.tableFooter()
        #core.end()
        #print core

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        return None
        
    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True
    #
    #@staticmethod
    #def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    #@staticmethod
    #def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    #@classmethod
    #def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod    
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'



