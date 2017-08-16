from quick.webtools.GeneralGuiTool import GeneralGuiTool
from gold.gsuite import GSuiteConstants
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.application.GalaxyInterface import GalaxyInterface
from collections import OrderedDict
from gold.application.HBAPI import GlobalBinSource, PlainTrack
from quick.util.TrackReportCommon import STAT_OVERLAP_COUNT_BPS,\
    STAT_OVERLAP_RATIO, STAT_FACTOR_OBSERVED_VS_EXPECTED, processRawResults, processResult, \
    STAT_COVERAGE_RATIO_VS_REF_TRACK, STAT_COVERAGE_RATIO_VS_QUERY_TRACK,\
    STAT_LIST_INDEX
from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
from quick.statistic.RawOverlapToSelfStat import RawOverlapToSelfStat
from gold.track.Track import Track


class DetermineSuiteTracksCoincidingWithAnotherSuite(GeneralGuiTool, GenomeMixin, UserBinMixin, DebugMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gSuiteFirst', 'gSuiteSecond']

    MERGE_INTRA_OVERLAPS = 'Merge any overlapping points/segments within the same track'
    ALLOW_MULTIPLE_OVERLAP = 'Allow multiple overlapping points/segments within the same track'

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
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Are (points/segments of) certain tracks of one suite coinciding particularly strongly with (all tracks of) another suite?"

    @classmethod
    def getInputBoxNames(cls):
        return [
                   ('Basic user mode', 'isBasic'),
                   ('', 'basicQuestionId'),
                   ('Select target track collection GSuite', 'gSuiteFirst'),
                   ('Select reference track collection GSuite [rows]', 'gSuiteSecond'),
               ] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               cls.getInputBoxNamesForUserBinSelection() + \
               cls.getInputBoxNamesForDebug()

    @staticmethod
    def getOptionsBoxIsBasic():
        return False

    @staticmethod
    def getOptionsBoxBasicQuestionId(prevChoices):
        return '__hidden__', None

    @staticmethod
    def getOptionsBoxGSuiteFirst(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxGSuiteSecond(prevChoices):  # Alternatively: getOptionsBox2()
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        cls._setDebugModeIfSelected(choices)

        targetGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteSecond)

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)



        analysisDef = 'dummy -> RawOverlapStat'
        # analysisDef = 'dummy [withOverlaps=yes] -> RawOverlapAllowSingleTrackOverlapsStat'
        results = OrderedDict()

        for targetTrack in targetGSuite.allTracks():
            targetTrackName = targetTrack.title
            for refTrack in refGSuite.allTracks():
                refTrackName = refTrack.title
                if targetTrack.trackName == refTrack.trackName:
                    # print targetTrack.title
                    # print targetTrack.trackName
                    result = DetermineSuiteTracksCoincidingWithAnotherSuite.handleSameTrack(targetTrack.trackName, regSpec, binSpec,
                                                                      targetGSuite.genome, galaxyFn)
                else:
                    result = GalaxyInterface.runManual([targetTrack.trackName, refTrack.trackName],
                                                       analysisDef, regSpec, binSpec,
                                                       targetGSuite.genome, galaxyFn,
                                                       printRunDescription=False,
                                                       printResults=False, printProgress=False).getGlobalResult()
                if targetTrackName not in results:
                    results[targetTrackName] = OrderedDict()
                results[targetTrackName][refTrackName] = result

        stat = STAT_OVERLAP_COUNT_BPS
        statIndex = STAT_LIST_INDEX[stat]
        title = ''

        processedResults = []
        headerColumn = []
        for targetTrackName in targetGSuite.allTrackTitles():
            resultRowDict = processRawResults(results[targetTrackName])
            resultColumn = []
            headerColumn = []
            for refTrackName, statList in resultRowDict.iteritems():
                resultColumn.append(statList[statIndex])
                headerColumn.append(refTrackName)
            processedResults.append(resultColumn)

        outputTable = {}
        for elN in range(0, len(headerColumn)):
            outputTable[elN] = {}
            outputTable[elN]['id'] = headerColumn[elN]

        transposedProcessedResults = [list(x) for x in zip(*processedResults)]

        # second question sumSecondgSuite
        # first question numSecondgSuite
        # fifth question numSecondgSuitePercentage
        for i in range(0, len(transposedProcessedResults)):
            outputTable[i]['sumSecondgSuite'] = sum(transposedProcessedResults[i])
            if not 'numSecondgSuite' in outputTable[i]:
                outputTable[i]['numSecondgSuite'] = 0
            for j in range(0, len(transposedProcessedResults[i])):
                if transposedProcessedResults[i][j] >= 1:
                    outputTable[i]['numSecondgSuite'] += 1
                else:
                    outputTable[i]['numSecondgSuite'] += 0
            outputTable[i]['numSecondgSuitePercentage'] = float(outputTable[i]['numSecondgSuite']) / float(
                targetGSuite.numTracks()) * 100

        from gold.statistic.CountSegmentStat import CountSegmentStat
        from gold.statistic.CountPointStat import CountPointStat
        from gold.description.TrackInfo import TrackInfo
        from gold.statistic.CountStat import CountStat

        # third question numPairBpSecondgSuite
        # fourth question numFreqBpSecondgSuite
        i = 0
        for refTrack in refGSuite.allTracks():
            formatName = TrackInfo(refTrack.genome, refTrack.trackName).trackFormatName
            analysisDef = CountStat
            analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, refTrack.genome)
            results = doAnalysis(AnalysisSpec(analysisDef), analysisBins, [PlainTrack(refTrack.trackName)])
            resultDict = results.getGlobalResult()
            if len(resultDict) == 0:
                outputTable[i]['numPairBpSecondgSuite'] = None
                outputTable[i]['numFreqBpSecondgSuite'] = None
                outputTable[i]['numFreqUniqueBpSecondgSuite'] = None
            else:
                outputTable[i]['numPairBpSecondgSuite'] = resultDict['Result']

                if outputTable[i]['numPairBpSecondgSuite'] != 0:
                    outputTable[i]['numFreqBpSecondgSuite'] = float(outputTable[i]['sumSecondgSuite']) / float(
                        outputTable[i]['numPairBpSecondgSuite'])
                else:
                    outputTable[i]['numFreqBpSecondgSuite'] = None

                if outputTable[i]['sumSecondgSuite'] != 0:
                    outputTable[i]['numFreqUniqueBpSecondgSuite'] = float(
                        outputTable[i]['numPairBpSecondgSuite']) / float(outputTable[i]['sumSecondgSuite'])
                else:
                    outputTable[i]['numFreqUniqueBpSecondgSuite'] = None

            i += 1




        # sortTable
        outputTableLine = []
        for key, item in outputTable.iteritems():
            line = [
                item['id'],
                item['numSecondgSuite'],
                item['sumSecondgSuite'],
                item['numPairBpSecondgSuite'],
                item['numFreqBpSecondgSuite'],
                item['numFreqUniqueBpSecondgSuite'],
                item['numSecondgSuitePercentage']
            ]
            outputTableLine.append(line)

        import operator
        outputTableLineSort = sorted(outputTableLine, key=operator.itemgetter(1), reverse=True)

        tableHeader = ['Region ID ',
                       'Number of cases with at least one event ',
                       'Total number of events',
                       'Genome coverage (unique bp)',
                       'Number of events per unique bp',
                       'Number of unique bp per event',
                       'Percentage of cases with at least one event']
        htmlCore = HtmlCore()

        htmlCore.begin()

        htmlCore.line("<b>Identification of genomic elements with high event recurrence</b> ")

        htmlCore.header(title)
        htmlCore.divBegin('resultsDiv')
        htmlCore.tableHeader(tableHeader, sortable=True, tableId='resultsTable')

        for line in outputTableLineSort:
            htmlCore.tableLine(line)

        plotRes = []
        plotXAxis = []
        for lineInx in range(1, len(outputTableLineSort[0])):
            plotResPart = []
            plotXAxisPart = []
            for lineInxO in range(0, len(outputTableLineSort)):
                # if outputTableLineSort[lineInxO][lineInx]!=0 and
                # if outputTableLineSort[lineInxO][lineInx]!=None:
                plotResPart.append(outputTableLineSort[lineInxO][lineInx])
                plotXAxisPart.append(outputTableLineSort[lineInxO][0])
            plotRes.append(plotResPart)
            plotXAxis.append(plotXAxisPart)

        htmlCore.tableFooter()
        htmlCore.divEnd()

        htmlCore.divBegin('plot', style='padding-top:20px;margin-top:20px;')

        vg = visualizationGraphs()
        res = vg.drawColumnCharts(
            plotRes,
            titleText=tableHeader[1:],
            categories=plotXAxis,
            height=500,
            xAxisRotation=270,
            xAxisTitle='Ragion ID',
            yAxisTitle='Number of cases with at least one event',
            marginTop=30,
            addTable=True,
            sortableAccordingToTable=True,
            legend=False
        )
        htmlCore.line(res)
        htmlCore.divEnd()

        htmlCore.hideToggle(styleClass='debug')
        htmlCore.end()

        print htmlCore

    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        from quick.toolguide.controller.ToolGuide import ToolGuideController
        from quick.toolguide import ToolGuideConfig

        if not (choices.gSuiteFirst and choices.gSuiteSecond):
            return ToolGuideController.getHtml(cls.toolId, [ToolGuideConfig.GSUITE_INPUT], choices.isBasic)

        errorString = GeneralGuiTool._checkGSuiteFile(choices.gSuiteFirst)
        if errorString:
            return errorString
        errorString = GeneralGuiTool._checkGSuiteFile(choices.gSuiteSecond)
        if errorString:
            return errorString

        gSuiteFirst = getGSuiteFromGalaxyTN(choices.gSuiteFirst)

        errorString = GeneralGuiTool._checkGSuiteRequirements \
            (gSuiteFirst,
             cls.GSUITE_ALLOWED_FILE_FORMATS,
             cls.GSUITE_ALLOWED_LOCATIONS,
             cls.GSUITE_ALLOWED_TRACK_TYPES,
             cls.GSUITE_DISALLOWED_GENOMES)

        if errorString:
            return errorString

        errorString = GeneralGuiTool._checkGSuiteTrackListSize(gSuiteFirst)
        if errorString:
            return errorString

        gSuiteSecond = getGSuiteFromGalaxyTN(choices.gSuiteSecond)

        errorString = GeneralGuiTool._checkGSuiteRequirements \
            (gSuiteSecond,
             cls.GSUITE_ALLOWED_FILE_FORMATS,
             cls.GSUITE_ALLOWED_LOCATIONS,
             cls.GSUITE_ALLOWED_TRACK_TYPES,
             cls.GSUITE_DISALLOWED_GENOMES)

        if errorString:
            return errorString

        errorString = GeneralGuiTool._checkGSuiteTrackListSize(gSuiteSecond)
        if errorString:
            return errorString

        errorString = cls._validateGenome(choices)
        if errorString:
            return errorString

        errorString = cls.validateUserBins(choices)
        if errorString:
            return errorString

    @classmethod
    def getToolDescription(cls):
        core = HtmlCore()

        core.paragraph('''

            <p>The tool provides screening of two track collections (GSuite files) against each other:</p>

            <p>- The target collection should corespond to a collection of cases (e.g. patients), each of which is defined by a set of events (e.g. somatic mutations). Any events sufficiently characterized by genomic locations/regions can be considered.</p>

            <p>- The reference collection should define genomic elements (e.g. genes) for which event recurrence should be calculated. Each genomic element can be composed of multiple subunits (e.g. exons in the case of genes), forming an individual track.</p>

            <p>To run the tool, follow these steps:</p>

            <p>Select the target and reference track collections (GSuite files) from your current history. Select genomic regions to which the analysis should be limited (or keep the default choice of chromosome arms).
            Click "Execute" in order to start the analysis.</p>''')

        core.paragraph('The results are presented in a sortable table and an interactive chart.')

        core.paragraph('''
            <p>Examples:</p>

            <p>- The tool can be used for identification of "cancer driver genes" (i.e. genes most frequently mutated in a patient cohort), with the reference collection serving for accurate description of a custom gene panel or, generally, the regions of any targeted sequencing study. Mutation frequencies are automatically normalized with respect to the total observed gene lengths.</p>

            <p>- Similarly, one could investigate the number of transcription factors (TFs) potentially binding to the intronic regions of genes. In this case, the target collection should map the binding sites of TFs (with one TF per track), while the reference collection should correspond to the intronic genomic regions (with each gene's introns occupying an own track). By default, both the total as well as the normalized counts of TFs (and TF binding sites) per gene would be included in the results.</p>
            ''')

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
                                      disallowedGenomes=cls.GSUITE_DISALLOWED_GENOMES)

        return str(core)

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

    @classmethod
    def handleSameTrack(cls, trackName, regSpec, binSpec, genome, galaxyFn):

        analysisSpec = AnalysisSpec(RawOverlapToSelfStat)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome)

        return doAnalysis(analysisSpec, analysisBins, [Track(trackName)]).getGlobalResult()

    @staticmethod
    def isDebugMode():
        '''
        Specifies whether debug messages are printed.
        '''
        return False

    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True
