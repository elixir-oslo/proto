from collections import OrderedDict
from urllib import quote

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisDefHandler, AnalysisSpec
from gold.description.AnalysisList import REPLACE_TEMPLATES
from gold.gsuite import GSuiteConstants, GSuiteStatUtils
from gold.gsuite.GSuiteConstants import GSUITE_SUFFIX, \
    GSUITE_EXPANDED_WITH_RESULT_COLUMNS_FILENAME
from gold.gsuite.GSuiteStatUtils import runMultipleSingleValStatsOnTracks
from gold.statistic.CountElementStat import CountElementStat
from gold.statistic.CountStat import CountStat
from gold.track.Track import Track
from gold.util import CommonConstants
from gold.util.CommonFunctions import prettyPrintTrackName, \
    strWithNatLangFormatting
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.result.model.GSuitePerTrackResultModel import GSuitePerTrackResultModel
from quick.statistic.GSuiteSimilarityToQueryTrackRankingsWrapperStat import \
    GSuiteSimilarityToQueryTrackRankingsWrapperStat
from quick.statistic.SingleValueOverlapStat import SingleValueOverlapStat
from quick.toolguide import ToolGuideConfig
from quick.toolguide.controller.ToolGuide import ToolGuideController
from quick.webtools.GeneralGuiTool import GeneralGuiTool, HistElement
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GSuiteResultsTableMixin import GSuiteResultsTableMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


# This is a template prototyping GUI that comes together with a corresponding
# web page.
class GSuiteTracksCoincidingWithQueryTrackTool(GeneralGuiTool, UserBinMixin,
                                               GenomeMixin, GSuiteResultsTableMixin,
                                               DebugMixin):
    Q1 = "Rank suite tracks by similarity to query track"
    Q2 = """Calculate p-values per track in suite: Is a track in the suite more similar to
    the query track than expected by chance? (MC)"""
    Q3 = """Calculate p-value of suite: Are the tracks in the suite (as a whole) more similar to
    the query track than expected by chance (MC)?"""

    ALLOW_UNKNOWN_GENOME = False
    ALLOW_GENOME_OVERRIDE = False

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
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.
        """
        return "Which tracks (in a suite) coincide most strongly with a separate single track?"

    @classmethod
    def getInputBoxNames(cls):
        """
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase and start with a non-capital letter (e.g. "firstKey")
        """
        return [('Basic user mode', 'isBasic'),
                ('Select query track from history', 'queryTrack'),
                ('Select reference GSuite', 'gsuite')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               [
                   ('Which analysis question do you want to run?', 'analysisQName'),
                   ('Select track to track similarity/distance measure', 'similarityFunc'),
                   ('Select summary function for track similarity to rest of suite', 'summaryFunc'),
                   ('Reversed (Used with similarity measures that are not symmetric)', 'reversed'),
                   ('Select MCFDR sampling depth', 'mcfdrDepth')] + \
               GSuiteResultsTableMixin.getInputBoxNamesForAttributesSelection() + \
               [('Concatenate the main results as columns to the input GSuite', 'addResults')
                ] + UserBinMixin.getUserBinInputBoxNames() + \
               DebugMixin.getInputBoxNamesForDebug()

    # @staticmethod
    # def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBoxIsBasic():  # Alternatively: getOptionsBox1()
        return False

    @staticmethod
    def getOptionsBoxQueryTrack(prevChoices):
        """
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to other
        methods. These are lists of results, one for each input box (in the
        order specified by getInputBoxOrder()).

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - The contents is the default value shown inside the text area
        - Returns: string

        Raw HTML code:          '__rawstr__', 'HTML code'
        - This is mainly intended for read only usage. Even though more advanced
          hacks are possible, it is discouraged.

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.

        History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        :param prevChoices:
        """
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxGsuite(prevChoices):  # Alternatively: getOptionsBox2()
        """
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        :param prevChoices:
        """
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxAnalysisQName(cls, prevChoices):
        return [cls.Q1, cls.Q2, cls.Q3]

    @staticmethod
    def getOptionsBoxSimilarityFunc(prevChoices):
        if not prevChoices.isBasic:
            return GSuiteStatUtils.PAIRWISE_STAT_LABELS

    @classmethod
    def getOptionsBoxSummaryFunc(cls, prevChoices):
        if not prevChoices.isBasic and prevChoices.analysisQName in [cls.Q3]:
            return GSuiteStatUtils.SUMMARY_FUNCTIONS_LABELS

    @staticmethod
    def getOptionsBoxReversed(prevChoices):
        if not prevChoices.isBasic:
            return False

    @classmethod
    def getOptionsBoxMcfdrDepth(cls, prevChoices):
        if not prevChoices.isBasic and prevChoices.analysisQName in [cls.Q2, cls.Q3]:
            analysisSpec = AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDR$'])
            return analysisSpec.getOptionsAsText().values()[0]

    @classmethod
    def getOptionsBoxResultsExplanation(cls, prevChoices):

        if prevChoices.gsuite and prevChoices.analysisQName in [cls.Q1, cls.Q2]:
            return GSuiteResultsTableMixin.getOptionsBoxResultsExplanation(prevChoices)

    @classmethod
    def getOptionsBoxAdditionalAttributes(cls, prevChoices):
        if prevChoices.gsuite and prevChoices.analysisQName in [cls.Q1, cls.Q2]:
            return GSuiteResultsTableMixin.getOptionsBoxAdditionalAttributes(prevChoices)
            #             gsuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            #             if gsuite.attributes:
            #                 return OrderedDict(zip(gsuite.attributes, [False]*len(gsuite.attributes)))

    @classmethod
    def getOptionsBoxLeadAttribute(cls, prevChoices):
        if prevChoices.gsuite and prevChoices.analysisQName in [cls.Q1, cls.Q2]:
            return GSuiteResultsTableMixin.getOptionsBoxLeadAttribute(prevChoices)
            #             if prevChoices.additionalAttributes and any(prevChoices.additionalAttributes.values()):
            #                 return [GSuiteConstants.TITLE_COL] + [key for key, val in prevChoices.additionalAttributes.iteritems() if val]
            #

    @staticmethod
    def getOptionsBoxAddResults(prevChoices):
        return ['No', 'Yes']

    # @staticmethod
    # def getOptionsBox3(prevChoices):
    #    return ['']

    # @staticmethod
    # def getOptionsBox4(prevChoices):
    #    return ['']

    # @staticmethod
    # def getInfoForOptionsBoxKey(prevChoices):
    #    '''
    #    If not None, defines the string content of an clickable info box beside
    #    the corresponding input box. HTML is allowed.
    #    '''
    #    return None

    # @staticmethod
    # def getDemoSelections():
    #    return ['testChoice1','..']

    @classmethod
    def getExtraHistElements(cls, choices):
        if choices.gsuite and choices.addResults == 'Yes':
            return [HistElement(GSUITE_EXPANDED_WITH_RESULT_COLUMNS_FILENAME, GSUITE_SUFFIX)]

    @staticmethod
    def drawPlot(results, additionalResultsDict, title, columnInd=0):

        dictIt = OrderedDict()
        dictIt[title] = []
        categoriesPart = []

        for key0, it0 in results.iteritems():
            dictIt[title].append(it0)
            categoriesPart.append(key0)

        for elC in categoriesPart:
            if additionalResultsDict[elC]:
                for key1, it1 in additionalResultsDict[elC].iteritems():
                    if key1 not in dictIt:
                        dictIt[key1] = []
                    dictIt[key1].append(it1)

        plotName = dictIt.keys()
        res = [it[1] for it in dictIt.items()]
        categories = []
        for i in range(0, len(res)):
            categories.append(categoriesPart)

        # table1 = generateHistogram('elementCount', ['Track', 'Histogram'], tableData1, plotType='columnChart')

        from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
        vg = visualizationGraphs()
        res = vg.drawColumnCharts(
            res,
            titleText=plotName,
            categories=categories,
            height=500,
            xAxisRotation=270,
            xAxisTitle='Track title',
            yAxisTitle='',
            marginTop=30,
            addTable=True,
            sortableAccordingToTableIndexWithTrackTitle=1 + int(columnInd),
            sortableAccordingToTable=True,
            plotOptions=True,
            legend=False
        )
        return res

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        """
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        :param choices:  Dict holding all current selections
        :param galaxyFn:
        :param username:
        """

        cls._setDebugModeIfSelected(choices)
        genome = choices.genome
        queryTrackNameAsList = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, choices.queryTrack,
                                                                                     printErrors=False,
                                                                                     printProgress=False)
        analysisQuestion = choices.analysisQName
        similarityStatClassName = choices.similarityFunc if choices.similarityFunc else GSuiteStatUtils.T5_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP
        summaryFunc = choices.summaryFunc if choices.summaryFunc else 'average'
        reverse = 'Yes' if choices.reversed else 'No'

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=genome)
        queryTrack = Track(queryTrackNameAsList)
        tracks = [queryTrack] + [Track(x.trackName, trackTitle=x.title) for x in gsuite.allTracks()]
        queryTrackTitle = prettyPrintTrackName(queryTrack.trackName)
        trackTitles = CommonConstants.TRACK_TITLES_SEPARATOR.join(
            [queryTrackTitle] + [quote(x.title, safe='') for x in gsuite.allTracks()])
        additionalResultsDict = OrderedDict()
        additionalAttributesDict = OrderedDict()
        if analysisQuestion in [cls.Q1, cls.Q2]:
            additionalAttributesDict = cls.getSelectedAttributesForEachTrackDict(choices.additionalAttributes, gsuite)
            # additional analysis
            stats = [SingleValueOverlapStat, CountStat,
                     CountElementStat]  # + [CountSegmentsOverlappingWithT2Stat] #takes long time
            additionalResultsDict = runMultipleSingleValStatsOnTracks(gsuite, stats, analysisBins,
                                                                      queryTrack=queryTrack)

        core = HtmlCore()
        if analysisQuestion == cls.Q1:
            analysisSpec = AnalysisSpec(GSuiteSimilarityToQueryTrackRankingsWrapperStat)
            analysisSpec.addParameter('pairwiseStatistic',
                                      GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[similarityStatClassName])
            #             analysisSpec.addParameter('summaryFunc', GSuiteStatUtils.SUMMARY_FUNCTIONS_MAPPER[summaryFunc])
            analysisSpec.addParameter('reverse', reverse)
            analysisSpec.addParameter('trackTitles', trackTitles)
            analysisSpec.addParameter('queryTracksNum', str(1))

            resultsObj = doAnalysis(analysisSpec, analysisBins, tracks)
            results = resultsObj.getGlobalResult()

            gsPerTrackResultsModel = GSuitePerTrackResultModel(results, ['Similarity to query track'],
                                                               additionalResultsDict=additionalResultsDict,
                                                               additionalAttributesDict=additionalAttributesDict)
            if choices.leadAttribute and choices.leadAttribute != GSuiteConstants.TITLE_COL:
                gsPerTrackResults = gsPerTrackResultsModel.generateColumnTitlesAndResultsDict(choices.leadAttribute)
            else:
                gsPerTrackResults = gsPerTrackResultsModel.generateColumnTitlesAndResultsDict()

            core.begin()
            core.divBegin(divId='results-page')
            core.divBegin(divClass='results-section')
            core.header(analysisQuestion)
            topTrackTitle = results.keys()[0]
            core.paragraph('''
                The track "%s" in the GSuite is the one most similar to the query track %s, with a similarity score of %s 
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                as measured by the "%s" track similarity measure.
            ''' % (
                topTrackTitle, queryTrackTitle, strWithNatLangFormatting(results[topTrackTitle]),
                similarityStatClassName))
            #             core.tableFromDictionary(results, columnNames=['Track title', 'Similarity to query track'], sortable=True, tableId='resultsTable')
            core.tableFromDictionary(gsPerTrackResults[1], columnNames=gsPerTrackResults[0], sortable=True,
                                     tableId='resultsTable', addInstruction=True)
            core.divEnd()
            core.divEnd()

            columnInd = 0
            if choices.leadAttribute and choices.leadAttribute != GSuiteConstants.TITLE_COL:
                columnInd = 1

            res = GSuiteTracksCoincidingWithQueryTrackTool.drawPlot(results, additionalResultsDict,
                                                                    'Similarity to query track', columnInd=columnInd)
            core.line(res)

            core.end()
            if choices.addResults == 'Yes':
                GSuiteStatUtils.addResultsToInputGSuite(gsuite, results, ['Similarity_score'],
                                                        cls.extraGalaxyFn[GSUITE_EXPANDED_WITH_RESULT_COLUMNS_FILENAME])
        elif analysisQuestion == cls.Q2:
            mcfdrDepth = choices.mcfdrDepth if choices.mcfdrDepth else \
                AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDR$']).getOptionsAsText().values()[0][0]
            analysisDefString = REPLACE_TEMPLATES[
                                    '$MCFDR$'] + ' -> GSuiteSimilarityToQueryTrackRankingsAndPValuesWrapperStat'
            analysisSpec = AnalysisDefHandler(analysisDefString)
            analysisSpec.setChoice('MCFDR sampling depth', mcfdrDepth)
            analysisSpec.addParameter('assumptions', 'PermutedSegsAndIntersegsTrack_')
            analysisSpec.addParameter('rawStatistic',
                                      GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[similarityStatClassName])
            analysisSpec.addParameter('pairwiseStatistic', GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[
                similarityStatClassName])  # needed for call of non randomized stat for assertion
            analysisSpec.addParameter('tail', 'more')
            analysisSpec.addParameter('trackTitles', trackTitles)
            analysisSpec.addParameter('queryTracksNum', str(1))
            results = doAnalysis(analysisSpec, analysisBins, tracks).getGlobalResult()

            gsPerTrackResultsModel = GSuitePerTrackResultModel(results, ['Similarity to query track', 'P-value'],
                                                               additionalResultsDict=additionalResultsDict,
                                                               additionalAttributesDict=additionalAttributesDict)
            if choices.leadAttribute and choices.leadAttribute != GSuiteConstants.TITLE_COL:
                gsPerTrackResults = gsPerTrackResultsModel.generateColumnTitlesAndResultsDict(choices.leadAttribute)
            else:
                gsPerTrackResults = gsPerTrackResultsModel.generateColumnTitlesAndResultsDict()

            core = HtmlCore()
            core.begin()
            core.divBegin(divId='results-page')
            core.divBegin(divClass='results-section')
            core.header(analysisQuestion)
            topTrackTitle = results.keys()[0]
            core.paragraph('''
                The track "%s" has the lowest P-value of %s corresponding to %s  similarity to the query track "%s"
                as measured by "%s" track similarity measure.
            ''' % (topTrackTitle, strWithNatLangFormatting(results[topTrackTitle][1]),
                   strWithNatLangFormatting(results[topTrackTitle][0]), queryTrackTitle, similarityStatClassName))
            #             core.tableFromDictionary(results, columnNames=['Track title', 'Similarity to query track', 'P-value'], sortable=False)
            core.tableFromDictionary(gsPerTrackResults[1], columnNames=gsPerTrackResults[0], sortable=True,
                                     tableId='resultsTable')
            core.divEnd()
            core.divEnd()
            core.end()
            if choices.addResults == 'Yes':
                GSuiteStatUtils.addResultsToInputGSuite(gsuite, results, ['Similarity_score', 'P_Value'],
                                                        cls.extraGalaxyFn[GSUITE_EXPANDED_WITH_RESULT_COLUMNS_FILENAME])
        else:
            mcfdrDepth = choices.mcfdrDepth if choices.mcfdrDepth else \
                AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDR$']).getOptionsAsText().values()[0][0]
            analysisDefString = REPLACE_TEMPLATES['$MCFDRv3$'] + ' -> TrackSimilarityToCollectionHypothesisWrapperStat'
            analysisSpec = AnalysisDefHandler(analysisDefString)
            analysisSpec.setChoice('MCFDR sampling depth', mcfdrDepth)
            analysisSpec.addParameter('assumptions', 'PermutedSegsAndIntersegsTrack_')
            analysisSpec.addParameter('rawStatistic', 'SummarizedInteractionWithOtherTracksV2Stat')
            analysisSpec.addParameter('pairwiseStatistic', GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[
                similarityStatClassName])  # needed for call of non randomized stat for assertion
            analysisSpec.addParameter('summaryFunc', GSuiteStatUtils.SUMMARY_FUNCTIONS_MAPPER[summaryFunc])
            analysisSpec.addParameter('tail', 'right-tail')
            results = doAnalysis(analysisSpec, analysisBins, tracks).getGlobalResult()
            pval = results['P-value']
            observed = results['TSMC_SummarizedInteractionWithOtherTracksV2Stat']
            significanceLevel = 'strong' if pval < 0.01 else ('weak' if pval < 0.05 else 'no')
            core = HtmlCore()
            core.begin()
            core.divBegin(divId='results-page')
            core.divBegin(divClass='results-section')
            core.header(analysisQuestion)
            core.paragraph('''
                The query track %s shows %s significance in similarity to the suite of %s 
                and corresponding p-value of %s,
                as measured by "%s" track similarity measure.
            ''' % (
                queryTrackTitle, significanceLevel, strWithNatLangFormatting(observed), strWithNatLangFormatting(pval),
                similarityStatClassName))
            core.divEnd()
            core.divEnd()
            core.end()

        print str(core)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        """
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        :param choices:  Dict holding all current selections
        """
        if not choices.queryTrack and not choices.gsuite:
            return ToolGuideController.getHtml(cls.toolId, [ToolGuideConfig.TRACK_INPUT, ToolGuideConfig.GSUITE_INPUT],
                                               choices.isBasic)
        if not choices.queryTrack:
            return ToolGuideController.getHtml(cls.toolId, [ToolGuideConfig.TRACK_INPUT], choices.isBasic)
        if not choices.gsuite:
            return ToolGuideController.getHtml(cls.toolId, [ToolGuideConfig.GSUITE_INPUT], choices.isBasic)

        errorString = GeneralGuiTool._checkGSuiteFile(choices.gsuite)
        if errorString:
            return errorString

        errorString = cls._validateGenome(choices)
        if errorString:
            return errorString

        errorString = GeneralGuiTool._checkTrack(choices, 'queryTrack', 'genome')
        if errorString:
            return errorString

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)

        errorString = GeneralGuiTool._checkGSuiteRequirements \
            (gsuite,
             cls.GSUITE_ALLOWED_FILE_FORMATS,
             cls.GSUITE_ALLOWED_LOCATIONS,
             cls.GSUITE_ALLOWED_TRACK_TYPES,
             cls.GSUITE_DISALLOWED_GENOMES)

        if errorString:
            return errorString

        errorString = GeneralGuiTool._checkGSuiteTrackListSize(gsuite)
        if errorString:
            return errorString

        errorString = cls.validateUserBins(choices)
        if errorString:
            return errorString

    @staticmethod
    def _getGenome(choices):
        return choices.genome

    @staticmethod
    def _getTrackName1(choices):
        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        return gsuite.allTracks().next().trackName

    @staticmethod
    def _getTrackName2(choices):
        return None

    # @staticmethod
    # def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    @staticmethod
    def isPublic():
        """
       Specifies whether the tool is accessible to all users. If False, the
       tool is only accessible to a restricted set of users as defined in
       LocalOSConfig.py.
       """
        return True

    #
    # @staticmethod
    # def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    # @staticmethod
    # def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    # @staticmethod
    # def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    # @staticmethod
    # def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    # @staticmethod
    # def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by AutoConfig.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    # @staticmethod
    # def getFullExampleURL():
    #    return None
    #
    # @classmethod
    # def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    @staticmethod
    def isDebugMode():
        """
        Specifies whether debug messages are printed.
        """
        return True

    @staticmethod
    def getOutputFormat(choices):
        """
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        :param choices:  Dict holding all current selections
        """
        return 'customhtml'