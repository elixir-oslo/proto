from urllib import quote

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteConstants
from gold.result.HeatmapPresenter import HeatmapFromTableDataPresenter
from gold.result.MatrixGlobalValuePresenter import \
    MatrixGlobalValueFromTableDataPresenter
from gold.track.Track import Track
from gold.util import CommonConstants
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.GalaxyInterface import GalaxyInterface
from quick.gsuite import GSuiteStatUtils
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.GSuiteVsGSuiteFullAnalysisV2Stat import RAW_OVERLAP_TABLE_RESULT_KEY, \
    SIMILARITY_SCORE_TABLE_RESULT_KEY
from quick.statistic.GSuiteVsGSuiteWrapperStat import GSuiteVsGSuiteWrapperStat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


# This is a template prototyping GUI that comes together with a corresponding
# web page.


class CoincidingTracksFromTwoGSuitesTool(GeneralGuiTool, UserBinMixin, GenomeMixin, DebugMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['queryGSuite', 'refGSuite']

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
        return "Are certain tracks of one suite coinciding particularly strongly with certain " \
               "tracks of another suite?"

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

        Note: the key has to be camelCase and start with a non-capital letter (e.g. "firstKey")
        '''
        return [
                   ('Basic user mode', 'isBasic'),
                   ('', 'basicQuestionId'),
                   ('Select the query GSuite', 'queryGSuite'),
                   ('Select the reference GSuite', 'refGSuite')
               ] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               [('Select track to track similarity/distance measure', 'similarityFunc'),
                ('Reversed (Used with similarity measures that are not symmetric)', 'reversed'),
                ('Remove zero rows from results table', 'removeZeroRow'),
                ('Remove zero columns from results table', 'removeZeroCol')
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
    def getOptionsBoxBasicQuestionId(prevChoices):
        return '__hidden__', None

    @staticmethod
    def getOptionsBoxQueryGSuite(prevChoices):
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
        '''
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxRefGSuite(prevChoices):
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxSimilarityFunc(prevChoices):
        if not prevChoices.isBasic:
            return GSuiteStatUtils.PAIRWISE_STAT_LABELS

    @staticmethod
    def getOptionsBoxReversed(prevChoices):
        if not prevChoices.isBasic:
            return False

    @staticmethod
    def getOptionsBoxRemoveZeroRow(prevChoices):
        if not prevChoices.isBasic:
            return ['No', 'Yes']

    @staticmethod
    def getOptionsBoxRemoveZeroCol(prevChoices):
        if not prevChoices.isBasic:
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

        cls._setDebugModeIfSelected(choices)
        genome = choices.genome
        queryGSuite = getGSuiteFromGalaxyTN(choices.queryGSuite)
        refGSuite = getGSuiteFromGalaxyTN(choices.refGSuite)
        if choices.similarityFunc:
            similarityStatClassNameKey = choices.similarityFunc
        else:
            similarityStatClassNameKey = GSuiteStatUtils.T5_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP

        isPointsVsSegments, pointsGSuite, segGSuite = cls.isPointsVsSegmentsAnalysis(queryGSuite, refGSuite)

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=genome)

        queryTrackList = [Track(x.trackName, x.title) for x in queryGSuite.allTracks()]
        refTrackList = [Track(x.trackName, x.title) for x in refGSuite.allTracks()]

        queryTrackTitles = CommonConstants.TRACK_TITLES_SEPARATOR.join(
            [quote(x.title, safe='') for x in queryGSuite.allTracks()])
        refTrackTitles = CommonConstants.TRACK_TITLES_SEPARATOR.join(
            [quote(x.title, safe='') for x in refGSuite.allTracks()])

        analysisSpec = AnalysisSpec(GSuiteVsGSuiteWrapperStat)
        analysisSpec.addParameter('queryTracksNum', str(len(queryTrackList)))
        analysisSpec.addParameter('refTracksNum', str(len(refTrackList)))
        analysisSpec.addParameter('queryTrackTitleList', queryTrackTitles)
        analysisSpec.addParameter('refTrackTitleList', refTrackTitles)
        analysisSpec.addParameter('similarityStatClassName',
                                  GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[similarityStatClassNameKey])
        if choices.removeZeroRow:
            analysisSpec.addParameter('removeZeroRow', choices.removeZeroRow)
        if choices.removeZeroCol:
            analysisSpec.addParameter('removeZeroColumn', choices.removeZeroCol)
        resultsObj = doAnalysis(analysisSpec, analysisBins, queryTrackList + refTrackList)
        results = resultsObj.getGlobalResult()

        # baseDir = GalaxyRunSpecificFile([RAW_OVERLAP_TABLE_RESULT_KEY], galaxyFn).getDiskPath()
        # rawOverlapHeatmapPresenter = HeatmapFromDictOfDictsPresenter(resultsObj, baseDir,
        #                                                              'Overlapping base-pair of tracks from the two suites',
        #                                                              printDimensions=False)

        rawOverlapTableData = results[RAW_OVERLAP_TABLE_RESULT_KEY]
        maxRawOverlap, maxROt1, maxROt2 = rawOverlapTableData.getMaxElement()
        similarityScoreTableData = results[SIMILARITY_SCORE_TABLE_RESULT_KEY]
        maxSimScore, maxSSt1, maxSSt2 = similarityScoreTableData.getMaxElement()

        baseDir = GalaxyRunSpecificFile([], galaxyFn=galaxyFn).getDiskPath()
        heatmapPresenter = HeatmapFromTableDataPresenter(resultsObj, baseDir=baseDir,
                                            header='Overlapping base-pairs between the tracks of the two suites',
                                            printDimensions=False)
        tablePresenter = MatrixGlobalValueFromTableDataPresenter(resultsObj, baseDir=baseDir,
                                            header='Table of overlapping base-pairs between the tracks of the two suites')

        core = HtmlCore()
        core.begin()
        core.divBegin(divId='results-page')
        core.divBegin(divId='svs-res-main-div', divClass='svs-res-main')    
        core.divBegin(divId='raw-overlap-div', divClass='results-section')
        core.divBegin(divId='raw-overlap-table', divClass='svs-table-div')
        core.header('Base-pair overlaps between the tracks of the two GSuites')
        core.paragraph("""From the tracks in the two GSuites the highest base-pair overlap <b>(%s bps)</b>
        is observed for the pair of <b>'%s'</b> and <b>'%s'</b>.""" % (maxRawOverlap, maxROt1, maxROt2))
        
        core.divBegin(divId='raw-table-result', divClass='result-div')
        core.divBegin(divId='raw-table-result', divClass='result-div-left')
        core.line('''Follow the links to view the results in an HTML table
        or raw tabular form:''')
        core.divEnd()
        core.divBegin(divId='raw-table-result', divClass='result-div-right')
        core.line(tablePresenter.getReference(RAW_OVERLAP_TABLE_RESULT_KEY))
        core.divEnd()#rawoverlap table
        core.divEnd()
        core.divEnd()
        core.divBegin(divId='raw-overlap-heatmap', divClass='svs-heatmap-div')
        try:
            core.header('Heatmap of base-pair overlaps')
            core.divBegin(divId='raw-table-result', divClass='result-div-heatmap')
            core.divBegin(divId='raw-table-result', divClass='result-div-left')
            core.line('''Follow the links to view the heatmap in the desired format:''')
            core.divEnd()
            core.divBegin(divId='raw-table-result', divClass='result-div-right')
            core.line(heatmapPresenter.getReference(RAW_OVERLAP_TABLE_RESULT_KEY))
            core.divEnd()
            core.divEnd()
        except:
            core.line('Heatmap for the base-pair overlaps could not be created.')
            core.divEnd()
            core.divEnd()
        core.divEnd()#rawoverlap heatmap
        core.divEnd()#rawoverlap
        

        core.divBegin(divId='sim-score-div', divClass='results-section')
        core.divBegin(divId='sim-score-table', divClass='svs-table-div')
        core.header('Similarity score between the tracks of the two GSuites measured by %s' % choices.similarityFunc)
        core.paragraph("""From the tracks in the two GSuites the highest similarity score <b>(%s)</b>
        is observed for the pair of <b>'%s'</b> and <b>'%s'</b>.""" % (maxSimScore, maxSSt1, maxSSt2))
        core.divBegin(divId='raw-table-result', divClass='result-div')
        core.divBegin(divId='raw-table-result', divClass='result-div-left')
        core.line("""Follow the links to view the results in an HTML table or raw tabular form:""")
        core.divEnd()
        core.divBegin(divId='raw-table-result', divClass='result-div-right')
        core.line(tablePresenter.getReference(SIMILARITY_SCORE_TABLE_RESULT_KEY))
        core.divEnd()
        core.divEnd()
        core.divEnd()#simscore table
        core.divBegin(divId='sim-score-heatmap', divClass='svs-heatmap-div')
        try:
            core.header('Heatmap of similarity scores')
            core.divBegin(divId='raw-table-result', divClass='result-div-heatmap')
            core.divBegin(divId='raw-table-result', divClass='result-div-left')
            core.line('''Follow the links to view the heatmap in the desired format:''')
            core.divEnd()
            core.divBegin(divId='raw-table-result', divClass='result-div-right')
            core.line(heatmapPresenter.getReference(SIMILARITY_SCORE_TABLE_RESULT_KEY))
            core.divEnd()
            core.divEnd()
        except:
            core.line('Heatmap for the similarity score could not be created.')
            core.divEnd()
            core.divEnd()
        core.divEnd()#simscore heatmap
        core.divEnd()#simscore
        core.divEnd()#results
        # core.paragraph(
        #     '''Table displaying the number of base-pairs overlapping between the tracks in the two suites:''')
        # core.tableFromDictOfDicts(rawOverlapTableData, firstColName='Track title')
        # # core.paragraph(rawOverlapHeatmapPresenter.getReference(resDictKey=RAW_OVERLAP_TABLE_RESULT_KEY))
        # core.paragraph(
        #     '''Table displaying the similarity score for the tracks in the two suites as measured by %s:''' % similarityStatClassNameKey)
        # core.tableFromDictOfDicts(similarityScoreTableData, firstColName='Track title')
        #
        core.divEnd()
        core.end()

        print str(core)

    @staticmethod
    def isPointsVsSegmentsAnalysis(queryGSuite, refGSuite):
        if (queryGSuite.trackType in [GSuiteConstants.POINTS,
                                      GSuiteConstants.VALUED_POINTS,
                                      GSuiteConstants.LINKED_POINTS,
                                      GSuiteConstants.LINKED_VALUED_POINTS] \
                    and \
                        refGSuite.trackType in [GSuiteConstants.SEGMENTS,
                                                GSuiteConstants.VALUED_SEGMENTS,
                                                GSuiteConstants.LINKED_SEGMENTS,
                                                GSuiteConstants.LINKED_VALUED_SEGMENTS]):
            return True, queryGSuite, refGSuite
        elif (refGSuite.trackType in [GSuiteConstants.POINTS,
                                      GSuiteConstants.VALUED_POINTS,
                                      GSuiteConstants.LINKED_POINTS,
                                      GSuiteConstants.LINKED_VALUED_POINTS] \
                      and \
                          queryGSuite.trackType in [GSuiteConstants.SEGMENTS,
                                                    GSuiteConstants.VALUED_SEGMENTS,
                                                    GSuiteConstants.LINKED_SEGMENTS,
                                                    GSuiteConstants.LINKED_VALUED_SEGMENTS]):
            return True, refGSuite, queryGSuite
        else:
            return False, None, None

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

        if not (choices.queryGSuite and choices.refGSuite):
            return ToolGuideController.getHtml(cls.toolId, [ToolGuideConfig.GSUITE_INPUT], choices.isBasic)

        errorString = GeneralGuiTool._checkGSuiteFile(choices.queryGSuite)
        if errorString:
            return errorString
        errorString = GeneralGuiTool._checkGSuiteFile(choices.refGSuite)
        if errorString:
            return errorString

        qGSuite = getGSuiteFromGalaxyTN(choices.queryGSuite)

        errorString = GeneralGuiTool._checkGSuiteRequirements \
            (qGSuite,
             cls.GSUITE_ALLOWED_FILE_FORMATS,
             cls.GSUITE_ALLOWED_LOCATIONS,
             cls.GSUITE_ALLOWED_TRACK_TYPES,
             cls.GSUITE_DISALLOWED_GENOMES)

        if errorString:
            return errorString

        errorString = GeneralGuiTool._checkGSuiteTrackListSize(qGSuite)
        if errorString:
            return errorString

        refGSuite = getGSuiteFromGalaxyTN(choices.refGSuite)

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

        errorString = cls._validateGenome(choices)
        if errorString:
            return errorString

        errorString = cls.validateUserBins(choices)
        if errorString:
            return errorString

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
        '''
       Specifies whether the tool is accessible to all users. If False, the
       tool is only accessible to a restricted set of users as defined in
       LocalOSConfig.py.
       '''
        return True

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
    @staticmethod
    def getToolDescription():
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        core = HtmlCore()
        core.divBegin()
        core.paragraph("""This tools implements a solution to the statistical question
                    'Are certain tracks of one suite coinciding particularly strongly with
                    certain tracks of another suite?'. To use the tool:""")
        core.orderedList(["Select the query GSuite (dataset collection of interest).",
                          "Select the reference GSuite (dataset collection to be screened against the query collection).",
                          "Select additional options (advanced mode only).",
                          "Execute the tool."])
        core.paragraph("""<br><br><b>Tool illustration.</b>
                    Coinciding tracks from two collections.<br>
                    Qi - Query track i (i = 1,..,m).<br>
                    Ri - Reference track i (i = 1,..,n).<br>
                    """)
        core.divEnd()
        return str(core)

    @staticmethod
    def getToolIllustration():
        '''
        Specifies an id used by StaticFile.py to reference an illustration file
        on disk. The id is a list of optional directory names followed by a file
        name. The base directory is STATIC_PATH as defined by AutoConfig.py. The
        full path is created from the base directory followed by the id.
        '''
        return ['illustrations', 'tools', 'suite-suite.png']
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

    @staticmethod
    def isDebugMode():
        '''
        Specifies whether debug messages are printed.
        '''
        return False

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
