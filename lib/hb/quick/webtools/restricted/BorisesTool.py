import itertools
import subprocess
from collections import OrderedDict, defaultdict, Counter

from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisDefHandler, AnalysisSpec
from gold.description.AnalysisList import REPLACE_TEMPLATES
from gold.description.AnalysisManager import AnalysisManager
from gold.description.TrackInfo import TrackInfo
from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import HbGSuiteTrack, GSuiteTrack, GalaxyGSuiteTrack
from gold.track.Track import Track
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.application.UserBinSource import GlobalBinSource
from quick.extra.ProgressViewer import ProgressViewer
from quick.extra.tcell.TCellReceptorSequenceModel import TCellReceptorSequenceModel
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.MultitrackSummarizedInteractionV2Stat import MultitrackSummarizedInteractionV2StatUnsplittable
from quick.statistic.QueryToReferenceCollectionWrapperStat import QueryToReferenceCollectionWrapperStat
from quick.statistic.SummarizedInteractionWithOtherTracksStat import SummarizedInteractionWithOtherTracksStatUnsplittable
from quick.statistic.SummarizedInteractionWithOtherTracksV2Stat import \
    SummarizedInteractionWithOtherTracksV2StatUnsplittable
from quick.trackaccess.TrackGlobalSearchModule import TrackGlobalSearchModule
from quick.util.CommonFunctions import createGalaxyToolURL, ensurePathExists
from quick.util.SequenceProximitityMeasures import levenshteinDistance, \
    alignmentScoreBlosum100Distance, generateProximityMatrix, jaroDistance, jaroWinklerDistance, \
    alignmentScoreBlosum62Distance, centeredAlignmentScoreBlosum100Distance, centeredAlignmentScoreBlosum62Distance, \
    fixedCenteredAlignmentScoreBlosum100Distance, fixedCenteredAlignmentScoreBlosum62Distance, \
    centeredLevenshteinDistance
from quick.util.TrackReportCommon import generatePilotPageOneParagraphs, \
    generatePilotPageTwoParagraphs, generatePilotPageThreeParagraphs, \
    generatePilotPageFiveParagraphs
from quick.util.debug import DebugUtil
from quick.webtools.GeneralGuiTool import MultiGeneralGuiTool, GeneralGuiTool,\
    HistElement


class BorisesTool(MultiGeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Boris's tools"


    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True

    @staticmethod
    def getSubToolClasses():
        return [FastaSequencesAnalysisTool, ChromatinCatalogDownloader, MultiTrackSingleAnalysisTool, UploadGSuiteTool,
                GBTool1, \
                GBTool2, GBTool4, PilotTool1, PilotTool2, PilotTool3, PilotTool5, PilotPageCombinedTool, \
                GBTestTool, CreateKmersTool, FilterOutSeqsFromFasta, \
                ExtractTrackFromRepositoryFromBinsDefinedByGSuiteTool, \
                FindMonomerRepeatsForFastaGSuite, \
                TestHyperGuiTool]


class ChromatinCatalogDownloader(GeneralGuiTool):
    HISTORY_PROGRESS_TITLE = 'Progress'

    '''
        For all possible categories and subcategories in BrowseChromatinCatalog tool
        download, preprocess and store in the HB repository.
    '''

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Download chromatin catalog tracks"

    @staticmethod
    def getInputBoxNames():
        '''
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

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('Select genome', 'genome')]

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
    def getOptionsBoxGenome():  # Alternatively: getOptionsBox1()
        '''
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
        '''
        return '__genome__'

    #     @staticmethod
    #     def getOptionsBoxSecondKey(prevChoices): # Alternatively: getOptionsBox2()
    #         '''
    #         See getOptionsBoxFirstKey().
    #
    #         prevChoices is a namedtuple of selections made by the user in the
    #         previous input boxes (that is, a namedtuple containing only one element
    #         in this case). The elements can accessed either by index, e.g.
    #         prevChoices[0] for the result of input box 1, or by key, e.g.
    #         prevChoices.key (case 2).
    #         '''
    #         return ''

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
    def execute(cls, choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''

        resultRemoteGSuiteList = []
        categoryTitleList = []
        categoryTrackCountList = []
        searchModule = TrackGlobalSearchModule()
        for category in searchModule.getCategories():
            for subCategory in searchModule.getSubCategories(category):
                remoteGSuite = searchModule.getGSuite(category, subCategory, fileTypes=['narrowPeak', 'broadPeak'])
                remoteGSuite.genome = choices.genome
                print remoteGSuite
                if not remoteGSuite.isEmpty():
                    resultRemoteGSuiteList.append(remoteGSuite)
                    nTracks = remoteGSuite.numTracks()
                    categoryTrackCountList.append(nTracks)
                    categoryTitleList.append(category + ':' + subCategory)
        progViewer = ProgressViewer(zip(['Downloading ' + x for x in categoryTitleList], categoryTrackCountList),
                                    cls.extraGalaxyFn[cls.HISTORY_PROGRESS_TITLE])
        for remoteGSuite, categoryTitle in itertools.izip(resultRemoteGSuiteList, categoryTitleList):
            nTracks = remoteGSuite.numTracks()
            #             progViewer.addProgressObject('Downloading to file and uncompressing ' + categoryTitle, nTracks)

            from gold.gsuite.GSuiteDownloader import GSuiteTrackUncompressorAndDownloader
            gSuiteDownloader = GSuiteTrackUncompressorAndDownloader()

            for gsTrack in remoteGSuite.allTracks():
                from gold.util.CommonFunctions import createOrigPath
                from gold.gsuite.GSuiteDownloader import getTitleAndSuffixWithCompressionSuffixesRemoved
                suffix = getTitleAndSuffixWithCompressionSuffixesRemoved(gsTrack)[0]

                fn = createOrigPath(remoteGSuite.genome,
                                    ['Sample data', 'Chromatin catalog'] + categoryTitle.split(':') + [gsTrack.title],
                                    suffix)
                # gsTrack._downloadToFileAndUncompress(fn)
                gSuiteDownloader.visit(gsTrack, fn)

                progViewer.update()

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        if not choices.genome:
            return 'Please select genome'

    @classmethod
    def getExtraHistElements(cls, choices):
        from quick.webtools.GeneralGuiTool import HistElement
        return [HistElement(cls.HISTORY_PROGRESS_TITLE, 'customhtml')]

    # @staticmethod
    # def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    # @staticmethod
    # def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
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
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
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
    # @staticmethod
    # def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    # @staticmethod
    # def getOutputFormat(choices):
    #    '''
    #    The format of the history element with the output of the tool. Note
    #    that html output shows print statements, but that text-based output
    #    (e.g. bed) only shows text written to the galaxyFn file.In the latter
    #    case, all all print statements are redirected to the info field of the
    #    history item box.
    #    '''
    #    return 'html'


class MultiTrackSingleAnalysisTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Run basic analysis on all GSuite tracks"

    @staticmethod
    def getInputBoxNames():
        '''
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

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('Select GSuite file:', 'history'), \
                #                 ('Select analysis category', 'analysisCategory'), \
                #                 ('Select analysis subcategory', 'analysisSubcategory'), \
                ('Select analysis', 'analysis'),
                ('Select parameter', 'paramOne'),
                ('Select output', 'outputType')]

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
    def getOptionsBoxHistory():  # Alternatively: getOptionsBox1()
        '''
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
        '''
        return '__history__', 'gsuite'

    #     @staticmethod
    #     def getOptionsBoxAnalysisCategory(prevChoices): # Alternatively: getOptionsBox2()
    #         '''
    #         See getOptionsBoxFirstKey().
    #
    #         prevChoices is a namedtuple of selections made by the user in the
    #         previous input boxes (that is, a namedtuple containing only one element
    #         in this case). The elements can accessed either by index, e.g.
    #         prevChoices[0] for the result of input box 1, or by key, e.g.
    #         prevChoices.key (case 2).
    #         '''
    #         if prevChoices.history:
    #
    #             return AnalysisManager.getMainCategoryNames()

    #             from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
    #             gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
    #             tracks = list(gSuite.allTracks())
    #             if len(tracks) > 0:
    #                 firstTrack = tracks[0]
    #                 return firstTrack.path, 1, True
    #
    #             from quick.application.GalaxyInterface import GalaxyInterface
    #
    #             return getAnalysisCategories
    #
    #     @staticmethod
    #     def getOptionsBoxAnalysisSubcategory(prevChoices):
    #         if prevChoices.analysisCategory:
    #             return AnalysisManager.getSubCategoryNames(prevChoices.analysisCategory)

    @staticmethod
    def getOptionsBoxAnalysis(prevChoices):

        #         if prevChoices.analysisCategory:
        if prevChoices.history:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
            tracks = list(gSuite.allTracks())
            #         fullCategory = AnalysisManager.combineMainAndSubCategories(prevChoices.analysisCategory, 'Basic')
            fullCategory = AnalysisManager.combineMainAndSubCategories('Descriptive statistics', 'Basic')
            return sorted([AnalysisDefHandler.splitAnalysisText(str(x))[0] for x in
                           AnalysisManager.getValidAnalysesInCategory(fullCategory, gSuite.genome, tracks[0].trackName,
                                                                      None)])

    @staticmethod
    def getOptionsBoxParamOne(prevChoices):
        if prevChoices.analysis:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
            tracks = list(gSuite.allTracks())
            fullCategory = AnalysisManager.combineMainAndSubCategories('Descriptive statistics', 'Basic')
            analysis = MultiTrackSingleAnalysisTool._resolveAnalysisFromName(gSuite.genome, fullCategory,
                                                                             tracks[0].trackName, prevChoices.analysis)
            paramOneName, paramOneValues = analysis.getFirstOptionKeyAndValues()
            if paramOneName and paramOneValues and len(paramOneValues) > 1:
                return paramOneValues

    @staticmethod
    def _resolveAnalysisFromName(genome, fullCategory, trackName, analysisName):
        selectedAnalysis = None
        for analysis in AnalysisManager.getValidAnalysesInCategory(fullCategory, genome, trackName, None):
            if analysisName == AnalysisDefHandler.splitAnalysisText(str(analysis))[0]:
                selectedAnalysis = analysis

        return selectedAnalysis

    @staticmethod
    def getOptionsBoxOutputType(prevChoices):
        return ['gsuite', 'customhtml']

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        gSuite = getGSuiteFromGalaxyTN(choices.history)
        #         fullCategory = AnalysisManager.combineMainAndSubCategories(choices.analysisCategory, 'Basic')
        fullCategory = AnalysisManager.combineMainAndSubCategories('Descriptive statistics', 'Basic')
        tracks = list(gSuite.allTracks())
        analysisName = choices.analysis
        selectedAnalysis = MultiTrackSingleAnalysisTool \
            ._resolveAnalysisFromName(gSuite.genome, fullCategory, tracks[0].trackName, analysisName)

        paramName, paramValues = selectedAnalysis.getFirstOptionKeyAndValues()
        if paramName and paramValues:
            if len(paramValues) == 1:
                selectedAnalysis.addParameter(paramName, paramValues[0])
            else:
                selectedAnalysis.addParameter(paramName, choices.paramOne)

        colNameSet = set()  # for html presentation of results
        for track in tracks:
            # TODO
            # Add user bin source
            result = doAnalysis(selectedAnalysis, GlobalBinSource(gSuite.genome), [track])
            resultDict = result.getGlobalResult()
            if 'Result' in resultDict:
                track.setAttribute(analysisName, str(resultDict['Result']))
                colNameSet.add(analysisName)
            else:
                for attrName, attrVal in resultDict.iteritems():
                    attrNameExtended = analysisName + ':' + attrName
                    track.setAttribute(attrNameExtended, str(attrVal))
                    colNameSet.add(attrNameExtended)
                    #             assert isinstance(resultDict['Result'], (int, basestring, float)), type(resultDict['Result'])
        if choices.outputType == 'gsuite':
            GSuiteComposer.composeToFile(gSuite, galaxyFn)
        else:  # customhtml
            core = HtmlCore()
            core.begin()
            core.header('Results table for' + analysisName)
            colNameList = list(colNameSet)
            core.tableHeader(['Track'] + colNameList, sortable=True)
            for track in gSuite.allTracks():
                colVals = [track.title]
                for colName in colNameList:
                    colVals.append(track.getAttribute(colName))
                core.tableLine(colVals)
            core.tableFooter()
            core.end()
            print core
            #         with open(galaxyFn) as f:
            #             for line in f.readLines():
            #                 print line
            #                 print '<br>'
            # TODO
            # Write GSuite to new history element
            #         return [AnalysisDefHandler.splitAnalysisText(str(x))[0] for x in AnalysisManager.getValidAnalysesInCategory(fullCategory, gSuite.genome, tracks[0].trackName, None)]

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.history)
        if errorStr:
            return errorStr

        gSuite = getGSuiteFromGalaxyTN(choices.history)
        if gSuite.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'

    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True

    @staticmethod
    def getOutputFormat(choices=None):
        return choices.outputType


class UploadGSuiteTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Upload GSuite"

    @staticmethod
    def getInputBoxNames():
        '''
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

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return []

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        print 'This tool redirects to the Upload file tool of Galaxy'

    @staticmethod
    def validateAndReturnErrors(choices):
        # a little trick to redirect to another tool
        core = HtmlCore()
        core.begin(redirectUrl=createGalaxyToolURL('upload1', file_type='gsuite'))
        return core.end()


# class GBTool1(GeneralGuiTool):
#
#     @staticmethod
#     def getToolName():
#         return 'Genome Biology - Stat 1'
#
#     @staticmethod
#     def getInputBoxNames():
#         return [
#                 ('Select GSuite', 'gSuite'),
#                 ('Select statistic', 'stat'),
#                 ('Select MCFDR sampling depth', 'mcfdrDepth'),
#                 ('Select summary function', 'summaryFunc'),
#                 ('Select permutation strategy', 'permutationStrat')
#                 ]
#
#
#     @staticmethod
#     def getOptionsBoxGSuite():
#         return GeneralGuiTool.getHistorySelectionElement('gsuite')
#
#     @staticmethod
#     def getOptionsBoxStat(prevChoices):
#         return [
#                 'PropOfReferenceTrackInsideTargetTrackStat',
#                 'PropOfReferenceTrackInsideUnionStat',
#                 'RatioOfIntersectionToGeometricMeanStat',
#                 'RatioOfOverlapToUnionStat'
#                 ]
#
#     @staticmethod
#     def getOptionsBoxSummaryFunc(prevChoices):
#         return sorted(SummarizedInteractionWithOtherTracksStatUnsplittable.functionDict.keys())
#
#     @staticmethod
#     def getOptionsBoxPermutationStrat(prevChoices):
#         #hardcoded for now to 'PermutedSegsAndIntersegsTrack'
#         return ['PermutedSegsAndSampledIntersegsTrack', 'PermutedSegsAndIntersegsTrack', 'RandomGenomeLocationTrack',
#                 'SegsSampledByIntensityTrack', 'ShuffledMarksTrack', 'SegsSampledByDistanceToReferenceTrack']
#
#
#     @staticmethod
#     def getOptionsBoxMcfdrDepth(prevChoices):
#         analysisSpec = AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDR$'])
#         return analysisSpec.getOptionsAsText().values()[0]
#
#     @staticmethod
#     def execute(choices, galaxyFn=None, username=''):
# #         ([assumptions=PermutedSegsIntersegsTrack_] [rawStatistic=SummarizedInteractionWithOtherTracksStat] [pairwiseStatistic=RatioOfOverlapToUnionStat]) -> RandomizationManagerStat
#         gsuite = getGSuiteFromGalaxyTN(choices.gSuite)
#         tracks = [Track(choices.track.split(':'))] + [Track(x.trackName) for x in gsuite.allTracks()]
#         analysisDefString = REPLACE_TEMPLATES['$MCFDR$'] + ' -> RandomizationManagerStat'
#         analysisSpec = AnalysisDefHandler(analysisDefString)
#         analysisSpec.setChoice('MCFDR sampling depth', choices.mcfdrDepth)
# #         analysisSpec.addParameter('assumptions', 'PermutedSegsAndIntersegsTrack_')
#         analysisSpec.addParameter('rawStatistic', 'SummarizedInteractionWithOtherTracksStat')
#         analysisSpec.addParameter('pairwiseStatistic', choices.stat)
#         analysisSpec.addParameter('summaryFunc', choices.summaryFunc)
#         analysisSpec.addParameter('tail', 'more')
#         analysisSpec.addParameter('randomizationStrategies', '_'.join([choices.permutationStrat for x in range(gsuite.numTracks())]))
#         analysisBins = GlobalBinSource(choices.genome)
#         results = doAnalysis(analysisSpec, analysisBins, tracks)
#         print results
#
#     @staticmethod
#     def validateAndReturnErrors(choices):
#         return None

class GBTool4(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Genome Biology - Stat 4'

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select genome', 'genome'),
            ('Select track', 'track'),
            ('Select GSuite', 'gSuite'),
            ('Select statistic', 'stat'),
            ('Select MCFDR sampling depth', 'mcfdrDepth'),
            ('Select summary function', 'summaryFunc'),
            ('Select permutation strategy', 'permutationStrat')
        ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxTrack(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('bed', 'gtrack')

    @staticmethod
    def getOptionsBoxGSuite(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxStat(prevChoices):
        return [
            'PropOfReferenceTrackInsideTargetTrackStat',
            'PropOfReferenceTrackInsideUnionStat',
            'RatioOfIntersectionToGeometricMeanStat',
            'RatioOfOverlapToUnionStat',
            'ObservedVsExpectedStat'
        ]

    @staticmethod
    def getOptionsBoxSummaryFunc(prevChoices):
        return sorted(SummarizedInteractionWithOtherTracksStatUnsplittable.functionDict.keys())

    @staticmethod
    def getOptionsBoxPermutationStrat(prevChoices):
        # hardcoded for now to 'PermutedSegsAndIntersegsTrack'
        return None

    @staticmethod
    def getOptionsBoxMcfdrDepth(prevChoices):
        analysisSpec = AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDR$'])
        return analysisSpec.getOptionsAsText().values()[0]

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        #         ([assumptions=PermutedSegsIntersegsTrack_] [rawStatistic=SummarizedInteractionWithOtherTracksStat] [pairwiseStatistic=RatioOfOverlapToUnionStat]) -> RandomizationManagerStat


        analysisDefString = REPLACE_TEMPLATES['$MCFDRv3$'] + ' -> TrackSimilarityToCollectionHypothesisWrapperStat'
        analysisSpec = AnalysisDefHandler(analysisDefString)
        analysisSpec.setChoice('MCFDR sampling depth', choices.mcfdrDepth)
        analysisSpec.addParameter('assumptions', 'PermutedSegsAndIntersegsTrack_')
        analysisSpec.addParameter('rawStatistic', 'SummarizedInteractionWithOtherTracksV2Stat')
        analysisSpec.addParameter('pairwiseStatistic', choices.stat)
        analysisSpec.addParameter('summaryFunc', choices.summaryFunc)
        analysisSpec.addParameter('tail', 'right-tail')
        analysisBins = GlobalBinSource(choices.genome)
        gsuite = getGSuiteFromGalaxyTN(choices.gSuite)
        trackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(choices.genome, choices.track,
                                                                          printErrors=False, printProgress=False)
        #         tracks = [Track(choices.track.split(':'))] + [Track(x.trackName) for x in gsuite.allTracks()]
        tracks = [Track(trackName)] + [Track(x.trackName) for x in gsuite.allTracks()]
        results = doAnalysis(analysisSpec, analysisBins, tracks)
        print results

    #         analysisDefString = REPLACE_TEMPLATES['$MCFDR$'] + ' -> RandomizationManagerStat'
    #         analysisSpec = AnalysisDefHandler(analysisDefString)
    #         analysisSpec.setChoice('MCFDR sampling depth', choices.mcfdrDepth)
    #         analysisSpec.addParameter('assumptions', 'PermutedSegsAndIntersegsTrack_')
    #         analysisSpec.addParameter('rawStatistic', 'SummarizedInteractionWithOtherTracksStat')
    #         analysisSpec.addParameter('pairwiseStatistic', choices.stat)
    #         analysisSpec.addParameter('summaryFunc', choices.summaryFunc)
    #         analysisSpec.addParameter('tail', 'more')
    #         analysisBins = GlobalBinSource(choices.genome)
    #         gsuite = getGSuiteFromGalaxyTN(choices.gSuite)
    #         tracks = [Track(choices.track.split(':'))] + [Track(x.trackName) for x in gsuite.allTracks()]
    #         results = doAnalysis(analysisSpec, analysisBins, tracks)
    #         print results

    #         analysisDefString = REPLACE_TEMPLATES['$MCFDRv2$'] + ' -> MultitrackRandomizationManagerStat'
    #         analysisSpec = AnalysisDefHandler(analysisDefString)
    #         analysisSpec.setChoice('MCFDR sampling depth', choices.mcfdrDepth)
    #         analysisSpec.addParameter('assumptions', 'PermutedSegsAndIntersegsTrack_')
    #         analysisSpec.addParameter('rawStatistic', 'SummarizedInteractionWithOtherTracksStat')
    #         analysisSpec.addParameter('pairwiseStatistic', choices.stat)
    #         analysisSpec.addParameter('summaryFunc', choices.summaryFunc)
    #         analysisSpec.addParameter('tail', 'more')
    #         analysisBins = GlobalBinSource(choices.genome)
    #         gsuite = getGSuiteFromGalaxyTN(choices.gSuite)
    #         trackStructure = TrackStructure()
    #         trackStructure[TrackStructure.QUERY_KEY] = [Track(choices.track.split(':'))]
    #         trackStructure[TrackStructure.REF_KEY] = [Track(x.trackName) for x in gsuite.allTracks()]
    #         results = doAnalysisV2(analysisSpec, analysisBins, trackStructure)
    #         print results
    #
    @staticmethod
    def validateAndReturnErrors(choices):
        return None


class GBTool2(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Genome Biology - Stat 2'

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select GSuite', 'gSuite'),
            ('Select statistic', 'stat'),
            ('Select MCFDR sampling depth', 'mcfdrDepth'),
            ('Select summary function for track vs collection interaction', 'summaryFunc'),
            ('Select permutation strategy', 'permutationStrat'),
            ('Select overall summary function', 'multitrackSummaryFunc')
        ]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxStat(prevChoices):
        return [
            'PropOfReferenceTrackInsideTargetTrackStat',
            'PropOfReferenceTrackInsideUnionStat',
            'RatioOfIntersectionToGeometricMeanStat',
            'RatioOfOverlapToUnionStat',
            'ObservedVsExpectedStat'
        ]

    @staticmethod
    def getOptionsBoxSummaryFunc(prevChoices):
        return sorted(SummarizedInteractionWithOtherTracksV2StatUnsplittable.functionDict.keys())

    @staticmethod
    def getOptionsBoxPermutationStrat(prevChoices):
        # hardcoded for now to 'PermutedSegsAndIntersegsTrack'
        return None

    @staticmethod
    def getOptionsBoxMultitrackSummaryFunc(prevChoices):
        return sorted(MultitrackSummarizedInteractionV2StatUnsplittable.functionDict.keys())

    @staticmethod
    def getOptionsBoxMcfdrDepth(prevChoices):
        analysisSpec = AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDR$'])
        return analysisSpec.getOptionsAsText().values()[0]

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        #         ([assumptions=PermutedSegsIntersegsTrack_] [rawStatistic=SummarizedInteractionWithOtherTracksStat] [pairwiseStatistic=RatioOfOverlapToUnionStat]) -> RandomizationManagerStat


        analysisDefString = REPLACE_TEMPLATES['$MCFDRv3$'] + ' -> CollectionSimilarityHypothesisWrapperStat'
        analysisSpec = AnalysisDefHandler(analysisDefString)
        analysisSpec.setChoice('MCFDR sampling depth', choices.mcfdrDepth)
        analysisSpec.addParameter('assumptions', 'PermutedSegsAndIntersegsTrack')
        analysisSpec.addParameter('rawStatistic', 'MultitrackSummarizedInteractionV2Stat')
        analysisSpec.addParameter('pairwiseStatistic', choices.stat)
        analysisSpec.addParameter('summaryFunc', choices.summaryFunc)
        analysisSpec.addParameter('multitrackSummaryFunc', choices.multitrackSummaryFunc)
        analysisSpec.addParameter('tail', 'right-tail')
        gsuite = getGSuiteFromGalaxyTN(choices.gSuite)
        analysisBins = GlobalBinSource(gsuite.genome)
        #         tracks = [Track(choices.track.split(':'))] + [Track(x.trackName) for x in gsuite.allTracks()]
        tracks = [Track(x.trackName) for x in gsuite.allTracks()]
        results = doAnalysis(analysisSpec, analysisBins, tracks)
        print results


# analysisDefString = REPLACE_TEMPLATES['$MCFDR$'] + ' -> RandomizationManagerStat'
#         analysisSpec = AnalysisDefHandler(analysisDefString)
#         analysisSpec.setChoice('MCFDR sampling depth', choices.mcfdrDepth)
#         analysisSpec.addParameter('assumptions', 'PermutedSegsAndIntersegsTrack_')
#         analysisSpec.addParameter('rawStatistic', 'SummarizedInteractionWithOtherTracksStat')
#         analysisSpec.addParameter('pairwiseStatistic', choices.stat)
#         analysisSpec.addParameter('summaryFunc', choices.summaryFunc)
#         analysisSpec.addParameter('tail', 'more')
#         analysisBins = GlobalBinSource(choices.genome)
#         gsuite = getGSuiteFromGalaxyTN(choices.gSuite)
#         tracks = [Track(choices.track.split(':'))] + [Track(x.trackName) for x in gsuite.allTracks()]
#         results = doAnalysis(analysisSpec, analysisBins, tracks)
#         print results

#         analysisDefString = REPLACE_TEMPLATES['$MCFDRv2$'] + ' -> MultitrackRandomizationManagerStat'
#         analysisSpec = AnalysisDefHandler(analysisDefString)
#         analysisSpec.setChoice('MCFDR sampling depth', choices.mcfdrDepth)
#         analysisSpec.addParameter('assumptions', 'PermutedSegsAndIntersegsTrack_')
#         analysisSpec.addParameter('rawStatistic', 'SummarizedInteractionWithOtherTracksStat')
#         analysisSpec.addParameter('pairwiseStatistic', choices.stat)
#         analysisSpec.addParameter('summaryFunc', choices.summaryFunc)
#         analysisSpec.addParameter('tail', 'more')
#         analysisBins = GlobalBinSource(choices.genome)
#         gsuite = getGSuiteFromGalaxyTN(choices.gSuite)
#         trackStructure = TrackStructure()
#         trackStructure[TrackStructure.QUERY_KEY] = [Track(choices.track.split(':'))]
#         trackStructure[TrackStructure.REF_KEY] = [Track(x.trackName) for x in gsuite.allTracks()]
#         results = doAnalysisV2(analysisSpec, analysisBins, trackStructure)
#         print results
#
class GBTool1(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Genome Biology - Stat 1'

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select GSuite', 'gSuite'),
            ('Select statistic', 'stat'),
            ('Select MCFDR sampling depth', 'mcfdrDepth'),
            ('Select summary function for track vs collection interaction', 'summaryFunc'),
            ('Select permutation strategy', 'permutationStrat')
        ]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxStat(prevChoices):
        return [
            'PropOfReferenceTrackInsideTargetTrackStat',
            'PropOfReferenceTrackInsideUnionStat',
            'RatioOfIntersectionToGeometricMeanStat',
            'RatioOfOverlapToUnionStat',
            'ObservedVsExpectedStat'
        ]

    @staticmethod
    def getOptionsBoxSummaryFunc(prevChoices):
        return sorted(SummarizedInteractionWithOtherTracksV2StatUnsplittable.functionDict.keys())

    @staticmethod
    def getOptionsBoxPermutationStrat(prevChoices):
        # hardcoded for now to 'PermutedSegsAndIntersegsTrack'
        return None

    @staticmethod
    def getOptionsBoxMultitrackSummaryFunc(prevChoices):
        return sorted(MultitrackSummarizedInteractionV2StatUnsplittable.functionDict.keys())

    @staticmethod
    def getOptionsBoxMcfdrDepth(prevChoices):
        analysisSpec = AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDR$'])
        return analysisSpec.getOptionsAsText().values()[0]

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        #         ([assumptions=PermutedSegsIntersegsTrack_] [rawStatistic=SummarizedInteractionWithOtherTracksStat] [pairwiseStatistic=RatioOfOverlapToUnionStat]) -> RandomizationManagerStat


        analysisDefString = REPLACE_TEMPLATES['$MCFDRv3$'] + ' -> MostTypicalTrackHypothesisWrapperStat'
        analysisSpec = AnalysisDefHandler(analysisDefString)
        analysisSpec.setChoice('MCFDR sampling depth', choices.mcfdrDepth)
        analysisSpec.addParameter('assumptions', 'PermutedSegsAndIntersegsTrack_')
        analysisSpec.addParameter('rawStatistic', 'MaxSummarizedInteractionV2Stat')
        analysisSpec.addParameter('pairwiseStatistic', choices.stat)
        analysisSpec.addParameter('summaryFunc', choices.summaryFunc)
        analysisSpec.addParameter('tail', 'right-tail')
        gsuite = getGSuiteFromGalaxyTN(choices.gSuite)
        analysisBins = GlobalBinSource(gsuite.genome)
        #         tracks = [Track(choices.track.split(':'))] + [Track(x.trackName) for x in gsuite.allTracks()]
        tracks = [Track(x.trackName) for x in gsuite.allTracks()]
        results = doAnalysis(analysisSpec, analysisBins, tracks)
        print results

    @staticmethod
    def validateAndReturnErrors(choices):
        return None


class PilotTool1(GeneralGuiTool):
    '''
        https://docs.google.com/document/d/1c03750V_xDXfdTYrHOoAZPIjVihtOUpfXlWQm7dO95Q/edit

        TOOL1 - basic overview of tracks in collection:
            The tracks in the collection contain on average X elements (median: Y elements),
            ranging from Z to W between the tracks. The tracks cover on average X Mbps (median: Y Mbps),
            ranging from X to Y Mbps between experiments. This amounts to on average covering X% of the genome, ranging from Y% to Z% between tracks.
            The average coverage (across tracks) is lowest in chrA (B%) and highest in chrC (D%).
            Detailed numbers per track can be inspected in a table of coverage proportion per track per chromosome,
            and in a table of element count per track per chromosome.

            The segments of the tracks are on average X bps long (median: Y bps), ranging from average length of X bps to Y bps between tracks.

            On average, the tracks show a strong local clustering tendency as measured by a Ripleys K  of X at scale 1Kbp and Y at scale 1Mbp
            (on average across tracks). Between tracks, these numbers range from X to Y at scale 1Kbp and from Z to W at scale 1Mbp.

            On average, X% of the tracks fall within exonic regions, ranging from Y% to Z% between tracks.
            This corresponds to an enrichment factor of X, ranging from Y to Z between tracks.
            Further details can be inspected in a table showing distribution of each track between exons, introns and intergenic regions.
    '''

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Pilot page one"

    @staticmethod
    def getInputBoxNames():
        '''
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

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('Select GSuite', 'gSuite')]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        paragraphs = generatePilotPageOneParagraphs(gSuite, galaxyFn, username=username)

        core = HtmlCore()
        core.begin()
        core.header('Basic overview of tracks in collection')
        for prg in paragraphs:
            core.paragraph(prg)
        core.end()

        print core

    @staticmethod
    def validateAndReturnErrors(choices):
        errMessage = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errMessage:
            return errMessage

    @staticmethod
    def getOutputFormat(choices=None):
        return 'customhtml'


class PilotTool2(GeneralGuiTool):
    '''
        https://docs.google.com/document/d/1c03750V_xDXfdTYrHOoAZPIjVihtOUpfXlWQm7dO95Q/edit

        TOOL 2 - Overlap between tracks:
        On average, around 15%  (~1.4Mbps) of the basepairs of a single track are unique to that track
        (not present in any of the other X tracks). Around 11% (1.0Mbps) are shared with at least half (X)
        of the other tracks, while around 0.5% (60Kbps) is shared with all the other tracks.
        Details are available in the form of a plot showing the percentage of an average track shared
        with a varying numbers of other tracks, as well as plots showing the same for an individual track.
        There is also available a plot showing how many base pairs are covered by 1, 2, 3 and up to X of
        the tracks
    '''

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Pilot page two"

    @staticmethod
    def getInputBoxNames():
        '''
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

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('Select GSuite', 'gSuite')]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        paragraphs = generatePilotPageTwoParagraphs(gSuite, galaxyFn)

        core = HtmlCore()
        core.begin()
        core.header('Overlap between tracks')
        for prg in paragraphs:
            core.paragraph(prg)
        core.end()

        print core

    @staticmethod
    def validateAndReturnErrors(choices):
        errMessage = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errMessage:
            return errMessage

    @staticmethod
    def getOutputFormat(choices=None):
        return 'customhtml'


class PilotTool3(GeneralGuiTool):
    '''
        https://docs.google.com/document/d/1c03750V_xDXfdTYrHOoAZPIjVihtOUpfXlWQm7dO95Q/edit

        TOOL 3 - similarity and uniqueness of tracks:
        Out of the **X** tracks, the track **gm12878** is the one that shows the highest degree of
        covering locations covered by the remaining tracks
        (being most like a superset of all other experiments).
        The track **HepG1** is the one covering the least locations unique to this dataset
        (not covered by other tracks). The track **CD4+** is the most typical track,
        i.e. the one showing the strongest preference for locating to positions covered by other tracks
        in the collection.

    '''

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Pilot page three"

    @staticmethod
    def getInputBoxNames():
        '''
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

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('Select GSuite', 'gSuite')]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        paragraphs = generatePilotPageThreeParagraphs(gSuite, galaxyFn)

        core = HtmlCore()
        core.begin()
        core.header('Similarity and uniqueness of tracks')
        for prg in paragraphs:
            core.paragraph(prg)
        core.end()

        print core

    @staticmethod
    def validateAndReturnErrors(choices):
        errMessage = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errMessage:
            return errMessage

    @staticmethod
    def getOutputFormat(choices=None):
        return 'customhtml'


class PilotTool5(GeneralGuiTool):
    '''
        https://docs.google.com/document/d/1c03750V_xDXfdTYrHOoAZPIjVihtOUpfXlWQm7dO95Q/edit

       TOOL 5 - Clustering of elements:
        On average, the tracks show a strong clustering tendency as measured by a Ripleys K  of X at scale 1Kbp and weak clustering tendency
        measured by Y at scale 1Mbp (on average across tracks).
        Between tracks, these numbers range from X to Y at scale 1Kbp and from Z to W at scale 1Mbp.

    '''

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Pilot page five"

    @staticmethod
    def getInputBoxNames():
        '''
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

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('Select GSuite', 'gSuite')]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        paragraphs = generatePilotPageFiveParagraphs(gSuite, galaxyFn)

        core = HtmlCore()
        core.begin()
        core.header('Clustering of track elements')
        for prg in paragraphs:
            core.paragraph(prg)
        core.end()

        print core

    @staticmethod
    def validateAndReturnErrors(choices):
        errMessage = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errMessage:
            return errMessage

    @staticmethod
    def getOutputFormat(choices=None):
        return 'customhtml'


class PilotPageCombinedTool(GeneralGuiTool):
    '''
        https://docs.google.com/document/d/1c03750V_xDXfdTYrHOoAZPIjVihtOUpfXlWQm7dO95Q/edit

        This tool combines all pilot pages into one.
    '''

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Pilot page"

    @staticmethod
    def getInputBoxNames():
        '''
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

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('Select GSuite', 'gSuite')]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        paragraphs = OrderedDict()
        paragraphs['Basic overview of tracks in collection'] = generatePilotPageOneParagraphs(gSuite, galaxyFn,
                                                                                              username=username)
        paragraphs['Overlap between tracks'] = generatePilotPageTwoParagraphs(gSuite, galaxyFn)
        paragraphs['Similarity and uniqueness of tracks'] = generatePilotPageThreeParagraphs(gSuite, galaxyFn)
        paragraphs['Clustering of tracks'] = generatePilotPageFiveParagraphs(gSuite, galaxyFn)

        core = HtmlCore()
        core.begin()
        core.divBegin(divClass='trackbook_main')
        for hdr, prgList in paragraphs.iteritems():
            core.divBegin(divClass='trackbook_section')
            core.header(hdr)
            for prg in prgList:
                core.paragraph(prg)
            core.divEnd()
        core.divEnd()
        core.end()

        print core

    @staticmethod
    def validateAndReturnErrors(choices):
        errMessage = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errMessage:
            return errMessage

    @staticmethod
    def getOutputFormat(choices=None):
        return 'customhtml'


class GBTestTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Test tool'

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select genome', 'genome'),
            ('Select track', 'track'),
            ('Select GSuite', 'gSuite'),
            ('Select statistic', 'stat')
            #                 ('Select MCFDR sampling depth', 'mcfdrDepth'),
            #                 ('Select summary function', 'summaryFunc'),
            #                 ('Select permutation strategy', 'permutationStrat')
        ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxTrack(prevChoices):
        return '__track__'

    @staticmethod
    def getOptionsBoxGSuite(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxStat(prevChoices):
        return [
            'PropOfReferenceTrackInsideTargetTrackStat',
            'PropOfReferenceTrackInsideUnionStat',
            'RatioOfIntersectionToGeometricMeanStat',
            'RatioOfOverlapToUnionStat'
        ]

    #     @staticmethod
    #     def getOptionsBoxSummaryFunc(prevChoices):
    #         return sorted(SummarizedInteractionWithOtherTracksStatUnsplittable.functionDict.keys())
    #
    #     @staticmethod
    #     def getOptionsBoxPermutationStrat(prevChoices):
    #         #hardcoded for now to 'PermutedSegsAndIntersegsTrack'
    #         return None
    #
    #     @staticmethod
    #     def getOptionsBoxMcfdrDepth(prevChoices):
    #         analysisSpec = AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDR$'])
    #         return analysisSpec.getOptionsAsText().values()[0]

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        #         ([assumptions=PermutedSegsIntersegsTrack_] [rawStatistic=SummarizedInteractionWithOtherTracksStat] [pairwiseStatistic=RatioOfOverlapToUnionStat]) -> RandomizationManagerStat
        #         analysisDefString = REPLACE_TEMPLATES['$MCFDR$'] + ' -> RandomizationManagerStat'
        analysisSpec = AnalysisSpec(QueryToReferenceCollectionWrapperStat)
        #         analysisSpec.setChoice('MCFDR sampling depth', choices.mcfdrDepth)
        #         analysisSpec.addParameter('assumptions', 'PermutedSegsAndIntersegsTrack_')
        #         analysisSpec.addParameter('rawStatistic', 'SummarizedInteractionWithOtherTracksStat')
        analysisSpec.addParameter('pairwiseStat', choices.stat)
        #         analysisSpec.addParameter('summaryFunc', choices.summaryFunc)
        #         analysisSpec.addParameter('tail', 'more')
        analysisBins = GlobalBinSource(choices.genome)
        gsuite = getGSuiteFromGalaxyTN(choices.gSuite)
        tracks = [Track(choices.track.split(':'))] + [Track(x.trackName) for x in gsuite.allTracks()]
        doAnalysis(analysisSpec, analysisBins, tracks)

    #         print results

    @staticmethod
    def validateAndReturnErrors(choices):
        return None


class FilterOutSeqsFromFasta(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Get only sequences from fasta file'

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select fasta file from history', 'file')
        ]

    @staticmethod
    def getOptionsBoxFile():
        return GeneralGuiTool.getHistorySelectionElement('fasta')

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        seqs = []
        with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.file), 'r') as f:
            for line in f:
                strpd = line.upper().strip()
                if strpd and strpd[0] in 'ACTG':
                    if strpd not in seqs:
                        seqs.append(strpd)

        for seq in seqs:
            print seq

    @staticmethod
    def validateAndReturnErrors(choices):
        if not choices.file:
            return "Please select a fasta file"


# @staticmethod
#     def getOutputFormat(choices=None):
#         return 'customhtml'

class CreateKmersTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Create k-mer tracks'

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select genome', 'genome'),
            ('Input sequences (one per line)', 'seqs')
        ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxSeqs(prevChoices):
        return ('', 20)

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        seqs = [s.strip() for s in choices.seqs.splitlines()]
        trackNameList = []
        for nmer in seqs:
            GalaxyInterface.createNmerTrack(choices.genome, nmer)
            trackNameList.append(['Sequence', 'K-mers', str(len(nmer)) + '-mers', nmer])
        # example trackName = ['Sequence', 'K-mers', '7-mers', 'agagaga']
        outGSuite = GSuite()
        for trackName in trackNameList:
            trackType = TrackInfo(choices.genome, trackName).trackFormatName.lower()
            hbUri = HbGSuiteTrack.generateURI(trackName=trackName)
            outGSuite.addTrack(GSuiteTrack(hbUri, title=' '.join(['Nmer track'] + trackName[-1:]), trackType=trackType,
                                           genome=choices.genome))

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['Kmers GSuite'])

    @staticmethod
    def validateAndReturnErrors(choices):
        errorStr = GeneralGuiTool._checkGenome(choices.genome)
        if errorStr:
            return errorStr

        if not choices.seqs:
            return 'Please enter at least one sequence'

            #     @staticmethod
            #     def getOutputFormat(choices=None):
            #         return 'gsuite'

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('Kmers GSuite', 'gsuite')]


class ExtractTrackFromRepositoryFromBinsDefinedByGSuiteTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Extract track from repository in regions given by GSuite tracks'

    @classmethod
    def getInputBoxNames(cls):
        return [
                   ('Select gsuite', 'gsuite')] + \
               [('Select genome', 'genome')] + \
               [('Select basis track', 'basisTrack'),
                ('Select extraction format', 'extFormatLbl')]

    @staticmethod
    def getOptionsBoxGsuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxGenome(prevChoices):
        return '__genome__'

    @staticmethod
    def getOptionsBoxBasisTrack(prevChoices):
        if prevChoices.gsuite and prevChoices.genome:
            # return GeneralGuiTool.getHistorySelectionElement()
            return '__track__'

    @staticmethod
    def getOptionsBoxExtFormatLbl(prevChoices):
        if prevChoices.genome and prevChoices.basisTrack:
            extrOpts = GalaxyInterface.getTrackExtractionOptions(
                prevChoices.genome, prevChoices.basisTrack.split(':')
            )
            return [x[0] for x in extrOpts if extrOpts]

    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     if choices.gsuite and choices.basisTrack:
    #         extractionOptions = dict(
    #             GalaxyInterface.getTrackExtractionOptions(choices.genome, choices.basisTrack.split(':')))
    #         extractionFormat = extractionOptions[choices.extFormatLbl] if extractionOptions else None
    #         gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
    #         return [HistElement(gsTrack.title, extractionFormat) for gsTrack in gsuite.allTracks()]

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        basisTrackNameAsList = choices.basisTrack.split(':')
        extractionOptions = dict(GalaxyInterface.getTrackExtractionOptions(choices.genome, basisTrackNameAsList))
        extractionFormat = extractionOptions[choices.extFormatLbl] if extractionOptions else None

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        outGSuite = GSuite()
        for gsTrack in gsuite.allTracks():
            # outputTrackFn = cls.extraGalaxyFn[gsTrack.title]
            # print '<br>\n<br>\n output track filename: ', outputTrackFn
            # print 'path: ', gsTrack.path
            # print 'parsed uri: ', gsTrack._parsedUri
            newTrackFileName = gsTrack.title + '.' + extractionFormat
            outGalaxyFn = ExternalTrackManager.createGalaxyFilesFn(galaxyFn, newTrackFileName)
            ensurePathExists(outGalaxyFn)
            uri = GalaxyGSuiteTrack.generateURI(galaxyFn, extraFileName=newTrackFileName)
            GalaxyInterface.parseExtFormatAndExtractTrackManyBins(choices.genome, basisTrackNameAsList,
                                                                  gsTrack.suffix, gsTrack.path, True,
                                                                  choices.extFormatLbl,
                                                                  outGalaxyFn)

            outGSuite.addTrack(GSuiteTrack(uri, title=gsTrack.title, fileFormat=gsTrack.fileFormat,
                                           trackType=gsTrack.trackType,
                                           genome=choices.genome, attributes=gsTrack.attributes))

        GSuiteComposer.composeToFile(outGSuite, galaxyFn)

        # FIXME: hyper_gui.py at line 362, genome is not set when GenomeMixin is used,
        # FIXME: BaseToolController.py line 74, there is no dbkey parameter.

        # filename = '/software/galaxy/galaxy-dist-hg-gsuite-submit/database/files/000/121/dataset_121468.dat'
        # if output != None:
        #     sys.stdout = open(output, "w", 0)
        # if params.has_key('sepFilePrRegion'):
        #     #args: genome, trackName, regSpec, binSpec, globalCoords, extractionFormat, galaxyFn
        #     # genome= 'mm9'
        #     # trackName = tracks1 = ['Sequence', 'DNA']
        #     # regSpec = region = 'valued.bed' (extracted from binfile parameter)
        #     # binSpec = binSize = '/software/galaxy/galaxy-dist-hg-gsuite-submit/database/files/120/dataset_120638.dat'
        #                           '/software/galaxy/galaxy-dist-hg-gsuite-submit/database/files/120/dataset_120642.dat'
        #     # globalCoords = True
        #     # extractionFormat = overlaps = 'Original file format (suffix: fa)'
        #     # galaxyFn = output = '/software/galaxy/galaxy-dist-hg-gsuite-submit/database/files/000/121/dataset_121416.dat'
        #
        #     # bins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome, trackName)
        #
        #     #uri = GalaxyGSuiteTrack.generateURI(self._galaxyFn, extraFileName=extraFileName)
        #
        #     GalaxyInterface.parseExtFormatAndExtractTrackManyBinsToRegionDirsInZipFile(genome, tracks1, region, binSize, True, overlaps, output)
        # else:
        #     GalaxyInterface.parseExtFormatAndExtractTrackManyBins(genome, tracks1, region, binSize, True, overlaps, output)

    @staticmethod
    def validateAndReturnErrors(choices):
        if not choices.gsuite:
            return "Please select a GSuite from history"
        if not choices.genome:
            return "Please select a genome for the basis track"

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        if choices.genome != gsuite.genome:
            return "The selected genome and the gsuite genome must be equal. Selected = %s; GSuite = %s" % (
                choices.genome, gsuite.genome)

    # @staticmethod
    # def _getGenome(choices):
    #     DebugUtil.insertBreakPoint()
    #     return choices.genome

    @staticmethod
    def getOutputFormat(choices=None):
        return 'gsuite'


class FindMonomerRepeatsForFastaGSuite(GeneralGuiTool):
    TRF_PATH = "/software/VERSIONS/trf-4.0.4/bin/trf404.linux64"

    @staticmethod
    def getToolName():
        return 'Find monomer repeats'

    @classmethod
    def getInputBoxNames(cls):
        return [
            ('Select gsuite', 'gsuite'),
            ('Match', 'match'),
            ('Mismatch', 'mismatch'),
            ('Delta', 'delta'),
            ('Matching probability (Pm)', 'pm'),
            ('Indel probability (Pi)', 'pi'),
            ('Min score', 'minscore'),
            ('Max period', 'maxperiod'),
            ('Min consensus length', 'minconsensus'),
            ('Max consensus length', 'maxconsensus')]

    @staticmethod
    def getOptionsBoxGsuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxMatch(prevChoices):
        return '2'

    @staticmethod
    def getOptionsBoxMismatch(prevChoices):
        return '5'

    @staticmethod
    def getOptionsBoxDelta(prevChoices):
        return '7'

    @staticmethod
    def getOptionsBoxPm(prevChoices):
        return '80'

    @staticmethod
    def getOptionsBoxPi(prevChoices):
        return '10'

    @staticmethod
    def getOptionsBoxMinscore(prevChoices):
        return '50'

    @staticmethod
    def getOptionsBoxMaxperiod(prevChoices):
        return '300'

    @staticmethod
    def getOptionsBoxMinconsensus(prevChoices):
        return '190'

    @staticmethod
    def getOptionsBoxMaxconsensus(prevChoices):
        return '240'

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        import os
        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        match = int(choices.match)
        mismatch = int(choices.mismatch)
        delta = int(choices.delta)
        pm = float(choices.pm)
        pi = float(choices.pi)
        minscore = int(choices.minscore)
        maxperiod = int(choices.maxperiod)
        minConsensusLength = int(choices.minconsensus)
        maxConsensusLength = int(choices.maxconsensus)
        for gsTrack in gsuite.allTracks():
            print '\n\n\n', gsTrack.title
            fastaFilepath = gsTrack.path
            print 'fasta file path: ', fastaFilepath
            print 'cur dir: ', os.getcwd()
            print 'fasta file dir: ', os.path.dirname(fastaFilepath)
            print 'galaxyFn dir: ', os.path.dirname(os.path.realpath(galaxyFn))
            resFile = GalaxyRunSpecificFile(['trf', gsTrack.title, gsTrack.title + '.tmp'], galaxyFn)
            ensurePathExists(resFile.getDiskPath())
            print 'resFile: ', resFile.getDiskPath()
            trackDirName = os.path.dirname(os.path.realpath(resFile.getDiskPath()))
            print 'resFile dir: ', trackDirName
            # parameters = ["2", "5", "7", "80", "10", "50", "300"] #Madeleine suggestion
            parameters = [str(match), str(mismatch), str(delta), str(pm), str(pi), str(minscore), str(maxperiod)]
            instruction = [cls.TRF_PATH, gsTrack.path] + parameters + ["-d", "-h"]
            pipe = subprocess.Popen(instruction, cwd=trackDirName, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            results, errors = pipe.communicate()

            # print results

    @staticmethod
    def parseTRFResultFile(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith('Sequence:'):
                    seqTitleLine = line.strip().split(":")[1]
                    seqTitleLineList = seqTitleLine.split()
                    print seqTitleLineList


class TestHyperGuiTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Test hypergui tool'

    @classmethod
    def getInputBoxNames(cls):
        return []

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        cls.somemethod()

    @classmethod
    def somemethod(cls):
        DebugUtil.insertBreakPoint()
        import hyperbrowser.hyper_gui as hg
        print hg

    @staticmethod
    def getOutputFormat(choices=None):
        return 'customhtml'


def generateHeatmapStaticFile(proximityMatrix, nameList, galaxyFn,
                              rowLabels, colLabels, title,
                              figureHeight=600, figureWidth=720):
    from quick.extra.plot import RPlotUtil
    resultFile = GalaxyRunSpecificFile(nameList, galaxyFn=galaxyFn)
    resultFile.openRFigure(h=figureHeight, w=figureWidth)
    RPlotUtil.drawHeatmap(proximityMatrix, rowLabels, colLabels, mainTitle=title)
    RPlotUtil.rDevOff()
    return resultFile


class FastaSequencesAnalysisTool(GeneralGuiTool):

    PROXIMITY_FUNCTIONS_DICT = OrderedDict(
        [
            (levenshteinDistance.__name__, levenshteinDistance),
            (centeredLevenshteinDistance.__name__, centeredLevenshteinDistance),
            (jaroDistance.__name__, jaroDistance),
            (jaroWinklerDistance.__name__, jaroWinklerDistance),
            (alignmentScoreBlosum100Distance.__name__, alignmentScoreBlosum100Distance),
            (alignmentScoreBlosum62Distance.__name__, alignmentScoreBlosum62Distance),
            (centeredAlignmentScoreBlosum100Distance.__name__, centeredAlignmentScoreBlosum100Distance),
            (centeredAlignmentScoreBlosum62Distance.__name__, centeredAlignmentScoreBlosum62Distance),
            (fixedCenteredAlignmentScoreBlosum100Distance.__name__, fixedCenteredAlignmentScoreBlosum100Distance),
            (fixedCenteredAlignmentScoreBlosum62Distance.__name__, fixedCenteredAlignmentScoreBlosum62Distance),
            # (levenshteinSimilarity.__name__, levenshteinSimilarity),
            # (jaroSimilarity.__name__, jaroSimilarity),
            # (jaroWinklerSimilarity.__name__, jaroWinklerSimilarity),
        ]
    )

    #(method_name, requires_euclidean metric)
    LINKAGE_METHODS = [
        ('average', False),
        ('complete', False),
        ('single', False),
        # ('ward', True),
        # ('centroid', True),
        # ('median', True),
        # ('weighted', False),
    ]


    @staticmethod
    def getToolName():
        return 'Fasta sequences analysis tool'

    @classmethod
    def getInputBoxNames(cls):
        return [("Select a GSuite of fasta files (1 per class)", "gSuite"),
                ("Remove sequences that belong to multiple classes", "remDup"),
                ("Select sequence proximity measure", "proxMeasure"),
                ("Select linkage method for the hierarchical clustering", "linkMethod"),
                ("Specify maximum number of clusters", 'clusterNr'),
                ("Use random sample (same number of sequences sampled from each class)", "useRandom"),
                ("Max size of random sample", "sampleSize"),
                ("Random seed (empty for no seed)", "randSeed"),
                ("Balance the dataset sizes before clustering", "balanced")]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxRemDup(prevChoices):
        return True

    @classmethod
    def getOptionsBoxProxMeasure(cls, prevChoices):
        return cls.PROXIMITY_FUNCTIONS_DICT.keys()

    @classmethod
    def getOptionsBoxLinkMethod(cls, prevChoices):
        return [x[0] for x in cls.LINKAGE_METHODS]

    @staticmethod
    def getOptionsBoxClusterNr(prevChoices):
        return "50"

    @staticmethod
    def getOptionsBoxUseRandom(prevChoices):
        return False

    @staticmethod
    def getOptionsBoxSampleSize(prevChoices):
        if prevChoices.useRandom:
            return '100'

    @staticmethod
    def getOptionsBoxRandSeed(prevChoices):
        if prevChoices.useRandom:
            return ""

    @classmethod
    def getOptionsBoxBalanced(cls, prevChoices):
        if not prevChoices.useRandom:
            return False

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        #Set random seed if needed
        randomSeed = choices.randSeed
        from gold.util.RandomUtil import getManualSeed, setManualSeed, random
        if randomSeed and randomSeed != 'Random' and getManualSeed() is None:
            setManualSeed(int(randomSeed))

        #Read in the sequences
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        #trackName -> dict of sequence models
        dataDict = OrderedDict()
        for gsTrack in gSuite.allTracks():
            filePath = gsTrack.path
            with open(filePath, "r") as fastaSeq:
                lines = fastaSeq.readlines()
            seqToTCellReceptorSeqObjDict = cls.createSequenceDict(lines, label=gsTrack.title)
            dataDict[gsTrack.title] = seqToTCellReceptorSeqObjDict

        labels = dataDict.keys()
        k = len(labels)


        seqsToRemove = set()
        if choices.remDup:
            for i, label1 in enumerate(labels):
                for j, label2 in enumerate(labels):
                    if i < j:
                        seqSet1 = set(dataDict[label1].keys())
                        seqSet2 = set(dataDict[label2].keys())
                        seqsToRemove.update(seqSet1.intersection(seqSet2))

            for seqs in dataDict.values():
                for seq in seqsToRemove:
                    del seqs[seq]

        sequenceSummaryDict = OrderedDict()
        sequenceSummaryColumnTitles = [
            "Track title (label)",
            "Number of unique sequences",
                                       ]
        for gsTrack in gSuite.allTracks():
            summaryVals = []
            summaryVals.append(len(dataDict[gsTrack.title]))
            sequenceSummaryDict[gsTrack.title] = summaryVals

        randomSampleDataDict = dataDict
        if choices.useRandom:
            randomSampleDataDict = OrderedDict()
            n = int(choices.sampleSize)
            for label, seqData in dataDict.iteritems():
                seqNr = len(seqData)
                randomSample = random.sample(list(xrange(seqNr)), n)
                randomSampleDataDict[label] = OrderedDict()
                for i in randomSample:
                    currentSeq = dataDict[label].keys()[i]
                    randomSampleDataDict[label][currentSeq] = dataDict[label][currentSeq]

        randomSeqList = []
        labelList = []
        for label, seqs in randomSampleDataDict.iteritems():
            randomSeqList = randomSeqList + seqs.keys()
            labelList = labelList + [label] * len(seqs.keys())

        proximityFunction = cls.PROXIMITY_FUNCTIONS_DICT[choices.proxMeasure]
        distanceMatrix = generateProximityMatrix(randomSeqList, proximityFunction)
        print distanceMatrix
        import scipy.spatial.distance as ssd
        distArray = ssd.squareform(distanceMatrix)
        from scipy.cluster.hierarchy import linkage, fcluster
        Z = linkage(distArray, method=choices.linkMethod)
        fc = fcluster(Z, int(choices.clusterNr), criterion='maxclust')

        clusters = defaultdict(list)
        for i, clusterId in enumerate(fc):
            clusters[clusterId].append(labelList[i])

        clusterSummaryDict = OrderedDict()
        clusterSummaryColNames = ["Cluster ID", "Cluster size"] + \
                                 labels + \
                                 [x + " %" for x in labels]

        for clusterId, cluster in clusters.iteritems():
            clusterSize = len(cluster)
            clusterSummaryVals = [str(clusterSize)]
            labelPercentages = []
            clusterCounter = Counter(cluster)
            for label in labels:
                labelCount = clusterCounter[label]
                clusterSummaryVals.append(str(labelCount))
                labelPercentages.append(str(float(labelCount)/clusterSize))
            clusterSummaryVals = clusterSummaryVals + labelPercentages
            clusterSummaryDict[clusterId] = clusterSummaryVals


        #TODO: 4. Print results


        #TODO: 5. Print dendograms

        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin()
        htmlCore.tableFromDictionary(sequenceSummaryDict,
                                     sequenceSummaryColumnTitles)

        htmlCore.tableFromDictionary(clusterSummaryDict,
                                     clusterSummaryColNames)

        # htmlCore.paragraph(str(fc))
        # htmlCore.paragraph(str(Counter(fc)))
        htmlCore.divEnd()
        htmlCore.end()
        print htmlCore

        # titleLinesCount = 0
        # seqToTCellReceptorSeqObjDict = OrderedDict()
        # header = ''
        # for line in lines:
        #     linStrpd = line.strip()
        #     if linStrpd.startswith(">"):
        #         # titleLinesCount += 1
        #         header = linStrpd
        #     else:
        #         currSeq = linStrpd
        #         if currSeq in seqToTCellReceptorSeqObjDict:
        #             currSeqObj = seqToTCellReceptorSeqObjDict[currSeq]
        #         else:
        #             currSeqObj = TCellReceptorSequenceModel(currSeq)
        #             seqToTCellReceptorSeqObjDict[currSeq] = currSeqObj
        #         currSeqObj.addHeader(header)
        #
        # labelToListOfSequencesDict = defaultdict(list)
        # for seq, seqModel in seqToTCellReceptorSeqObjDict.iteritems():
        #     labelToListOfSequencesDict[seqModel.chainsLabel].append(seq)
        #
        # print "Class counts: "
        # for classLabel, seqsPerClass in labelToListOfSequencesDict.iteritems():
        #     print classLabel, ": ", str(len(seqsPerClass))
        #
        # print
        # print
        #
        # seqLenList = [len(x) for x in seqToTCellReceptorSeqObjDict]
        #
        # from numpy import mean, percentile
        # print "Summary for sequence lengths:"
        # print "Min len: ", min(seqLenList)
        # print "1% :", percentile(seqLenList, 1)
        # print "5% :", percentile(seqLenList, 5)
        # print "25% :", percentile(seqLenList, 25)
        # print "Avg len: ", mean(seqLenList)
        # print "75% :", percentile(seqLenList, 75)
        # print "95% :", percentile(seqLenList, 95)
        # print "99% :", percentile(seqLenList, 99)
        # print "Max len: ", max(seqLenList)
        # print ""
        # print ""
        #
        # copyNumberList = [x.copyNumber for _, x in seqToTCellReceptorSeqObjDict.iteritems()]
        #
        # print "Summary for sequence copy numbers:"
        # print "Min copy nr: ", min(copyNumberList)
        # print "1% :", percentile(copyNumberList, 1)
        # print "5% :", percentile(copyNumberList, 5)
        # print "25% :", percentile(copyNumberList, 25)
        # print "Avg copy nr: ", mean(copyNumberList)
        # print "75% :", percentile(copyNumberList, 75)
        # print "95% :", percentile(copyNumberList, 95)
        # print "99% :", percentile(copyNumberList, 99)
        # print "Max copy nr: ", max(copyNumberList)
        # print ""
        # print ""
        # seqNr = len(seqToTCellReceptorSeqObjDict)
        # print "Nr of unique sequences: ", str(seqNr)
        # print ""
        # print ""
        #
        # seqList = [x.sequence for x in seqToTCellReceptorSeqObjDict.values()]
        # labelList = [x.chainsLabel for x in seqToTCellReceptorSeqObjDict.values()]
        #
        # if choices.useRandom:
        #     #generate a 25% random sample of the sequences, max 2500
        #     import random
        #     if choices.randSeed:
        #         random.seed(choices.randSeed)
        #     n = int(choices.sampleSize)
        #     if n > (seqNr / 4):
        #         n = int(seqNr / 4)
        #
        #     randomSample = random.sample(list(xrange(seqNr)), n)
        #     randomSample.sort()
        #     randomSeqList = [seqList[x] for x in randomSample]
        #     seqList = randomSeqList
        #     randomLabelList = [labelList[x] for x in randomSample]
        #     labelList = randomLabelList
        #
        # proximityFunction = cls.PROXIMITY_FUNCTIONS_DICT[choices.proxMeasure]
        # fileNameList = ["heatmap.png"]
        # figureTitle = '''Heatmap of sequence proximity measured with %s''' % proximityFunction.__name__
        # heatmapStaticFile = cls.getHeatmapGalaxyRunSpecificFile(galaxyFn,
        #                                                         fileNameList,
        #                                                         proximityFunction,
        #                                                         figureTitle,
        #                                                         seqList,
        #                                                         labelList)
        # print heatmapStaticFile.getLink(linkText=figureTitle)
        # print heatmapStaticFile.getURL()

        # print ''
        # print ''
        # seqPairToDistanceDict = dict()
        # distanceToSeqPairDict = defaultdict(list)

        # import Levenshtein as lev
        # for i in xrange(len(seqs)):
        #     for j in xrange(i+1, len(seqs)):
        #         seq1 = seqs[i]
        #         seq2 = seqs[j]
        #         levDist = lev.distance(seq1, seq2)
        #         seqPairToDistanceDict[(seq1, seq2)] = levDist
        #         distanceToSeqPairDict[levDist].append((seq1, seq2))
        #
        # print ''
        # print ''
        # for seqPair, levDist in seqPairToDistanceDict.iteritems():
        #     print seqPair, "\t\t", str(levDist)
        #
        # print ''
        # print ''
        # for levDist, seqPairs  in distanceToSeqPairDict.iteritems():
        #     print str(levDist), "\t\t", seqPairs
        #     print "Pair count: ", len(seqPairs)
        #     print ''

    @classmethod
    def createSequenceDict(cls, lines, label=None):
        seqToTCellReceptorSeqObjDict = OrderedDict()
        header = ''
        for line in lines:
            linStrpd = line.strip()
            if linStrpd.startswith(">"):
                # titleLinesCount += 1
                header = linStrpd
            else:
                currSeq = linStrpd
                if currSeq in seqToTCellReceptorSeqObjDict:
                    currSeqObj = seqToTCellReceptorSeqObjDict[currSeq]
                else:
                    currSeqObj = TCellReceptorSequenceModel(currSeq, label=label)
                    seqToTCellReceptorSeqObjDict[currSeq] = currSeqObj
                currSeqObj.addHeader(header)
        return seqToTCellReceptorSeqObjDict

    @classmethod
    def getHeatmapGalaxyRunSpecificFile(cls, galaxyFn, fileNameList, proximityFunction, figureTitle,
                                        seqList, labels):
        proximityMatrix = generateProximityMatrix(sequenceList=seqList,
                                                  proximityFunc=proximityFunction,
                                                  isSymmetrical=True)
        heatmapStaticFile = generateHeatmapStaticFile(proximityMatrix,
                                                      fileNameList,
                                                      galaxyFn,
                                                      labels,
                                                      labels,
                                                      figureTitle)
        return heatmapStaticFile

    @staticmethod
    def validateAndReturnErrors(choices):
        if not choices.gSuite:
            return "Please select a gsuite file from history"

        if not choices.clusterNr:
            return "Please specify number of clusters"
        else:
            try:
                int(choices.clusterNr)
            except:
                return "Please specify a valid number of clusters"

        if choices.useRandom:
            if not choices.sampleSize:
                return "Please specify maximum size of the sample."
            else:
                try:
                    int(choices.sampleSize)
                except:
                    return "Maximum size of sample must be an integer value"

            # @staticmethod
            # def getOutputFormat(choices=None):
            #     return 'customhtml'

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'


    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True
