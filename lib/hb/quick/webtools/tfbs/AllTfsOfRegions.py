from collections import defaultdict, OrderedDict

from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.application.ProcTrackOptions import ProcTrackOptions
from gold.description.AnalysisDefHandler import AnalysisDefHandler
from quick.extra.TrackIntersection import TrackIntersection
from quick.extra.tfbs.TfbsTrackNameMappings import TfbsTrackNameMappings, TfbsGSuiteNameMappings
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.extra.tfbs.TfTrackNameMappings import TfTrackNameMappings
from quick.extra.tfbs.getTrackRelevantInfo import getTrackRelevantInfo
from quick.multitrack.MultiTrackCommon import getGSuiteFromGSuiteFile, getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin

#from docs.manual.InstantRunningForTesting import trackTitles
from gold.util import CommonConstants
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs, plotFunction
from gold.gsuite import GSuiteConstants
from quick.gsuite import GSuiteStatUtils
from gold.description.AnalysisList import REPLACE_TEMPLATES
from gold.application.HBAPI import doAnalysis
from gold.track.Track import Track

'''
Created on Nov 12, 2014
@author: Antonio Mora
Last update: Antonio Mora; Jun 03, 2016
'''

class AllTfsOfRegions(GeneralGuiTool, UserBinMixin, DebugMixin):
    REGIONS_FROM_HISTORY = 'History (user-defined)'
    SELECT = '--- Select ---'
    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]
    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    @staticmethod
    def getToolName():
        return 'Scan transcription factors of a genomic region'

    @classmethod
    def getInputBoxNames(cls):
        return [('', 'basicQuestionId'),
                ('Genome', 'genome'),\
                ('Genomic Regions Source', 'genomicRegions'),\
                ('Genomic Regions Tracks', 'genomicRegionsTracks'),\
                ('TF Source', 'sourceTfs'),\
                ('TF Source Details', 'sourceTfsDetails'),\
                ('TF Tracks', 'tfTracks')\
                ] + cls.getInputBoxNamesForUserBinSelection() + DebugMixin.getInputBoxNamesForDebug()

    @classmethod
    def getOptionsBoxBasicQuestionId(cls):
        return '__hidden__', None

    @classmethod
    def getOptionsBoxGenome(cls, prevChoices):
        return [cls.SELECT, 'hg19', 'mm9']

    @staticmethod
    def getInfoForOptionsBoxGenome():
        return 'Before starting, please select a genome. The only two currently available genome versions are: "Homo sapiens hg19" and \
        "Mus musculus mm9".'

    @classmethod
    def getOptionsBoxGenomicRegions(cls, prevChoices):
        if prevChoices.genome != cls.SELECT:
            return [cls.SELECT] + ['Hyperbrowser repository'] + ['Hyperbrowser repository (cell-type-specific)'] + \
        [cls.REGIONS_FROM_HISTORY] # ['Input Genomic Region']

    @classmethod
    def getOptionsBoxGenomicRegionsTracks(cls, prevChoices):
        if prevChoices.genome != cls.SELECT:
            if prevChoices.genomicRegions == cls.REGIONS_FROM_HISTORY:
                return GeneralGuiTool.getHistorySelectionElement('bed', 'gsuite')
                #return ('__history__','bed','category.bed','gtrack', 'gsuite')
            #elif prevChoices.genomicRegions == 'Input Genomic Region':
            #    return #('', 1, False) # Function to extract this region from a track and send it to history? Or do it before using this function?
            elif prevChoices.genomicRegions == cls.SELECT:
                return
            elif prevChoices.genomicRegions == 'Hyperbrowser repository':
                return [cls.SELECT] + TfbsTrackNameMappings.getTfbsTrackNameMappings(prevChoices.genome).keys()
            else:
                selectedTrackNames = []
                genElementGSuiteName = TfbsGSuiteNameMappings.getTfbsGSuiteNameMappings(prevChoices.genome).values()
                for gSuite in genElementGSuiteName:
                    thisGSuite = getGSuiteFromGSuiteFile(gSuite)
                    for track in thisGSuite.allTracks():
                        selectedTrackNames.append(':'.join(track.trackName[2:]))
                return [cls.SELECT] + selectedTrackNames

    @staticmethod
    def getInfoForOptionsBoxGenomicRegionsTracks(prevChoices):
        if prevChoices.genome == 'hg19':
            return 'This tool will allow you to determine overlap between one genomic region track and one or more transcription factor tracks (binding\
            and co-binding of multiple TFs into certain regions).<p>In this step,\
            you can choose between three sources of genomic region tracks: The single tracks stored in the hyperbrowser repository, the cell-line\
            specific multi-tracks (GSuite) stored in the GSuite hyperbrowser repository, or tracks that you have previously uploaded to Galaxy History.<p>\
            The single tracks in the hyperbrowser repository include:<ul>\
            <li><a href="http://www.ensembl.org/Homo_sapiens/Info/Index">Ensemble Genes, Exons and Introns</a></li>\
            <li><a href="http://www.ncbi.nlm.nih.gov/refseq/rsg/">RefSeq Genes, Exons and Introns</a></li>\
            <li><a href="http://genome.ucsc.edu/cgi-bin/hgTables?hgta_doSchemaDb=hg19&hgta_doSchemaTable=switchDbTss">SwitchGear TSS Database</a></li>\
            <li><a href="http://enhancer.lbl.gov/cgi-bin/imagedb3.pl?form=search&show=1&search.form=no&search.result=yes">Vista Enhancers Database</a></li>\
            <li><a href="http://enhancer.binf.ku.dk/presets/">FANTOM5/Transcribed-Enhancer-Atlas Robust Enhancers</a></li>\
            <li><a href="http://enhancer.binf.ku.dk/presets/">FANTOM5/Transcribed-Enhancer-Atlas Ubiquitous Enhancers -cell-based</a></li>\
            <li><a href="http://enhancer.binf.ku.dk/presets/">FANTOM5/Transcribed-Enhancer-Atlas Ubiquitous Enhancers -anatomy-based</a></li>\
            </ul><p>The multi-tracks in the GSuite hyperbrowser repository include:<ul>\
            <li><a href="http://genome.ucsc.edu/cgi-bin/hgTrackUi?g=wgEncodeHistoneSuper">Enhancer-associated histone marks per cell type (H3K4me1, H3K27ac, and H3K36me3, for GM12878, H1HESC, HeLaS3, HepG2, HUVEC, K562, and NHEK cells)</a></li>\
            <li><a href="http://enhancer.binf.ku.dk/presets/">Enhancer per tissue/organ (FANTOM5 enhancers for 41 different tissues/organs)</a></li>\
            <li><a href="http://enhancer.binf.ku.dk/presets/">Enhancer per cell type (FANTOM5 enhancers for 71 different cell types)</a></li>\
            <li><a href="http://genome.ucsc.edu/cgi-bin/hgTrackUi?g=wgEncodeDNAseSuper">Open chromatin per cell type (ENCODE synthesis data for Gliobla, GM12878, GM12892, H1HESC, HeLaS3, HepG2, HUVEC, K562, Medullo, and NHEK cells)</a></li>\
            <li><a href="http://genome.ucsc.edu/cgi-bin/hgTrackUi?g=wgEncodeAwgSegmentation">Segmentation per cell type (Segway predictions for GM12878, H1HESC, HeLaS3, HepG2, HUVEC, and K562 cells, plus ChromHMM predictions for K562 cells)</a></li>\
            </ul><p>'
        elif prevChoices.genome == 'mm9':
            return 'This tool will allow you to determine overlap between one genomic region track and one or more transcription factor tracks (binding\
            and co-binding of multiple TFs into certain regions).<p>In this step,\
            you can choose between three sources of genomic region tracks: The single tracks stored in the hyperbrowser repository, the cell-line\
            specific multi-tracks (GSuite) stored in the GSuite hyperbrowser repository, or tracks that you have previously uploaded to Galaxy History.\
            The single tracks in the hyperbrowser repository include:<ul>\
            <li><a href="http://www.ensembl.org/Mus_musculus/Info/Index">Ensemble Genes</a></li>\
            <li><a href="http://www.ncbi.nlm.nih.gov/refseq/rsg/">RefSeq Genes, Exons, Introns and Intergenic regions</a></li>\
            <li><a href="http://fantom.gsc.riken.jp/5/data/">FANTOM5 Cage Peak Robust</a></li>\
            </ul><p>The multi-tracks in the GSuite hyperbrowser repository include:<ul>\
            <li><a href="http://genome.ucsc.edu/cgi-bin/hgTrackUi?g=wgEncodeHistoneSuper">Enhancer-associated histone marks per cell type (H3K4me1, H3K27ac, and H3K36me3, for ES-E14 and MEL cells)</a></li>\
            <li><a href="http://genome.ucsc.edu/cgi-bin/hgTrackUi?g=wgEncodeDNAseSuper">Open chromatin per cell type (ENCODE synthesis data for ES-E14 and MEL cells)</a></li>\
            </ul><p>'
        else:
            return

    '''@classmethod
    def getOptionsBoxSourceTfs(cls, prevChoices):
        if prevChoices.genomicRegions != '--- Select ---':
            return TfTrackNameMappings.getTfTrackNameMappings(prevChoices.genome).keys()
        else:
            return

    @classmethod
    def getOptionsBoxTfTracks(cls, prevChoices):
        if prevChoices.genomicRegions != '--- Select ---':
            tfSourceTN = TfTrackNameMappings.getTfTrackNameMappings(prevChoices.genome)[ prevChoices.sourceTfs ]
            subtypes = ProcTrackOptions.getSubtypes(prevChoices.genome, tfSourceTN, True)
            falses = ['False']*len(subtypes)
            return OrderedDict(zip(subtypes,falses))'''

    @classmethod
    def getOptionsBoxSourceTfs(cls, prevChoices):
        if prevChoices.genomicRegionsTracks:
            if prevChoices.genomicRegionsTracks != cls.SELECT:
                return [cls.SELECT] + ['Hyperbrowser repository'] + [cls.REGIONS_FROM_HISTORY]
            else:
                return
        else:
            return

    @classmethod
    def getOptionsBoxSourceTfsDetails(cls, prevChoices):
        if prevChoices.sourceTfs != cls.SELECT:
            if prevChoices.sourceTfs == 'Hyperbrowser repository':
                sourceTfKeys = [cls.SELECT] + TfTrackNameMappings.getTfTrackNameMappings(prevChoices.genome).keys()
                return sourceTfKeys
            elif prevChoices.sourceTfs == cls.REGIONS_FROM_HISTORY:
                return ('__history__','bed','category.bed','gtrack','gsuite')
        else:
            return

    @staticmethod
    def getInfoForOptionsBoxSourceTfsDetails(prevChoices):
        if prevChoices.genome == 'hg19':
            return 'This tool will allow you to determine overlap between one genomic region track and one or more transcription factor tracks (binding\
            and co-binding of multiple TFs into certain regions).<p>In this step,\
            you can choose between three sources of transcription factor tracks: The TFBS Conserved Track (<a href="http://genome.ucsc.edu/cgi-bin/hgTables?hgta_doSchemaDb=hg19&hgta_doSchemaTable=tfbsConsSites">see for details</a>),\
            the track with ChIP-seq uniform peaks from ENCODE (<a href="http://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg19&g=wgEncodeAwgTfbsUniform">see for details</a>),\
            or tracks that you have previously uploaded to Galaxy History.'
        elif prevChoices.genome == 'mm9':
            return 'This tool will allow you to determine overlap between one genomic region track and one or more transcription factor tracks (binding\
            and co-binding of multiple TFs into certain regions).<p>In this step,\
            you can choose between two sources of transcription factor tracks: Either Stanford & Yale TFBS ChIP-seq track (<a href=\
            "http://genome.ucsc.edu/cgi-bin/hgTables?db=mm9&hgta_group=regulation&hgta_track=wgEncodeSydhTfbs">see for details</a>), or\
            tracks that you have previously uploaded to Galaxy History.'
        else:
            return

    @classmethod
    def getOptionsBoxTfTracks(cls, prevChoices):
        if prevChoices.sourceTfsDetails != cls.SELECT:
            genome = prevChoices.genome
            sourceTfs = prevChoices.sourceTfs
            sourceTfsDetails = prevChoices.sourceTfsDetails
            if sourceTfs == cls.SELECT:
                return
            elif sourceTfs == 'Hyperbrowser repository':
                tfSourceTN = TfTrackNameMappings.getTfTrackNameMappings(prevChoices.genome)[ sourceTfsDetails ]
                subtypes = ProcTrackOptions.getSubtypes(prevChoices.genome, tfSourceTN, True)
                falses = ['False']*len(subtypes)
                return OrderedDict(zip(subtypes,falses))
            elif sourceTfs == cls.REGIONS_FROM_HISTORY:
                if isinstance(sourceTfsDetails, basestring):
                    galaxyTN = sourceTfsDetails.split(':')
                    if galaxyTN[1] == "gsuite":  #ExternalTrackManager.extractFileSuffixFromGalaxyTN(prevChoices.sourceTfsDetails, allowUnsupportedSuffixes=True) == "gsuite"
                        errorString = GeneralGuiTool._checkGSuiteFile(sourceTfsDetails)
                        if not errorString:
                            gSuite = getGSuiteFromGalaxyTN(sourceTfsDetails)
                            sizeErrorString = GeneralGuiTool._checkGSuiteTrackListSize(gSuite, 1, 1000)
                            if not sizeErrorString:
                                reqErrorString = GeneralGuiTool._checkGSuiteRequirements \
                                    (gSuite,
                                     AllTfsOfRegions.GSUITE_ALLOWED_FILE_FORMATS,
                                     AllTfsOfRegions.GSUITE_ALLOWED_LOCATIONS,
                                     AllTfsOfRegions.GSUITE_ALLOWED_TRACK_TYPES,
                                     AllTfsOfRegions.GSUITE_DISALLOWED_GENOMES)
                                if not reqErrorString:
                                    validity = 'Valid'
                                else:
                                    return
                            else:
                                return
                        else:
                            return
                        if validity == 'Valid':
                            selectedTrackNames = []
                            gSuite = getGSuiteFromGalaxyTN(sourceTfsDetails)
                            for track in gSuite.allTracks():
                                selectedTrackNames.append(':'.join(track.trackName))
                            falses = ['False']*len(selectedTrackNames)
                            return OrderedDict(zip(selectedTrackNames,falses))
                    else:
                        tfTrackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, galaxyTN)
                        return [':'.join(tfTrackName)]
                else:
                    return
            else:
                return
        else:
            return

    @staticmethod
    def countStatistics(similarityFunc, choices, genome, tracks, trackTitles):
        
        trackList = tracks[1:]

        resultsForStatistics=OrderedDict()
        
        llDict=OrderedDict()
        trackT =  trackTitles[1:]
        i=0
        for tt1 in trackT:
            if not tt1 in llDict:
                llDict[tt1] = []
                resultsForStatistics[tt1]={}
                for tt2 in range(i, len(trackT)):
                    llDict[tt1].append(trackT[tt2])
            i+=1
#         
#         print 'llDict=' + str(llDict)
#         print 'trackT=' + str(trackT)
#         print 'trackList=' + str(trackList)
        
        for key0, it0 in llDict.iteritems():
            if len(it0) > 1:
                trackCollection=[]
                for it1 in it0:
                    
                    trackNumber = trackT.index(it1)
                    trackCollection.append(trackList[trackNumber])
                    
                trackTitles = CommonConstants.TRACK_TITLES_SEPARATOR.join(it0)
                
#                 print str(key0) + '- trackCollection: ' + str(trackCollection) + ' trackTitles: ' + str(trackTitles)
                
                for similarityStatClassName in similarityFunc:
                    regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
                    analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=genome)
                        
                    mcfdrDepth = AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDR$']).getOptionsAsText().values()[0][0]
                    analysisDefString = REPLACE_TEMPLATES['$MCFDR$'] + ' -> GSuiteSimilarityToQueryTrackRankingsAndPValuesWrapperStat'
                    analysisSpec = AnalysisDefHandler(analysisDefString)
                    analysisSpec.setChoice('MCFDR sampling depth', mcfdrDepth)
                    analysisSpec.addParameter('assumptions', 'PermutedSegsAndIntersegsTrack_')
                    analysisSpec.addParameter('rawStatistic', GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[similarityStatClassName])
                    analysisSpec.addParameter('pairwiseStatistic', GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[similarityStatClassName]) #needed for call of non randomized stat for assertion
                    analysisSpec.addParameter('tail', 'more')
                    analysisSpec.addParameter('trackTitles', trackTitles)#that need to be string

                    #i added that one later

                    analysisSpec.addParameter('queryTracksNum', str(len(trackCollection)))
                    results = doAnalysis(analysisSpec, analysisBins, trackCollection).getGlobalResult()
                        
                    if not similarityStatClassName in resultsForStatistics[key0]:
                        resultsForStatistics[key0][similarityStatClassName] = {}
                  
                  
                    resultsForStatistics[key0][similarityStatClassName] = results
                    
        return resultsForStatistics

    @staticmethod
    def countStatisticResults(resultDict, tfList, trackTitlesForStat):
        
        
        for key0, it0 in resultDict.iteritems():
            tfTrue = True
            
            if len(it0)!=2:
                for tfE in tfList:
                    if not tfE in resultDict[key0].keys():
                        resultDict[key0][tfE]={}
                
            for key1, it1 in it0.iteritems():
                tfTrue=False
#                 print 'key1' + str(key1) + ' ' + str(it1)
                if len(it1) != len(trackTitlesForStat)-1:
                    for elN in range(1, len(trackTitlesForStat)):
                        nameEl = trackTitlesForStat[elN]
                        if nameEl not in it1.keys():
                            if nameEl == key0:
                                resultDict[key0][key1][nameEl] = [None, None]
                            else:
                                if key1 in resultDict[nameEl]:
                                    if key0 in resultDict[nameEl][key1]:
                                        resultDict[key0][key1][nameEl] = resultDict[nameEl][key1][key0]
                                    else:
                                        resultDict[key0][key1][nameEl] = [None, None]
                                else:
                                    resultDict[key0][key1][nameEl] = [None, None]
        #                             print '----' + str(key0) + ' ' + str(key1) + ' ' + str(nameEl)
            if tfTrue == True:
                for el in tfList:
                    resultDict[key0][el]=OrderedDict
                    for elN in range(1, len(trackTitlesForStat)):
                        nameEl = trackTitlesForStat[elN]
                        if nameEl == key0:
                            resultDict[key0][el][nameEl] = [None, None]
                        else:
                            if el in resultDict[nameEl]:
                                if key0 in resultDict[nameEl][el]:
                                    resultDict[key0][el][nameEl] = resultDict[nameEl][el][key0]
                                else:
                                    resultDict[key0][el][nameEl] = [None, None]
        
        
        
        resultDictlineTablePart=['Data']
        for elN in range(1, len(trackTitlesForStat)):
            resultDictlineTablePart.append(str(trackTitlesForStat[elN]) + ' -- value ')
            resultDictlineTablePart.append(str(trackTitlesForStat[elN]) + ' -- p-value ')

        # print '<br \> result dict'
        # print resultDict
        # print '<br \>'
        # print 'tflist'
        # print tfList
        # print '<br />'
        
        resultDictlineTable={}
        for el in tfList:
            resultDictlineTable[el] = [resultDictlineTablePart]


            # print 'el' + '<br \>'
            # print el
            # print '<br \> resultDictlineTable'
            # print resultDictlineTable
            # print '<br \>'


        for key0, it0 in resultDict.iteritems():
            # print key0
            for key1, it1 in it0.iteritems():
                resultDictlineTablePart=[]
                resultDictlineTablePart.append(key0)
                for elN in range(1, len(trackTitlesForStat)):
                    resultDictlineTablePart.append(it1[trackTitlesForStat[elN]][0])
                    resultDictlineTablePart.append(it1[trackTitlesForStat[elN]][1])

                # print 'key1' +str(key1) + 'AA<br \>'
                if not key1 in resultDictlineTable:
                    print 'no key'
                resultDictlineTable[key1].append(resultDictlineTablePart)
        
        return resultDictlineTable

    @staticmethod
    def isDebugMode():
        '''
        Specifies whether the debug mode is turned on.
        '''
        return False

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        cls._setDebugModeIfSelected(choices)

        genome = choices.genome
        genomicRegions = choices.genomicRegions
        genomicRegionsTracks = choices.genomicRegionsTracks
        sourceTfs = choices.sourceTfs
        sourceTfsDetails = choices.sourceTfsDetails
        tfTracks = choices.tfTracks

        # Get Genomic Region track name:
        if genomicRegions == cls.REGIONS_FROM_HISTORY:
            galaxyTN = genomicRegionsTracks.split(':')
            genElementTrackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, galaxyTN)

            #queryGSuite = getGSuiteFromGalaxyTN(genomicRegionsTracks)
            #queryTrackList = [Track(x.trackName, x.title) for x in queryGSuite.allTracks()]

        elif genomicRegions == 'Hyperbrowser repository':
                selectedGenRegTrack = TfbsTrackNameMappings.getTfbsTrackNameMappings(genome)[ genomicRegionsTracks ]
                if isinstance(selectedGenRegTrack,dict):
                    genElementTrackName = selectedGenRegTrack.values()
                else:
                    genElementTrackName = selectedGenRegTrack
        elif genomicRegions == 'Hyperbrowser repository (cell-type-specific)':
                genElementTrackName = ['Private', 'Antonio'] + genomicRegionsTracks.split(':')
        else:
            return

        # Get TF track names:
        if isinstance(tfTracks,dict):
            selectedTfTracks = [key for key,val in tfTracks.iteritems() if val == 'True']
        else:
            selectedTfTracks = [tfTracks]
            
        
        

        queryTrackTitle = '--'.join(genElementTrackName)
    
        trackTitles = [queryTrackTitle]
        tracks = [Track(genElementTrackName, trackTitle=queryTrackTitle)]
        
        for i in selectedTfTracks:
            if sourceTfs == 'Hyperbrowser repository':
                tfTrackName = TfTrackNameMappings.getTfTrackNameMappings(genome)[ sourceTfsDetails ] + [i]
                tracks.append(Track(tfTrackName, trackTitle=tfTrackName[len(tfTrackName)-1]))
                trackTitles.append(tfTrackName[len(tfTrackName)-1])

            else:
                tfTrackName = i.split(':')

                queryGSuite = getGSuiteFromGalaxyTN(sourceTfsDetails)

                for x in queryGSuite.allTracks():
                    selectedTrackNames = (':'.join(x.trackName))
                    if i == selectedTrackNames:
                        tracks.append(Track(x.trackName, x.title))
                        trackTitles.append(x.trackName[-1])


                # queryGSuite = getGSuiteFromGalaxyTN(sourceTfsDetails)
                # tfTrackName = [x.trackName for x in queryGSuite.allTracks()] + [i]
                # tracks += [Track(x.trackName, x.title) for x in queryGSuite.allTracks()]
                # trackTitles += tfTrackName

        # print tfTrackName
        # print tracks
        # print trackTitles

        trackTitlesForStat= trackTitles 
        
        trackTitles = CommonConstants.TRACK_TITLES_SEPARATOR.join(trackTitles)

        ##first statistic for Q2
        resultsForStatistics=OrderedDict()

        similarityFunc = [#GSuiteStatUtils.T7_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP,
                          GSuiteStatUtils.T5_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP
                          ]

        for similarityStatClassName in similarityFunc:
            regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
            analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=genome)
              
            mcfdrDepth = AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDR$']).getOptionsAsText().values()[0][0]
            analysisDefString = REPLACE_TEMPLATES['$MCFDR$'] + ' -> GSuiteSimilarityToQueryTrackRankingsAndPValuesWrapperStat'
            analysisSpec = AnalysisDefHandler(analysisDefString)
            analysisSpec.setChoice('MCFDR sampling depth', mcfdrDepth)
            analysisSpec.addParameter('assumptions', 'PermutedSegsAndIntersegsTrack_')
            analysisSpec.addParameter('rawStatistic', GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[similarityStatClassName])
            analysisSpec.addParameter('pairwiseStatistic', GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[similarityStatClassName]) #needed for call of non randomized stat for assertion
            analysisSpec.addParameter('tail', 'more')
            analysisSpec.addParameter('trackTitles', trackTitles)#that need to be string
            analysisSpec.addParameter('queryTracksNum', str(len(tracks)))

            results = doAnalysis(analysisSpec, analysisBins, tracks).getGlobalResult()
              
            if not similarityStatClassName in resultsForStatistics:
                resultsForStatistics[similarityStatClassName] = {}
            
            
            resultsForStatistics[similarityStatClassName] = results

        keyTitle = [
            #'Normalized ratio of observed to expected overlap (normalized Forbes similarity measure)',
            'Ratio of observed to expected overlap (Forbes similarity measure)'
        ]

        # 'Normalized Forbes coefficient: ratio of observed to expected overlap normalized in relation to the reference GSuite',
        # 'Forbes coefficient: ratio of observed to expected overlap'

        keyTitle =[
            #GSuiteStatUtils.T7_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP,
            GSuiteStatUtils.T5_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP
        ]

        resultDict = AllTfsOfRegions.countStatistics(similarityFunc, choices, genome, tracks, trackTitlesForStat)

        resultDictShow = AllTfsOfRegions.countStatisticResults(resultDict, keyTitle, trackTitlesForStat)
        

#         print resultsForStatistics


        '''selectedTrackNames = []
        if sourceTfs == 'History (user-defined)':
            if selectedTfTracks.split(":")[1] == "gsuite":
                gSuite = getGSuiteFromGalaxyTN(selectedTfTracks)
                for track in gSuite.allTracks():
                    selectedTrackNames.append(track.trackName)
            else:
                galaxyTN = selectedTfTracks.split(':')
                gRegTrackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, galaxyTN)
                selectedTrackNames.append(gRegTrackName)
        else:'''
        
        
        tfNameList = []
        
        #Intersection between TF Tracks and selected region (Table 1):
        n = 0
        allTargetBins = []; alltfNames = []; table1 = []
        for i in selectedTfTracks:
            n = n+1
            #newGalaxyFn = galaxyFn.split(".")[0] + str(n) + "." + "dat"

            if sourceTfs == 'Hyperbrowser repository':
                tfTrackName = TfTrackNameMappings.getTfTrackNameMappings(genome)[ sourceTfsDetails ] + [i]
            else:
                tfTrackName = i.split(':')
                tfTrackName.pop(0)
            #tfIntersection.expandReferenceTrack(upFlankSize, downFlankSize)
            tfIntersection = TrackIntersection(genome, genElementTrackName, tfTrackName, galaxyFn, str(n))
            
            
            regFileNamer = tfIntersection.getIntersectedRegionsStaticFileWithContent()
            targetBins = tfIntersection.getIntersectedReferenceBins()
            
            #regSpec, targetBins = UserBinSelector.getRegsAndBinsSpec(choices)

            tfHits = [i] * len(targetBins)
            fixedTargetBins = [str(a).split(" ")[0] for a in targetBins]
            extendedTargetBins = [list(a) for a in zip(fixedTargetBins, tfHits)]
            allTargetBins = allTargetBins + extendedTargetBins
            tfName = i
            alltfNames = alltfNames + [tfName]

            # Save output table:
            tfNameList.append(tfName)
            line = [tfName] + [len(targetBins)] + [regFileNamer.getLink('Download bed-file')] + [regFileNamer.getLoadToHistoryLink('Send bed-file to History')]
            table1 = table1 + [line]
        

        # Computing totals:
        fullCase = ','.join(alltfNames)
        firstColumn = [item[0] for item in allTargetBins]
        uniqueAllTargetBins = list(set(firstColumn))
        
        # Group TFs by bound region:
        d1 = defaultdict(list)
        for k, v in allTargetBins:
            d1[k].append(v)
        allTFTargetBins = dict((k, ','.join(v)) for k, v in d1.iteritems())
        
        allTFTargetList = []; fullCaseTFTargetList = []
        for key, value in allTFTargetBins.iteritems():
            allTFTargetList = allTFTargetList + [[key,value]]
            if value == fullCase:
                fullCaseTFTargetList = fullCaseTFTargetList + [[key,value]]
        
        analysis3 = TrackIntersection.getFileFromTargetBins(allTFTargetList, galaxyFn, str(3))
        analysis4 = TrackIntersection.getFileFromTargetBins(fullCaseTFTargetList, galaxyFn, str(4))

        # Print output to table:
        title = 'TF targets and co-occupancy of ' + genElementTrackName[-1] + ' genomic regions'
        htmlCore = HtmlCore()
        
        pf = plotFunction(tableId='resultsTable')
        
        htmlCore.begin()
        htmlCore.header(title)
        htmlCore.divBegin('resultsDiv')
        
        htmlCore.line(pf.createButton(bText = 'Show/Hide more results'))
        
        # htmlCore.tableHeader(['Transcription Factor', 'Normalized ratio of observed to expected overlap (normalized Forbes similarity measure) -- Similarity to genomic regions track', 'Normalized ratio of observed to expected overlap (normalized Forbes similarity measure) -- p-value','Ratio of observed to expected overlap (Forbes similarity measure) -- Similarity to genomic regions track', 'Ratio of observed to expected overlap (Forbes similarity measure) -- p-value', 'Number of TF-Target Track Regions', 'File of TF Target Regions', 'File of TF Target Regions', 'Number of TF-co-occupied Regions', 'File of TF co-occupied Regions', 'File of TF co-occupied Regions', 'Rank of TF co-occupancy motifs', 'Rank of TF co-occupancy motifs'], sortable=True, tableId='resultsTable')

        #previous ordering
        # htmlCore.tableHeader(['Transcription Factor', 'Normalized Forbes index --overlap score',
        #                       'Normalized Forbes index --p-value',
        #                       'Forbes index --overlap score', 'Forbes index --p-value',
        #                       'Number of TF-Target Track Regions', 'File of TF Target Regions',
        #                       'File of TF Target Regions', 'Number of target track regions occupied by this TF',
        #                       'File of TF co-occupied Regions', 'File of TF co-occupied Regions',
        #                       'Rank of TF co-occupancy motifs', 'Rank of TF co-occupancy motifs'],
        #                      sortable=True, tableId='resultsTable')

        htmlCore.tableHeader(['Transcription Factor', 'Number of TF-Target Track Regions', 'File of TF Track Regions',
                             'Number of target track regions occupied by this TF', 'File of TF Target Regions',
                             'Forbes index --overlap score', 'Forbes index --p-value',
                             #'Normalized Forbes index --overlap score', 'Normalized Forbes index --p-value',
                             'File of TF co-occupied Regions', 'Rank of TF co-occupancy motifs'],
                            sortable=True, tableId='resultsTable')

        # Adding co-occupancy results to table:
        n = 1000 
        genRegionNumElements = [int(x) for x in getTrackRelevantInfo.getNumberElements(genome, genElementTrackName)]
        
        
        for key0, it0 in resultsForStatistics.iteritems():
            for el in tfNameList:
                if el not in it0:
                    resultsForStatistics[key0][el]=[None, None]
        
        
        
        resultsPlotDict={}
        resultPlotCat=[]
        resultsPlot=[]
        
        resultsForStatisticsProper={}
        for key0, it0 in resultsForStatistics.iteritems():
            if not key0 in resultsPlotDict:
                resultsPlotDict[key0]={}
            resultsPlotPart=[]
            for key1, it1 in it0.iteritems():
                resultsPlotPart.append(it1[0])
                if not key1 in resultsForStatisticsProper:
                    resultsForStatisticsProper[key1] = []
                if not key1 in resultsPlotDict[key0]:
                    resultsPlotDict[key0][key1]=None
                for el in it1: 
                    resultsForStatisticsProper[key1].append(el)
                resultsPlotDict[key0][key1] = it1[0]

        resultPlotCat.append(tfNameList)
        resultPlotCat.append(tfNameList)
        
        
        
        
        #resultPlotCatPart = tfNameList
        
#         print resultPlotCatPart
        
        for key0, it0 in resultsPlotDict.iteritems():
            resultsPlotPart=[]
            for el in tfNameList:
                if el in it0:
                    resultsPlotPart.append(it0[el])
                else:
                    resultsPlotPart.append(None)
            resultsPlot.append(resultsPlotPart)
        
        
        
        for i in table1:
            thisCaseTFTargetList = []
            for key, value in allTFTargetList:
                if i[0] in value and ',' in value:
                    thisCaseTFTargetList = thisCaseTFTargetList + [[key,value]]
            n = n + 1
            
            thisAnalysis = TrackIntersection.getFileFromTargetBins(thisCaseTFTargetList, galaxyFn, str(n))

            thisCaseCoCountsList = []
            thing = [x[1] for x in thisCaseTFTargetList]
            for k in list(set(thing)):
                thisCount = thing.count(k)
                thisCaseCoCountsList = thisCaseCoCountsList +  \
                                       [[k, thisCount, 100*float(thisCount)/float(sum(genRegionNumElements)), 100*float(thisCount)/float(len(thisCaseTFTargetList))]]
            thisCaseCoCountsList.sort(key=lambda x: x[2], reverse=True)
            n = n + 1
            
            thisCoCountsAnalysis = TrackIntersection.getOccupancySummaryFile(thisCaseCoCountsList, galaxyFn, str(n))
            
            thisLine = [len(thisCaseTFTargetList)] + \
            [thisAnalysis.getLink('Download file')] + [thisAnalysis.getLoadToHistoryLink('Send file to History')] + \
            [thisCoCountsAnalysis.getLink('Download file')] + [thisCoCountsAnalysis.getLoadToHistoryLink('Send file to History')]
            
            newLineI = []
            tfName = i[0] 
            newLineI.append(tfName)
            
            for el in resultsForStatisticsProper[tfName]:
                newLineI.append(el)
            
            for elN in range(1, len(i)):
                newLineI.append(i[elN])
            
            
#             htmlCore.tableLine(i + thisLine)


                # htmlCore.tableHeader(['Transcription Factor', 'Normalized Forbes index --overlap score',
                #                       'Normalized Forbes index --p-value',
                #                       'Forbes index --overlap score', 'Forbes index --p-value',
                #                       'Number of TF-Target Track Regions', 'File of TF Target Regions',
                #                       'File of TF Target Regions', 'Number of target track regions occupied by this TF',
                #                       'File of TF co-occupied Regions', 'File of TF co-occupied Regions',
                #                       'Rank of TF co-occupancy motifs', 'Rank of TF co-occupancy motifs'],
                #                      sortable=True, tableId='resultsTable')

                # htmlCore.tableHeader(['Transcription Factor', 'Number of TF-Target Track Regions', 'File of TF Track Regions',
                #                      'Number of target track regions occupied by this TF', 'File of TF Target Regions',
                #                      'Forbes index --overlap score', 'Forbes index --p-value',
                #                      'Normalized Forbes index --overlap score', 'Normalized Forbes index --p-value',
                #                      'File of TF co-occupied Regions', 'Rank of TF co-occupancy motifs'],
                #                     sortable=True, tableId='resultsTable')


            tl = newLineI + thisLine
            # previous ordering tl - 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
            # actual ordering - 0, 5, 7, 8, 7, 3, 4, 1, 2, 9, 11

            #ordering  = [0, 5, 7, 8, 10, 3, 4, 1, 2, 10, 12]
            ordering = [0, 3, 5, 6, 8, 1, 2, 8, 10]


            #1, 2, => delete


            eoList = []
            for eo in ordering:
                eoList.append(tl[eo])

            htmlCore.tableLine(eoList)
            
        totalCoOccupancyTargetList = []; n = 2000
        for key, value in allTFTargetList:
            n = n + 1
            if ',' in value:
                totalCoOccupancyTargetList = totalCoOccupancyTargetList + [[key,value]]
        #newGalaxyFn = galaxyFn.split(".")[0] + str(n) + "." + "dat"
        totalCoOccupancyAnalysis = TrackIntersection.getFileFromTargetBins(totalCoOccupancyTargetList, galaxyFn, str(n))
        #line = ['Total reported regions'] + [len(allTargetBins)] + [''] + [''] + [''] + [''] + ['']

        #line = ['Full co-occupancy of ' + fullCase] + ['-'] + ['-'] + ['-'] + ['-'] + ['-'] + ['-'] + ['-'] + [len(fullCaseTFTargetList)] + [analysis4.getLink('Download file')] + [analysis4.getLoadToHistoryLink('Send file to History')] + ['-'] + ['-']

        line = ['Full co-occupancy of ' + fullCase] + \
               ['-'] + \
               ['-'] + \
               [len(fullCaseTFTargetList)] + \
               ['-'] + \
               ['-'] + \
               ['-'] + \
               [analysis4.getLoadToHistoryLink('Send file to History')] + \
               ['-']

        htmlCore.tableLine(line)
        #line = ['Total unique regions'] + ['-'] + ['-'] + ['-'] + ['-']  + [len(allTFTargetList)] + [analysis3.getLink('Download bed-file')] + [analysis3.getLoadToHistoryLink('Send bed-file to History')] + [len(totalCoOccupancyTargetList)] + [totalCoOccupancyAnalysis.getLink('Download file')] + [totalCoOccupancyAnalysis.getLoadToHistoryLink('Send file to History')] + ['-'] + ['-']

        line = ['Total unique regions'] + \
               [len(allTFTargetList)] + \
               ['-'] + \
               [len(totalCoOccupancyTargetList)] + \
               [analysis3.getLoadToHistoryLink('Send bed-file to History')] + \
               ['-'] +\
               ['-'] + \
               [totalCoOccupancyAnalysis.getLoadToHistoryLink('Send file to History')] + \
               ['-']


        htmlCore.tableLine(line)

        htmlCore.tableFooter()
        htmlCore.divEnd()
        
        
        
        # htmlCore.line(pf.hideColumns(indexList=[2, 4]))
        #

        sumRes = 0
        for r in resultsPlot[0]:
            if r != None:
                sumRes+=r

        if sumRes !=0:
            vg = visualizationGraphs()
            result = vg.drawColumnCharts(
                                        [resultsPlot[0]],
                                        height=300,
                                        categories=resultPlotCat,
                                        legend=False,
                                        addOptions='width: 90%; float:left; margin: 0 4%;',
                                        #titleText=['Overlap between TFs and genomic region using normalized Forbes', 'Overlap between TFs and genomic region using Forbes'],
                                        titleText=['Overlap between TFs and genomic region using Forbes'],
                                        xAxisRotation=90,
                                        xAxisTitle='TF',
                                        yAxisTitle='value'
                                        )

            htmlCore.line(result)
        
        
        for key0, it0 in resultDictShow.iteritems():
            htmlCore.divBegin('resultsDiv'+str(key0))
            htmlCore.header(key0)
            htmlCore.tableHeader(it0[0], sortable=True, tableId='resultsTable'+str(key0))
            
            for elN in range(1, len(it0)):
                htmlCore.tableLine(it0[elN])
        
            htmlCore.tableFooter()
            htmlCore.divEnd()
        
        
        htmlCore.hideToggle(styleClass='debug')

        htmlCore.end()
        print htmlCore


    @classmethod
    def validateAndReturnErrors(cls, choices):
        genome = choices.genome
        genomicRegions = choices.genomicRegions
        genomicRegionsTracks = choices.genomicRegionsTracks
        sourceTfs = choices.sourceTfs
        sourceTfsDetails = choices.sourceTfsDetails
        tfTracks = choices.tfTracks

        # Check genome
        if genome == cls.SELECT:
            return 'Please select a genome build.'

        # Check that all region boxes have data:
        if genomicRegions == AllTfsOfRegions.SELECT:
            return 'Please select a genomic region.'
        if genomicRegionsTracks == AllTfsOfRegions.SELECT:
            return 'Please select a genomic region track.'

        # Check tracks for Genomic Regions-History:
        if genomicRegions == AllTfsOfRegions.REGIONS_FROM_HISTORY:
            errorString = GeneralGuiTool._checkTrack(choices, 'genomicRegionsTracks', 'genome')
            if errorString:
                return errorString

        # Check that TF box has data:
        if sourceTfs == AllTfsOfRegions.SELECT:
            return 'Please select a TF source.'

        # Check tracks for TFs-History:
        if sourceTfs == AllTfsOfRegions.REGIONS_FROM_HISTORY:
            if sourceTfsDetails == AllTfsOfRegions.SELECT:
                return 'Please select a TF track.'
            else:
                if isinstance(sourceTfsDetails, basestring):
                    trackType = sourceTfsDetails.split(':')[1]
                    if trackType == "gsuite":
                        errorString = GeneralGuiTool._checkGSuiteFile(sourceTfsDetails)
                        if errorString:
                            return errorString
                        gSuite = getGSuiteFromGalaxyTN(sourceTfsDetails)
                        sizeErrorString = GeneralGuiTool._checkGSuiteTrackListSize(gSuite, 1, 1000)
                        if sizeErrorString:
                            return sizeErrorString
                        reqErrorString = GeneralGuiTool._checkGSuiteRequirements \
                            (gSuite,
                             AllTfsOfRegions.GSUITE_ALLOWED_FILE_FORMATS,
                             AllTfsOfRegions.GSUITE_ALLOWED_LOCATIONS,
                             AllTfsOfRegions.GSUITE_ALLOWED_TRACK_TYPES,
                             AllTfsOfRegions.GSUITE_DISALLOWED_GENOMES)

                        if reqErrorString:
                            return reqErrorString
                    else:
                        errorString = GeneralGuiTool._checkTrack(choices, 'sourceTfsDetails', 'genome')
                        if errorString:
                            return errorString

        return None

    @classmethod
    def _getGenome(cls, choices):
        if choices.genome != cls.SELECT:
            return choices.genome

    @staticmethod
    def getOutputFormat(choices=None):
        return 'customhtml'

    @staticmethod
    def getToolIllustration():
        return ['illustrations','tools','TF5.jpg']

    @staticmethod
    def getToolDescription():
        return '<b>Transcription Factor Analysis Workbench, v.1.0</b><p>\
        This tool allows the user to explore all TF binding sites inside a given genomic region (genes, exons,\
        introns, promoters or enhancers) for all chosen TFs (see the following picture).<p>\
        As an input, the tool offers pre-determined tracks of TF binding sites from the Hyperbrowser repository and \
        a certain number of useful genomic tracks to be compared to the TF tracks of interest. If \
        the genomic track you need is not here, you can upload it to Galaxy History using "Get Data",\
        then selecting Genomic Region = History Element in the tool.<p>\
        As an output, this tool will allow you to determine overlap between one genomic region track and one or more\
        transcription factor tracks (identity of all binding TFs, frequency of binding of each TF, and co-binding of\
        multiple TFs, into certain genomic regions).<p>'

    @staticmethod
    def isPublic():
        return True

    @staticmethod
    def getFullExampleURL():
        return 'https://hyperbrowser.uio.no/gsuite/u/hb-superuser/p/tfaw---the-transcription-factor-analysis-workbench'
