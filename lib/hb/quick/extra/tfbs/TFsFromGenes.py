import os
from urllib import quote

from config.Config import HB_SOURCE_CODE_BASE_DIR, URL_PREFIX
from gold.util.CommonFunctions import getOrigFn
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.extra.tfbs.TfInfo import TfInfo
from quick.util.CommonFunctions import extractIdFromGalaxyFn
from quick.util.GenomeInfo import GenomeInfo
import third_party.safeshelve as safeshelve


class TFsFromRegions(object):
    @classmethod
    def _runCategoryPointCount(cls, genome, regSpec, binSpec, trackName1, applyBoundaryFilter=True):
        analysisDef = 'Category point count: Number of elements each category of track1 (with overlaps)'+\
                  '[tf1:=SegmentToStartPointFormatConverter:]'+\
                  '-> FreqByCatStat'    
        print '<div class="debug">'
        res = GalaxyInterface.runManual([trackName1], analysisDef, regSpec, binSpec, genome, \
                                        printResults=False, printHtmlWarningMsgs=False, applyBoundaryFilter=applyBoundaryFilter)
        #userBinSource, fullRunArgs = GalaxyInterface._prepareRun(trackName1, None, analysisDef, regSpec, binSpec, genome)
        #if applyBoundaryFilter:
        #    userBinSource = GERegionBoundaryFilter(userBinSource, GlobalBinSource(genome))
        #res = AnalysisDefJob(analysisDef, trackName1, None, userBinSource, **fullRunArgs).run()        
        print res        
        print '</div>'
        return res

    #@staticmethod
    #def findOverrepresentedTFsInRegions(genome, tfSource, regionsBedFn, upFlankSize, downFlankSize, galaxyFn):
    #    assert False #not finished..
    #    
    #    #galaxyFn = '/usit/insilico/web/lookalike/galaxy_dist-20090924-dev/database/files/003/dataset_3347.dat'
    #    #print 'overriding galaxyFN!: ', galaxyFn
    #    galaxyId = extractIdFromGalaxyFn(galaxyFn)
    #    uniqueWebPath = getUniqueWebPath(extractIdFromGalaxyFn(galaxyFn))
    #
    #    assert genome == 'hg18'
    #    
    #    tfTrackNameMappings = TfInfo.getTfTrackNameMappings(genome)
    #    tfTrackName = tfTrackNameMappings[tfSource]
    #    
    #    
    #    #Get gene track
    #    assert geneSource == 'Ensembl'
    #    targetGeneRegsTempFn = uniqueWebPath + os.sep + 'geneRegs.bed'
    #    geneRegsTrackName = GenomeInfo.getStdGeneRegsTn(genome)
    #    geneRegsFn = getOrigFn(genome, geneRegsTrackName, '.category.bed')
    #    #GalaxyInterface.getGeneTrackFromGeneList(genome, geneRegsTrackName, ensembleGeneIdList, targetGeneRegsTempFn )
    #    targetGeneRegsTempFn = regionsBedFn
    #    
    #    assert upFlankSize == downFlankSize == 0 #Should instead extend regions to include flanks
    #    
    #    tcGeneRegsTempFn = uniqueWebPath + os.sep + 'tcGeneRegs.targetcontrol.bedgraph'
    #    #Think this will be okay, subtraction not necessary as targets are put first:
    #    controlGeneRegsTempFn = geneRegsFn
    #    #print targetGeneRegsTempFn, controlGeneRegsTempFn, tcGeneRegsTempFn
    #    GalaxyInterface.combineToTargetControl(targetGeneRegsTempFn, controlGeneRegsTempFn, tcGeneRegsTempFn)
    #    
    #    #tcGeneRegsExternalTN = ['external'] +galaxyId +  [tcGeneRegsTempFn]
    #    tcGeneRegsExternalTN = ExternalTrackManager.createStdTrackName(galaxyId, 'tempTc')
    #    
    #    #tcGeneRegsExternalTN = ['external'] +targetGalaxyId +  [tcGeneRegsTempFn]
    #    #tcGeneRegsExternalTN = ['galaxy', externalId, tcGeneRegsTempFn]
    #    
    #    targetGeneRegsExternalTN = ExternalTrackManager.createStdTrackName(galaxyId, 'tempTc', '1')
    #    controlGeneRegsExternalTN = ExternalTrackManager.createStdTrackName(galaxyId, 'tempTc', '0')
    #    
    #    #pre-process
    #    print 'Pre-processing file: %s, with trackname: %s ' % (tcGeneRegsTempFn, tcGeneRegsExternalTN)
    #    ExternalTrackManager.preProcess(tcGeneRegsTempFn, tcGeneRegsExternalTN, 'targetcontrol.bedgraph',genome)
    #    print 'Pre-processing TN: ', targetGeneRegsExternalTN
    #    ExternalTrackManager.preProcess(targetGeneRegsTempFn, targetGeneRegsExternalTN, 'bed',genome)
    #    print 'Pre-processing TN: ', controlGeneRegsExternalTN
    #    ExternalTrackManager.preProcess(controlGeneRegsTempFn, controlGeneRegsExternalTN, 'bed',genome)
    #    
    #    #print tcGeneRegsExternalTN
    #    trackName1, trackName2 = tfTrackName, tcGeneRegsExternalTN
    #    
    #    analysisDef = 'Categories differentially located in targets?: Which categories of track1-points fall more inside case than control track2-segments? [rawStatistic:=PointCountInsideSegsStat:]' +\
    #              '[tf1:=SegmentToStartPointFormatConverter:] [tf2:=TrivialFormatConverter:]' +\
    #              '-> DivergentRowsInCategoryMatrixStat'
    #    regSpec, binSpec = '*','*'
    #    
    #    #print 'skipping preproc!!'
    #    #ExternalTrackManager.preProcess(tcGeneRegsExternalTN[-1], tcGeneRegsExternalTN, 'targetcontrol.bedgraph', genome)
    #    #ExternalTrackManager.preProcess(targetGeneRegsTempFn, targetGeneRegsExternalTN, 'bed', genome)
    #    
    #    userBinSource, fullRunArgs = GalaxyInterface._prepareRun(trackName1, trackName2, analysisDef, regSpec, binSpec, genome)
    #    #userBinSource = GERegionBoundaryFilter(userBinSource, GlobalBinSource(genome))
    #    res = AnalysisDefJob(analysisDef, trackName1, trackName2, userBinSource, **fullRunArgs).run()
    #    GalaxyInterface._viewResults([res], galaxyFn)
    #    #GalaxyInterface.run(tfTrackName, tcGeneRegsExternalTN, analysisDef, regSpec, binSpec, genome, galaxyFn)
    #    #GalaxyInterface.run(':'.join(tfTrackName), ':'.join(tcGeneRegsExternalTN), analysisDef, regSpec, binSpec, genome, galaxyFn)


    @classmethod
    def findTFsOccurringInRegions(cls, genome, tfSource, regionsBedFn, upFlankSize, downFlankSize, galaxyFn):
        uniqueWebPath = GalaxyRunSpecificFile([], galaxyFn).getDiskPath()
        #assert genome == 'hg18' #other genomes not supported. TF id links do not specify genome for pre-selection of analysis
        
        tfTrackNameMappings = TfInfo.getTfTrackNameMappings(genome)
        assert tfTrackNameMappings != {}, 'No TF info for genome: %s' % genome
        
        tfTrackName = tfTrackNameMappings[tfSource]
                
        if (upFlankSize == downFlankSize == 0):
            flankedRegionsFn = regionsBedFn
        else:
            flankedRegionsFn= uniqueWebPath + os.sep + 'flankedRegs.bed'
            GalaxyInterface.expandBedSegments(regionsBedFn, flankedRegionsFn, genome, upFlankSize, downFlankSize)

        regSpec, binSpec = 'bed', flankedRegionsFn
        res = cls._runCategoryPointCount(genome, regSpec, binSpec, tfTrackName)

        tfNames = res.getResDictKeys()
        #print 'RES: ', res.getGlobalResult()[tfNames[0]], type(res.getGlobalResult()[tfNames[0]])
        pwm2tfids = safeshelve.open(os.sep.join([HB_SOURCE_CODE_BASE_DIR,'data','pwm2TFids.shelf']), 'r')
        tf2class = safeshelve.open(os.sep.join([HB_SOURCE_CODE_BASE_DIR,'data','TfId2Class.shelf']), 'r')
        pwmName2id= safeshelve.open(os.sep.join([HB_SOURCE_CODE_BASE_DIR,'data','pwmName2id.shelf']), 'r')
        #print tfNames[0],tfNames[1], ' VS ', pwm2tfids.keys()[0], len(pwm2tfids)
        #tfs = list(reversed(sorted([(res.getGlobalResult()[tf], tf, '%s (%i hits (class %s))'%(tf, res.getGlobalResult()[tf]), '/'.join([tf2class[x] for x in pwm2tfids[tf]]) ) for tf in tfNames]))) #num hits, tfName, tfTextInclHits
        tfs = list(reversed(sorted([(res.getGlobalResult()[tf], tf, '%s (%i hits )'%(tf, res.getGlobalResult()[tf]) + \
                                     (' (class: %s)'%'/'.join(set([str(tf2class.get(x)) for x in pwm2tfids[pwmName2id[tf]] if x in tf2class]))\
                                      if (tf in pwmName2id and pwmName2id[tf] in pwm2tfids and any([x in tf2class for x in pwm2tfids[pwmName2id[tf]]]))\
                                    else '') ) \
                                    for tf in tfNames])) ) #num hits, tfName, tfTextInclHits
        
        tfsPlural = 's' if len(tfs)!=1 else ''
        print '<p>There are %i TF%s targeting your regions of interest, using "%s" as source of TF occurrences.</p>' % (len(tfs), tfsPlural, tfSource)
        
        expansionStr = ' flanked' if not (upFlankSize == downFlankSize == 0) else ''                

        idHtmlFileNamer = GalaxyRunSpecificFile(['allTfIds.html'],galaxyFn)
        idHtmlFileNamer.writeTextToFile('<br>'.join(['<a href=/hbdev/hyper?track1=%s&track2=>%s</a>'%( quote(':'.join(tfTrackName+[tf[1]])), tf[2]) for tf in tfs]))
        print '<p>', idHtmlFileNamer.getLink('Inspect html file'), ' of all TF IDs occurring 1 or more times within your%s regions of interest, with each TF ID linking to analysis with this TF pre-selected.</p>' % (expansionStr)

        idFileNamer = GalaxyRunSpecificFile(['allTfIds.txt'],galaxyFn)
        idFileNamer.writeTextToFile(os.linesep.join([tf[2] for tf in tfs]) + os.linesep)
        print '<p>', idFileNamer.getLink('Inspect text file'), ' listing all TF IDs occurring 1 or more times within your%s regions of interest.</p>' % (expansionStr)
    
        extractedTfbsFileNamer = GalaxyRunSpecificFile(['tfbsInGeneRegions.bed'],galaxyFn)
        GalaxyInterface.extractTrackManyBins(genome, tfTrackName, regSpec, binSpec, True, 'bed', False, False, extractedTfbsFileNamer.getDiskPath(), True)
        print '<p>', extractedTfbsFileNamer.getLoadToHistoryLink('Inspect bed-file'), 'of all TF binding sites occurring within your%s regions of interest.</p>' % (expansionStr)

        for dummy,tf,dummy2 in tfs:            
            extractedTfbsFileNamer = GalaxyRunSpecificFile([tf+'_tfbsInGeneRegions.bed'],galaxyFn)
            GalaxyInterface.extractTrackManyBins(genome, tfTrackName+[tf], regSpec, binSpec, True, 'bed', False, False, extractedTfbsFileNamer.getDiskPath())
            print '<p>', extractedTfbsFileNamer.getLoadToHistoryLink('Binding sites of the TF %s' %tf, 'bed'), 'occurring within your%s regions of interest (bed-file).</p>' % (expansionStr)
                
class TFsFromGenes(TFsFromRegions):
    @staticmethod
    def findOverrepresentedTFsFromGeneSet(genome, tfSource, ensembleGeneIdList,upFlankSize, downFlankSize, geneSource, galaxyFn):
        #galaxyFn = '/usit/insilico/web/lookalike/galaxy_dist-20090924-dev/database/files/003/dataset_3347.dat'
        #print 'overriding galaxyFN!: ', galaxyFn
        galaxyId = extractIdFromGalaxyFn(galaxyFn)
        uniqueWebPath = GalaxyRunSpecificFile([], galaxyFn).getDiskPath()

        assert genome == 'hg18'

        tfTrackNameMappings = TfInfo.getTfTrackNameMappings(genome)
        tfTrackName = tfTrackNameMappings[tfSource]


        #Get gene track
        assert geneSource == 'Ensembl'
        targetGeneRegsTempFn = uniqueWebPath + os.sep + 'geneRegs.bed'
        geneRegsTrackName = GenomeInfo.getStdGeneRegsTn(genome)
        geneRegsFn = getOrigFn(genome, geneRegsTrackName, '.category.bed')
        GalaxyInterface.getGeneTrackFromGeneList(genome, geneRegsTrackName, ensembleGeneIdList, targetGeneRegsTempFn )

        assert upFlankSize == downFlankSize == 0 #Should instead extend regions to include flanks

        tcGeneRegsTempFn = uniqueWebPath + os.sep + 'tcGeneRegs.targetcontrol.bedgraph'
        #Think this will be okay, subtraction not necessary as targets are put first:
        controlGeneRegsTempFn = geneRegsFn
        #print targetGeneRegsTempFn, controlGeneRegsTempFn, tcGeneRegsTempFn
        GalaxyInterface.combineToTargetControl(targetGeneRegsTempFn, controlGeneRegsTempFn, tcGeneRegsTempFn)

        #tcGeneRegsExternalTN = ['external'] +galaxyId +  [tcGeneRegsTempFn]
        tcGeneRegsExternalTN = ExternalTrackManager.createStdTrackName(galaxyId, 'tempTc')

        #tcGeneRegsExternalTN = ['external'] +targetGalaxyId +  [tcGeneRegsTempFn]
        #tcGeneRegsExternalTN = ['galaxy', externalId, tcGeneRegsTempFn]

        targetGeneRegsExternalTN = ExternalTrackManager.createStdTrackName(galaxyId, 'tempTc', '1')
        controlGeneRegsExternalTN = ExternalTrackManager.createStdTrackName(galaxyId, 'tempTc', '0')

        #pre-process
        print 'Pre-processing file: %s, with trackname: %s ' % (tcGeneRegsTempFn, tcGeneRegsExternalTN)
        ExternalTrackManager.preProcess(tcGeneRegsTempFn, tcGeneRegsExternalTN, 'targetcontrol.bedgraph',genome)
        print 'Pre-processing TN: ', targetGeneRegsExternalTN
        ExternalTrackManager.preProcess(targetGeneRegsTempFn, targetGeneRegsExternalTN, 'bed',genome)
        print 'Pre-processing TN: ', controlGeneRegsExternalTN
        ExternalTrackManager.preProcess(controlGeneRegsTempFn, controlGeneRegsExternalTN, 'bed',genome)

        #print tcGeneRegsExternalTN
        trackName1, trackName2 = tfTrackName, tcGeneRegsExternalTN

        analysisDef = 'Categories differentially located in targets?: Which categories of track1-points fall more inside case than control track2-segments? [rawStatistic:=PointCountInsideSegsStat:]' +\
                  '[tf1:=SegmentToStartPointFormatConverter:] [tf2:=TrivialFormatConverter:]' +\
                  '-> DivergentRowsInCategoryMatrixStat'
        regSpec, binSpec = '*','*'

        #print 'skipping preproc!!'
        #ExternalTrackManager.preProcess(tcGeneRegsExternalTN[-1], tcGeneRegsExternalTN, 'targetcontrol.bedgraph', genome)
        #ExternalTrackManager.preProcess(targetGeneRegsTempFn, targetGeneRegsExternalTN, 'bed', genome)

        GalaxyInterface.runManual([trackName1, trackName2], analysisDef, regSpec, binSpec, genome, printResults=True, printHtmlWarningMsgs=False)
        #userBinSource, fullRunArgs = GalaxyInterface._prepareRun(trackName1, trackName2, analysisDef, regSpec, binSpec, genome)
        ##userBinSource = GERegionBoundaryFilter(userBinSource, GlobalBinSource(genome))
        #res = AnalysisDefJob(analysisDef, trackName1, trackName2, userBinSource, **fullRunArgs).run()
        #GalaxyInterface._viewResults([res], galaxyFn)
        #GalaxyInterface.run(tfTrackName, tcGeneRegsExternalTN, analysisDef, regSpec, binSpec, genome, galaxyFn)
        #GalaxyInterface.run(':'.join(tfTrackName), ':'.join(tcGeneRegsExternalTN), analysisDef, regSpec, binSpec, genome, galaxyFn)

    @classmethod
    def findTFsTargetingGenes(cls, genome, tfSource, ensembleGeneIdList,upFlankSize, downFlankSize, geneSource, galaxyFn):
        #galaxyFn = '/usit/insilico/web/lookalike/galaxy_dist-20090924-dev/database/files/003/dataset_3347.dat'
        #print 'overriding galaxyFN!: ', galaxyFn
        uniqueWebPath = GalaxyRunSpecificFile([], galaxyFn).getDiskPath()

        assert genome in ['mm9','hg18','hg19'] #other genomes not supported. TF id links do not specify genome for pre-selection of analysis
        
        #if tfSource == 'UCSC tfbs conserved':
        #    tfTrackName = ['Gene regulation','TFBS','UCSC prediction track']
        #else:
        #    raise
        tfTrackNameMappings = TfInfo.getTfTrackNameMappings(genome)
        tfTrackName = tfTrackNameMappings[tfSource]
                
        #Get gene track
        #targetGeneRegsTempFn = uniqueWebPath + os.sep + 'geneRegs.bed'
        #geneRegsTrackName = GenomeInfo.getStdGeneRegsTn(genome)
        #geneRegsFn = getOrigFn(genome, geneRegsTrackName, '.category.bed')
        #GalaxyInterface.getGeneTrackFromGeneList(genome, geneRegsTrackName, ensembleGeneIdList, targetGeneRegsTempFn )

        if not (upFlankSize == downFlankSize == 0):
            unflankedGeneRegsTempFn = uniqueWebPath + os.sep + '_geneRegs.bed'
            #flankedGeneRegsTempFn  = uniqueWebPath + os.sep + 'flankedGeneRegs.bed'
            flankedGeneRegsTempStaticFile = GalaxyRunSpecificFile(['flankedGeneRegs.bed'], galaxyFn)
            flankedGeneRegsTempFn = flankedGeneRegsTempStaticFile.getDiskPath()
            geneRegsTrackName = GenomeInfo.getStdGeneRegsTn(genome)
            #geneRegsFn = getOrigFn(genome, geneRegsTrackName, '.category.bed')
            GalaxyInterface.getGeneTrackFromGeneList(genome, geneRegsTrackName, ensembleGeneIdList, unflankedGeneRegsTempFn )
            GalaxyInterface.expandBedSegments(unflankedGeneRegsTempFn, flankedGeneRegsTempFn, genome, upFlankSize, downFlankSize, suffix='category.bed')
            #flankedGeneRegsExternalTN = ['external'] +galaxyId +  [flankedGeneRegsTempFn]
            regSpec, binSpec = 'category.bed', flankedGeneRegsTempFn
        else:
            regSpec, binSpec = '__genes__', ','.join(ensembleGeneIdList)

        res = cls._runCategoryPointCount(genome, regSpec, binSpec, tfTrackName)

        #trackName1 = tfTrackName
        #
        #analysisDef = 'Category point count: Number of elements each category of track1 (with overlaps)'+\
        #          '[tf1:=SegmentToStartPointFormatConverter:]'+\
        #          '-> FreqByCatStat'
        ##assert len(ensembleGeneIdList)==1
        ##geneId = ensembleGeneIdList[0]
        #
        #print '<div class="debug">'        
        #userBinSource, fullRunArgs = GalaxyInterface._prepareRun(trackName1, None, analysisDef, regSpec, binSpec, genome)
        #res = AnalysisDefJob(analysisDef, trackName1, None, userBinSource, **fullRunArgs).run()
        #
        #print res        
        ##GalaxyInterface._viewResults([res], galaxyFn)
        #print '</div>'
        tfs = res.getResDictKeys()
        
        genesPlural = 's' if len(ensembleGeneIdList)>1 else ''
        tfsPlural = 's' if len(tfs)!=1 else ''
        print '<p>There are %i TF%s targeting your gene%s of interest (%s), using "%s" as source of TF occurrences.</p>' % (len(tfs), tfsPlural, genesPlural, ','.join(ensembleGeneIdList), tfSource)
        if not (upFlankSize == downFlankSize == 0):            
            print '(using ', flankedGeneRegsTempStaticFile.getLink('these genomic regions'), ' for genes)'
        expansionStr = ' flanked' if not (upFlankSize == downFlankSize == 0) else ''                

        idHtmlFileNamer = GalaxyRunSpecificFile(['allTfIds.html'],galaxyFn)
        idHtmlFileNamer.writeTextToFile('<br>'.join(['<a href=%s/hyper?dbkey=%s&track1=%s&track2=>%s</a>'%(URL_PREFIX, genome, quote(':'.join(tfTrackName+[tf])), tf) for tf in tfs]))
        #idHtmlFileNamer.writeTextToFile('<br>'.join(['<a href=/hbdev/hyper?track1=%s&track2=>%s</a>'%( ':'.join(tfTrackName+[tf]), tf) for tf in tfs]))
        print '<p>', idHtmlFileNamer.getLink('Inspect html file'), ' of all TF IDs occurring 1 or more times within your%s gene region%s of interest, with each TF ID linking to analysis with this TF pre-selected.</p>' % (expansionStr, genesPlural)

        idFileNamer = GalaxyRunSpecificFile(['allTfIds.txt'],galaxyFn)
        idFileNamer.writeTextToFile(os.linesep.join(tfs) + os.linesep)
        print '<p>', idFileNamer.getLink('Inspect text file'), ' listing all TF IDs occurring 1 or more times within your%s gene region%s of interest.</p>' % (expansionStr, genesPlural)
    
        extractedTfbsFileNamer = GalaxyRunSpecificFile(['tfbsInGeneRegions.bed'],galaxyFn)
        GalaxyInterface.extractTrackManyBins(genome, tfTrackName, regSpec, binSpec, True, 'bed', False, False, extractedTfbsFileNamer.getDiskPath())
        print '<p>', extractedTfbsFileNamer.getLink('Inspect bed-file'), 'of all TF binding sites occurring within your%s gene region%s of interest.</p>' % (expansionStr, genesPlural)
        
        #idFile = idFileNamer.getFile()
        #idFile.write(', '.join([str(bin.val) for bin in targetBins if res[bin][resDictKey]>0]) + os.sep)
        #idFile.close()
        
        #print idFileNamer.getLink('Text file'), ' of TF IDs'
        
        #GalaxyInterface.run(tfTrackName, tcGeneRegsExternalTN, analysisDef, regSpec, binSpec, genome, galaxyFn)
        #GalaxyInterface.run(':'.join(tfTrackName), ':'.join(tcGeneRegsExternalTN), analysisDef, regSpec, binSpec, genome, galaxyFn)
