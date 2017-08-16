import quick.gsuite.GSuiteHbIntegration
from gold.gsuite import GSuiteConstants, GSuiteFunctions
from gold.util.CommonFunctions import prettyPrintTrackName,\
    strWithNatLangFormatting
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util import TrackReportCommon
from quick.util.TrackReportCommon import STAT_LIST_INDEX,\
    STAT_FACTOR_OBSERVED_VS_EXPECTED, addPlotToHtmlCore
from quick.visualization.VisualizationUtil import normalizeMatrixData
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.BasicModeAnalysisInfoMixin import BasicModeAnalysisInfoMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


# This is a template prototyping GUI that comes together with a corresponding
# web page.
class TrackVsCollectionAnalysisTool(GeneralGuiTool, UserBinMixin,
                                    GenomeMixin, BasicModeAnalysisInfoMixin):

    GSUITE_FILE_OPTIONS_BOX_KEYS = ['refTrackCollection']
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
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Screen track against a track collection"

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
#                 BasicModeAnalysisInfo.getInputBoxNamesForAnalysisInfo() +\
#                 [('Basic mode question id', 'bmQid'),
#                  ('Analysis info:', 'analysisInfo')] +\
        return cls.getInputBoxNamesForAnalysisInfo() + \
               [('Basic user mode', 'isBasic')] + \
               [('Select query track from history','targetTrack'),
                ('Select reference GSuite', 'refTrackCollection')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
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
    
#     @staticmethod
#     def getOptionsBoxAnalysisInfo(prevChoices):
#         return ('__rawstr__', '<p> id: ' + prevChoices.basicQuestionId + '</p>')
#     
#     @staticmethod
#     def getOptionsBoxAnalysisInfo(prevChoices):
#         retStr = '<p> id: ' + prevChoices.basicQuestionId + '</p>'
#         return '__rawstr__', retStr
# 
#     @staticmethod
#     def getOptionsBoxTargetTrackGenome(prevChoices):
#         return GeneralGuiTool.GENOME_SELECT_ELEMENT

    @staticmethod
    def getOptionsBoxTargetTrack(prevChoices): # Alternatively: getOptionsBox1()
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
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxRefTrackCollection(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    #@staticmethod
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

#     @staticmethod
#     def getOutputFormat(choices=None):
#         return 'customhtml'



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
        genome = choices.genome
        targetTrack = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, choices.targetTrack, printErrors=False, printProgress=False)

        refGSuite = getGSuiteFromGalaxyTN(choices.refTrackCollection)

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=genome) 

        results = TrackReportCommon.getOverlapResultsForTrackVsCollection(genome, targetTrack, refGSuite, analysisBins=analysisBins)
        processedResults = TrackReportCommon.processRawResults(results)
        
        targetTrackTitle = prettyPrintTrackName(targetTrack)
        title = 'Screening of track ' + targetTrackTitle
        sortedProcessedResultsTupleList = sorted(processedResults.iteritems(), 
            key=lambda x:x[1][STAT_LIST_INDEX[STAT_FACTOR_OBSERVED_VS_EXPECTED]], 
            reverse=True)
        refTrackNames = [x[0] for x in sortedProcessedResultsTupleList]
        refTrackNames = [x.replace('\'', '').replace('"','') for x in refTrackNames]
        plotData = [x[1] for x in sortedProcessedResultsTupleList]
#         plotData = zip(*plotData) #invert
        plotData = normalizeMatrixData(plotData)

        printVals = tuple([str(targetTrackTitle)]) + tuple([str(x[0]) for x in sortedProcessedResultsTupleList[0:3]])

        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.header(title)
        
        if choices.bmQid and choices.bmQid not in ['None']:
            htmlCore.append(str(
                quick.gsuite.GSuiteHbIntegration.getAnalysisQuestionInfoHtml(choices.bmQid)))
        
        htmlCore.divBegin('resultsDiv')
        htmlCore.paragraph(
        '''
            The query track <b>%s</b> overlaps most strongly (is most highly enriched) with the tracks <b>%s</b>, <b>%s</b> and <b>%s</b> 
            from the selected collection. See below for a full (ranked) table of overlap and enrichment.
        ''' % printVals
        )
        
        htmlCore.paragraph('''
        The coverage of the query track is %s bps.
        ''' % strWithNatLangFormatting(TrackReportCommon.getQueryTrackCoverageFromRawOverlapResults(results))
        )
        
        htmlCore.tableHeader(TrackReportCommon.HEADER_ROW, sortable=True, tableId='resultsTable')
        for refTrackName, refTrackResults in sortedProcessedResultsTupleList:
            line = [refTrackName] + [strWithNatLangFormatting(x) for x in refTrackResults]
            htmlCore.tableLine(line)
        htmlCore.tableFooter()
        htmlCore.divEnd()
        
        '''

        addColumnPlotToHtmlCore(htmlCore, 
                                refTrackNames,  
                                TrackReportCommon.HEADER_ROW[1:], 
                                'stat', 'Results plot (data is normalized for better visual comparison) ', 
                                plotData, xAxisRotation = 315)
        '''
        addPlotToHtmlCore(htmlCore, 
                        refTrackNames,  
                        TrackReportCommon.HEADER_ROW[1:], 
                        'stat', 'Results plot (data is normalized for better visual comparison) ', 
                        plotData, xAxisRotation = 315)
    
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

        if not choices.targetTrack and not choices.refTrackCollection:
            return ToolGuideController.getHtml(cls.toolId, [ToolGuideConfig.TRACK_INPUT, ToolGuideConfig.GSUITE_INPUT], choices.isBasic)
        if not choices.targetTrack:
            return ToolGuideController.getHtml(cls.toolId, [ToolGuideConfig.TRACK_INPUT], choices.isBasic)
        if not choices.refTrackCollection:
            return ToolGuideController.getHtml(cls.toolId, [ToolGuideConfig.GSUITE_INPUT], choices.isBasic)
            
        errorString = GeneralGuiTool._checkGSuiteFile(choices.refTrackCollection)
        if errorString:
            return errorString

        errorString = cls._validateGenome(choices)
        if errorString:
            return errorString
        
        errorString = GeneralGuiTool._checkTrack(choices, 'targetTrack', 'genome')
        if errorString:
            return errorString


        refGSuite = getGSuiteFromGalaxyTN(choices.refTrackCollection)

        errorString = GeneralGuiTool._checkGSuiteRequirements \
            (refGSuite,
             cls.GSUITE_ALLOWED_FILE_FORMATS,
             cls.GSUITE_ALLOWED_LOCATIONS,
             cls.GSUITE_ALLOWED_TRACK_TYPES,
             cls.GSUITE_DISALLOWED_GENOMES)
        
        if errorString:
            return errorString

        errorString = GeneralGuiTool._checkGSuiteTrackListSize(refGSuite)
        if errorString:
            return errorString

        errorString = cls.validateUserBins(choices)
        if errorString:
            return errorString

#         if targetTrackGenome: #This should always be true for a valid GSuite
#             regSpec, binSpec = UserBinSelector.getRegsAndBinsSpec(choices)
#             if regSpec.strip() is '' or binSpec.strip() is '':
#                 return 'Region and bin must be specified'
#             ubSource = GalaxyInterface._getUserBinSource(regSpec, binSpec, targetTrackGenome)
#
#             hasBins = False
#             for bin in ubSource:
#                 hasBins = True
#                 break
#
#             if not hasBins:
#                 return 'Zero analysis bins specified. This may be caused by entering an incorrect filtering condition, e.g. a mistyped chromosome.'

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

        core.paragraph('The tool enables screening of a genome-wide dataset (track) '
                       'agains a track collection (GSuite).')

        core.paragraph('To run the tool, follow these steps:')

        core.orderedList(['Select a single target track from history',
                          'Select a reference track collection as a GSuite file from history',
                          'Select the genome region for the anaysis',
                          'Click "Execute"'])

        core.paragraph('The results present several different statistics for the '
                       'target dataset in reference to each dataset '
                       'from the collection, organized in a sortable table.')

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
                                      disallowedGenomes=cls.GSUITE_DISALLOWED_GENOMES)

        return str(core)

        #return '''
        #    The tool enables screening of a genome-wide dataset (track) agains a dataset collection (GSuite).<br>
        #    To run the tool first import a target dataset and a reference dataset collection into history.<br>
        #    Select them accordingly, select the genome region and press execute.<br>
        #    <br>
        #    The results present several different statistics for the target dataset in reference to each dataset<br>
        #    from the collection, organized in a sortable table.
        #'''

    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
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

    # @staticmethod
    # def getFullExampleURL():
    #     return 'u/hb-superuser/p/screen-track-against-a-track-collection'

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
    def getOutputFormat(choices=None):
        return 'customhtml'
