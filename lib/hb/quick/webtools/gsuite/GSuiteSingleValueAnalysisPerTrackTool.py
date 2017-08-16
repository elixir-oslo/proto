from collections import OrderedDict

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.description.AnalysisManager import AnalysisManager
from gold.gsuite import GSuiteConstants, GSuiteComposer
from gold.statistic.CountElementStat import CountElementStat
from gold.statistic.CountSegmentStat import CountSegmentStat
from gold.util.CommonFunctions import strWithNatLangFormatting
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.GalaxyInterface import GalaxyInterface
from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.AvgElementLengthStat import AvgElementLengthStat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


class GSuiteSingleValueAnalysisPerTrackTool(GeneralGuiTool, GenomeMixin, UserBinMixin, DebugMixin):
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
    ANALYSIS_PRETTY_NAME_TO_ANALYSIS_SPEC_MAPPING = {
        'Base-pair coverage': AnalysisSpec(CountSegmentStat),
        'Average length of segments': AnalysisSpec(AvgElementLengthStat),
        'Number of elements': AnalysisSpec(CountElementStat)
    }

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Compute a basic measure for each track in a GSuite"

    @classmethod
    def getInputBoxNames(cls):
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
        return [('Basic user mode', 'isBasic'),
                ('Select a GSuite:', 'gsuite'),
                ] + cls.getInputBoxNamesForGenomeSelection() + [
                   ('Select a measure (descriptive statistic)', 'analysis'),
                   # ('Select parameter', 'paramOne'),
                   ('', 'explainOutput'),
               ] + cls.getInputBoxNamesForUserBinSelection() + \
               cls.getInputBoxNamesForDebug()

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
    def getOptionsBoxGsuite(prevChoices):  # Alternatively: getOptionsBox1()
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

    @classmethod
    def getOptionsBoxAnalysis(cls, prevChoices):

        #         if prevChoices.analysisCategory:
        if prevChoices.gsuite:
            # TODO: fix implementation, dont delete commented out code until than
            # gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            # tracks = list(gSuite.allTracks())
            # #         fullCategory = AnalysisManager.combineMainAndSubCategories(prevChoices.analysisCategory, 'Basic')
            # fullCategory = AnalysisManager.combineMainAndSubCategories('Descriptive statistics', 'Basic')
            # return sorted([AnalysisDefHandler.splitAnalysisText(str(x))[0] for x in
            #                AnalysisManager.getValidAnalysesInCategory(fullCategory, gSuite.genome, tracks[0].trackName,
            #                                                           None)])

            return cls.ANALYSIS_PRETTY_NAME_TO_ANALYSIS_SPEC_MAPPING.keys()
            # AnalysisManager.getAnalysisDict()[cls.DESCRIPTIVE_BASIC_CAT].keys()

    # @classmethod
    # def getOptionsBoxParamOne(cls, prevChoices):
    #     if prevChoices.analysis:
    #         gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
    #         tracks = list(gSuite.allTracks())
    #         # fullCategory = AnalysisManager.combineMainAndSubCategories('Descriptive statistics', 'Basic')
    #         # analysis = GSuiteSingleValueAnalysisPerTrackTool._resolveAnalysisFromName(gSuite.genome, fullCategory,
    #         #                                                                           tracks[0].trackName,
    #         #                                                                           prevChoices.analysis)
    #         analysis = cls.ANALYSIS_PRETTY_NAME_TO_ANALYSIS_SPEC_MAPPING[prevChoices.analysis]
    #         paramOneName, paramOneValues = analysis.getFirstOptionKeyAndValues()
    #         if paramOneName and paramOneValues and len(paramOneValues) > 1:
    #             return paramOneValues

    # @staticmethod
    # def _resolveAnalysisFromName(genome, fullCategory, trackName, analysisName):
    #     selectedAnalysis = None
    #     for analysis in AnalysisManager.getValidAnalysesInCategory(fullCategory, genome, trackName, None):
    #         if analysisName == AnalysisDefHandler.splitAnalysisText(str(analysis))[0]:
    #             selectedAnalysis = analysis
    #
    #     return selectedAnalysis

    @staticmethod
    def getOptionsBoxExplainOutput(prevChoices):
        core = HtmlCore()
        core.divBegin(divClass='input-explanation')
        core.paragraph("""Select 'gsuite' for output to get a new GSuite with the results as a metadata column
        <br> or select 'html' to view a simple table of the results.""")
        core.divEnd()
        return '__rawstr__', str(core)

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
        DebugMixin._setDebugModeIfSelected(choices)
        genome = choices.genome
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        #         fullCategory = AnalysisManager.combineMainAndSubCategories(choices.analysisCategory, 'Basic')
        fullCategory = AnalysisManager.combineMainAndSubCategories('Descriptive statistics', 'Basic')
        tracks = list(gSuite.allTracks())
        analysisName = choices.analysis
        # selectedAnalysis = GSuiteSingleValueAnalysisPerTrackTool \
        #     ._resolveAnalysisFromName(gSuite.genome, fullCategory, tracks[0].trackName, analysisName)

        selectedAnalysis = cls.ANALYSIS_PRETTY_NAME_TO_ANALYSIS_SPEC_MAPPING[choices.analysis]

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=genome)
        # paramName, paramValues = selectedAnalysis.getFirstOptionKeyAndValues()
        # if paramName and paramValues:
        #     if len(paramValues) == 1:
        #         selectedAnalysis.addParameter(paramName, paramValues[0])
        #     else:
        #         selectedAnalysis.addParameter(paramName, choices.paramOne)

        tableDict = OrderedDict()

        for track in tracks:
            tableDict[track.title] = OrderedDict()
            result = doAnalysis(selectedAnalysis, analysisBins, [track])
            resultDict = result.getGlobalResult()
            if 'Result' in resultDict:
                track.setAttribute(analysisName.lower(), str(resultDict['Result']))
                tableDict[track.title][analysisName] = strWithNatLangFormatting(resultDict['Result'])
            else:
                for attrName, attrVal in resultDict.iteritems():
                    attrNameExtended = analysisName + ':' + attrName
                    track.setAttribute(attrNameExtended.lower(), str(attrVal))
                    tableDict[track.title][attrNameExtended] = strWithNatLangFormatting(attrVal)
                    # assert isinstance(resultDict['Result'], (int, basestring, float)), type(resultDict['Result'])

        core = HtmlCore()
        core.begin()
        core.header('Results: ' + analysisName)

        def _produceTable(core, tableDict=None, tableId=None):
            return core.tableFromDictOfDicts(tableDict, firstColName='Track title',
                                             tableId=tableId, expandable=True,
                                             visibleRows=20, presorted=0)

        tableId = 'results_table'
        tableFile = GalaxyRunSpecificFile([tableId, 'table.tsv'], galaxyFn)
        tabularHistElementName = 'Raw results: ' + analysisName

        gsuiteFile = GalaxyRunSpecificFile([tableId, 'input_with_results.gsuite'], galaxyFn)
        GSuiteComposer.composeToFile(gSuite, gsuiteFile.getDiskPath())
        gsuiteHistElementName = \
            getGSuiteHistoryOutputName('result', ', ' + analysisName, choices.gsuite)

        core.tableWithImportButtons(tabularFile=True, tabularFn=tableFile.getDiskPath(),
                                    tabularHistElementName=tabularHistElementName,
                                    gsuiteFile=True, gsuiteFn=gsuiteFile.getDiskPath(),
                                    gsuiteHistElementName=gsuiteHistElementName,
                                    produceTableCallbackFunc=_produceTable,
                                    tableDict=tableDict, tableId=tableId)
        core.end()
        print core

    @classmethod
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

        if not choices.gsuite:
            return ToolGuideController.getHtml(cls.toolId, [ToolGuideConfig.GSUITE_INPUT], choices.isBasic)

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gsuite)
        if errorStr:
            return errorStr

        errorString = cls._validateGenome(choices)
        if errorString:
            return errorString

        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        errorString = GeneralGuiTool._checkGSuiteRequirements \
            (gSuite,
             cls.GSUITE_ALLOWED_FILE_FORMATS,
             cls.GSUITE_ALLOWED_LOCATIONS,
             cls.GSUITE_ALLOWED_TRACK_TYPES,
             cls.GSUITE_DISALLOWED_GENOMES)

        if errorString:
            return errorString

        errorString = GeneralGuiTool._checkGSuiteTrackListSize(gSuite)
        if errorString:
            return errorString

        errorString = cls.validateUserBins(choices)
        if errorString:
            return errorString

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
        return 'customhtml'

    @staticmethod
    def isDebugMode():
        return False
