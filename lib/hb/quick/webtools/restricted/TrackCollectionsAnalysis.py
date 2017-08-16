from collections import OrderedDict

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteConstants
from gold.track.Track import Track
from gold.util.CommonFunctions import strWithStdFormatting
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.RawOverlapToSelfStat import RawOverlapToSelfStat
from quick.util.TrackReportCommon import STAT_OVERLAP_COUNT_BPS,\
    STAT_OVERLAP_RATIO, STAT_FACTOR_OBSERVED_VS_EXPECTED, processRawResults,\
    STAT_COVERAGE_RATIO_VS_REF_TRACK, STAT_COVERAGE_RATIO_VS_QUERY_TRACK,\
    STAT_LIST_INDEX
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.BasicModeAnalysisInfoMixin import BasicModeAnalysisInfoMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class TrackCollectionsAnalysis(GeneralGuiTool, UserBinMixin,
                               GenomeMixin, BasicModeAnalysisInfoMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gSuiteFirst', 'gSuiteSecond']
    ALLOW_UNKNOWN_GENOME = False
    ALLOW_GENOME_OVERRIDE = False
    ALLOW_MULTIPLE_GENOMES = False
    WHAT_GENOME_IS_USED_FOR = 'the analysis'

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
        return "Screen two track collections against each other"

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
        return cls.getInputBoxNamesForAnalysisInfo() + \
               [('Basic user mode', 'isBasic')] + \
               [('Select query GSuite', 'gSuiteFirst'),
                ('Select reference GSuite', 'gSuiteSecond')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               [('Select statistic', 'statistic'),
                ('Select overlap handling', 'intraOverlap')] + \
               cls.getInputBoxNamesForUserBinSelection()

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
    def getOptionsBoxIsBasic(prevChoices):
        return False


    @staticmethod
    def getOptionsBoxGSuiteFirst(prevChoices): # Alternatively: getOptionsBox1()
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
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxGSuiteSecond(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxStatistic(prevChoices):
        return [STAT_OVERLAP_COUNT_BPS,
                STAT_OVERLAP_RATIO,
                STAT_FACTOR_OBSERVED_VS_EXPECTED,
                STAT_COVERAGE_RATIO_VS_QUERY_TRACK,
                STAT_COVERAGE_RATIO_VS_REF_TRACK
                ]
    #@staticmethod
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getInfoForOptionsBoxKey(prevChoices):
    #    '''
    #    If not None, defines the string content of an clickable info box beside
    #    the corresponding input box. HTML is allowed.
    #    '''
    #    return None

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @staticmethod
    def getOptionsBoxIntraOverlap(prevChoices):
        return [TrackCollectionsAnalysis.MERGE_INTRA_OVERLAPS,
                 TrackCollectionsAnalysis.ALLOW_MULTIPLE_OVERLAP]

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
#         from gold.application.LogSetup import setupDebugModeAndLogging
        #setupDebugModeAndLogging()

#         targetTrackNames, targetTrackCollection, targetTrackGenome = getGSuiteDataFromGalaxyTN(choices.gSuiteFirst)
#         targetTracksDict = OrderedDict(zip(targetTrackNames, targetTrackCollection))
#         refTrackNames, refTrackCollection, refTrackCollectionGenome = getGSuiteDataFromGalaxyTN(choices.gSuiteSecond)
#         refTracksDict = OrderedDict(zip(refTrackNames, refTrackCollection))
#         
        targetGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteSecond)

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)


        if choices.intraOverlap == TrackCollectionsAnalysis.MERGE_INTRA_OVERLAPS:
            analysisDef = 'dummy -> RawOverlapStat'
        else:
            analysisDef = 'dummy [withOverlaps=yes] -> RawOverlapAllowSingleTrackOverlapsStat'
        results = OrderedDict()
#         for targetTrackName, targetTrack in targetTracksDict.iteritems():
#             for refTrackName, refTrack in refTracksDict.iteritems():
        for targetTrack in targetGSuite.allTracks():
            targetTrackName = targetTrack.title
            for refTrack in refGSuite.allTracks():
                refTrackName = refTrack.title
                if targetTrack.trackName == refTrack.trackName:
                    result = TrackCollectionsAnalysis.handleSameTrack(targetTrack.trackName, regSpec, binSpec,
                                                       choices.genome, galaxyFn)
                else:
                    result = GalaxyInterface.runManual([targetTrack.trackName, refTrack.trackName],
                                                       analysisDef, regSpec, binSpec,
                                                       choices.genome, galaxyFn,
                                                       printRunDescription=False,
                                                       printResults=False).getGlobalResult()
                if targetTrackName not in results :
                    results[targetTrackName] = OrderedDict()
                results[targetTrackName][refTrackName] = result

        stat = choices.statistic
        statIndex = STAT_LIST_INDEX[stat]
        title = 'Screening track collections  (' + stat + ')'

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

        transposedProcessedResults = [list(x) for x in zip(*processedResults)]

        tableHeader = ['Track names'] + targetGSuite.allTrackTitles()
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.header(title)
        htmlCore.divBegin('resultsDiv')
        htmlCore.tableHeader(tableHeader, sortable=True, tableId='resultsTable')
        for i, row in enumerate(transposedProcessedResults):
            line = [headerColumn[i]] + [strWithStdFormatting(x) for x in row]
            htmlCore.tableLine(line)
        htmlCore.tableFooter()
        htmlCore.divEnd()

#         #hicharts can't handle strings that contain ' or " as input for series names
        targetTrackNames = [x.replace('\'', '').replace('"','') for x in targetGSuite.allTrackTitles()]
        refTrackNames = [x.replace('\'', '').replace('"','') for x in refGSuite.allTrackTitles()]
# 
#         '''
#         addColumnPlotToHtmlCore(htmlCore, targetTrackNames, refTrackNames,
#                                 stat, title + ' plot',
#                                 processedResults, xAxisRotation = -45, height=800)
#         '''
#         '''
#         addPlotToHtmlCore(htmlCore, targetTrackNames, refTrackNames,
#                                 stat, title + ' plot',
#                                 processedResults, xAxisRotation = -45, height=400)
#         '''
#         
        from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
        vg = visualizationGraphs()
        result = vg.drawColumnChart(processedResults,
                      height=600,
                      yAxisTitle=stat,
                      categories=refTrackNames,
                      xAxisRotation=90,
                      seriesName=targetTrackNames,
                      shared=False,
                      titleText=title + ' plot',
                      overMouseAxisX=True,
                      overMouseLabelX = ' + this.value.substring(0, 10) +')
        
        htmlCore.line(result)
        #htmlCore.line(vg.visualizeResults(result, htmlCore))
        
        htmlCore.hideToggle(styleClass='debug')
        htmlCore.end()

        print htmlCore

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

        if not choices.gSuiteFirst:
            return ToolGuideController.getHtml(cls.toolId, [ToolGuideConfig.GSUITE_INPUT], choices.isBasic)
        if not choices.gSuiteSecond:
            return ToolGuideController.getHtml(cls.toolId, [ToolGuideConfig.GSUITE_INPUT], choices.isBasic)
        
        errorString = GeneralGuiTool._checkGSuiteFile(choices.gSuiteFirst)
        if errorString:
            return errorString
        targetGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        #targetTrackGenome = targetGSuite.genome

        errorString = GeneralGuiTool._checkGSuiteTrackListSize(targetGSuite)
        if errorString:
            return errorString

        errorString = GeneralGuiTool._checkGSuiteFile(choices.gSuiteSecond)
        if errorString:
            return errorString

        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteSecond)

        #errorString = GeneralGuiTool._checkGenomeEquality(targetTrackGenome, refGSuite.genome)
        #if errorString:
        #    return errorString

        errorString = GeneralGuiTool._checkGSuiteTrackListSize(refGSuite)
        if errorString:
            return errorString

        errorString = cls._validateGenome(choices)
        if errorString:
            return errorString

        errorString = GeneralGuiTool._checkGSuiteRequirements \
            (targetGSuite,
             TrackCollectionsAnalysis.GSUITE_ALLOWED_FILE_FORMATS,
             TrackCollectionsAnalysis.GSUITE_ALLOWED_LOCATIONS,
             TrackCollectionsAnalysis.GSUITE_ALLOWED_TRACK_TYPES,
             TrackCollectionsAnalysis.GSUITE_DISALLOWED_GENOMES)
        if errorString:
            return errorString

        errorString = GeneralGuiTool._checkGSuiteRequirements \
            (refGSuite,
             TrackCollectionsAnalysis.GSUITE_ALLOWED_FILE_FORMATS,
             TrackCollectionsAnalysis.GSUITE_ALLOWED_LOCATIONS,
             TrackCollectionsAnalysis.GSUITE_ALLOWED_TRACK_TYPES,
             TrackCollectionsAnalysis.GSUITE_DISALLOWED_GENOMES)
        if errorString:
            return errorString

        errorString = cls.validateUserBins(choices)
        if errorString:
            return errorString

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

    @classmethod
    def getToolDescription(cls):
        core = HtmlCore()

        core.paragraph('The tool provides screening of two track collections '
                       '(GSuite files) against each other. The input for the tool are '
                       'two GSuite files, a target and a reference one, that contain '
                       'one or more tracks each.')

        core.paragraph('To run the tool, follow these steps:')

        core.orderedList(['Select two track collections (GSuite files) from history.'
                          'Select the desired statistic that you want to be calculated '
                          'for each track pair.'
                          'Select the genome region for the anaysis',
                          'Click "Execute"'])

        core.paragraph('The results are presented in a sortable table and an interactive chart.')

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
                                      disallowedGenomes=cls.GSUITE_DISALLOWED_GENOMES)

        return str(core)

        #return '''
        #    The tool provides screening of two dataset collections (GSuites) against each other.<br><br>
        #    The input for the tool are two GSuites, a target and a reference one, that contain one or more datasets each.<br><br>
        #    To start using the tool, please import at least two GSuites into history.<br>
        #    Select the desired statistic that you want to be calculated for each dataset pair and execute.<br><br>
        #    The results are presented in a sortable table and an interactive chart.<br>
        #'''

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

    # @staticmethod
    # def getFullExampleURL():
    #     return 'u/hb-superuser/p/screen-two-track-collections-against-each-other'
    
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

    @classmethod
    def handleSameTrack(cls, trackName, regSpec, binSpec, genome, galaxyFn):
        
        analysisSpec = AnalysisSpec(RawOverlapToSelfStat)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome)
        
        return doAnalysis(analysisSpec, analysisBins, [Track(trackName)]).getGlobalResult()
        

    
