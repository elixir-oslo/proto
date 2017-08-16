from gold.gsuite import GSuiteConstants
from quick.multitrack.MultiTrackAnalysis import MultiTrackBasePairCoverage,\
    MultiTrackInclusionStructure, MultiTrackFactorsOfObserevedVsExpectedOverlap,\
    MultiTrackHypothesisTesting, MultiTrackCoverageDepthBps,\
    MultiTrackBasePairCoverageProportional, MultiTrackCoverageDepthProportional,\
    MultiTrackCoverageDepthExtra, MultiTrackCoverageDepthProportionalToAny,\
    MultiTrackExpectedOverlapGivenBinPresence,\
    MultiTrackFocusedTrackDepthCoverage,\
    MultiTrackFocusedTrackDepthCoverageProportional,\
    MultiTrackCoverageProportionToOthers
from quick.multitrack.MultiTrackCommon import getGSuiteDataFromGalaxyTN,\
    getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.UserBinMixin import UserBinMixin


# This is a template prototyping GUI that comes together with a corresponding
# web page.
class MultiTrackAnalysisTool(GeneralGuiTool, UserBinMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['histElement']

    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]
    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]
    
    LBL_BP_COVERAGE_BPS = 'Base pair coverage of all track combinations (bps)'
    LBL_BP_COVERAGE_PROPORTIONAL = 'Base pair coverage of all track combinations (proportion of bin size)'
    LBL_COVERAGE_DEPTH_BPS = 'Coverage depth of multiple tracks along the genome (bps)'
    LBL_COVERAGE_DEPTH_PROPORTIONAL = 'Coverage depth of multiple tracks along the genome (proportions of bin size)'
    LBL_COVERAGE_DEPTH_PROPORTIONAL_TO_EACHOTHER = 'Coverage depth of multiple tracks along the genome (proportions of any coverage (depth1-depthN))'
    LBL_COVERAGE_DEPTH_EXTRA = 'Proportion of further coverage at increasing depths'
    LBL_TRACK_COVERAGE_PROPORTION_TO_OTHERS = 'The proportion of each track covered by a varying number of other tracks'
    LBL_FACTORS_OBSERVED_VS_EXPECTED = 'Factors of observed versus expected overlap with various relations preserved'
    LBL_OBSERVED_VS_EXPECTED_GIVEN_BIN_PRESENCE = 'Factors of observed versus expected overlap given bin presence'
    LBL_HYPOTHESIS_TESTING_MULTI = 'Hypothesis testing on multi-track relations'
    LBL_INCLUSION_STRUCTURE = 'Inclusion structure between tracks'
    LBL_FOCUSED_TRACK_DEPTH_COVERAGE = 'Track coverage given depth of other tracks'
    LBL_FOCUSED_TRACK_DEPTH_COVERAGE_PROPORTIONAL = 'Proportional track coverage given depth of other tracks'
    ANALYSES_CATEGORY_DICT = {'Basic overlap':[
            LBL_BP_COVERAGE_BPS,
            LBL_BP_COVERAGE_PROPORTIONAL,
            LBL_COVERAGE_DEPTH_BPS,
            LBL_COVERAGE_DEPTH_PROPORTIONAL,
            LBL_COVERAGE_DEPTH_PROPORTIONAL_TO_EACHOTHER,
            LBL_COVERAGE_DEPTH_EXTRA,
            LBL_TRACK_COVERAGE_PROPORTION_TO_OTHERS
                                                ],
                              'Observed versus expected overlaps':[
            LBL_FACTORS_OBSERVED_VS_EXPECTED,
            LBL_OBSERVED_VS_EXPECTED_GIVEN_BIN_PRESENCE
                                                ],
                              'Hypothesis testing':[
            LBL_HYPOTHESIS_TESTING_MULTI
                                                    ],
                              'Inclusion structure':[
            LBL_INCLUSION_STRUCTURE,
            LBL_FOCUSED_TRACK_DEPTH_COVERAGE,
            LBL_FOCUSED_TRACK_DEPTH_COVERAGE_PROPORTIONAL
                                                    ]
                              }

    ##Constants
    ##The list of available analyses
#     ANALYSES_LIST = ['Base pair coverage of all track combinations',
#         'Inclusion structure between tracks',
# #         'Observed versus expected overlap with various relations preserved',
#         'Factors of observed versus expected overlap with various relations preserved',
#         'Hypothesis testing on multi-track relations',
#         'Coverage depth of multiple tracks along the genome']
#
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Analyse relations of tracks in GSuite"

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
                ('Select GSuite','histElement')] + [
            ('Select analysis category','AnalysisCategory'),
            ('Select analysis','Analysis'),
            ('Lower-order relations to preserve in null model','PreserveRelations'),
            ('Track properties to preserve in null model','PreserveProperties'),
            ('Number of MC samples','NumResamplings')
            ] + cls.getInputBoxNamesForUserBinSelection()
            
            
    @staticmethod
    def getOptionsBoxIsBasic():
        return False

    @staticmethod
    def getOptionsBoxHistElement(prevChoices): # Alternatively: getOptionsBox1()
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
        #should accept only gtrack suite (but user may not be aware of the types, a file uploaded with Upload file galaxy tool will upload a gsuite as txt by default)
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxAnalysisCategory(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return MultiTrackAnalysisTool.ANALYSES_CATEGORY_DICT.keys()

    @staticmethod
    def getOptionsBoxAnalysis(prevChoices):
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return MultiTrackAnalysisTool.ANALYSES_CATEGORY_DICT[prevChoices.AnalysisCategory]

    @staticmethod
    def getOptionsBoxPreserveRelations(prevChoices):
        if prevChoices.Analysis == MultiTrackAnalysisTool.LBL_HYPOTHESIS_TESTING_MULTI:
            return ['Do not preserve any pair-wise relations', \
                    'Preserve pair-wise relation between Track 1 and Track 3', \
                    'Preserve pair-wise relation between Track 2 and Track 3']

    @staticmethod
    def _hypothesisTestingIsSelcted(choices):
        return choices.Analysis == 'Hypothesis testing on multi-track relations'

    @classmethod
    def getOptionsBoxPreserveProperties(cls, prevChoices):
        if not (cls._hypothesisTestingIsSelcted(prevChoices) and prevChoices.PreserveRelations != None):
            return None

        if prevChoices.PreserveRelations == 'Do not preserve any pair-wise relations':
            tracks = 'T1 and T2'
            plural = 's'
        elif prevChoices.PreserveRelations == 'Preserve pair-wise relation between Track 1 and Track 3':
            tracks = 'T2'
            plural = ''
        elif prevChoices.PreserveRelations == 'Preserve pair-wise relation between Track 2 and Track 3':
            tracks = 'T1'
            plural = ''
        else:
            raise Exception(prevChoices.PreserveRelations )
        return [entry%(plural,tracks) for entry in ['For randomized track%s (%s), preserve segment and inter-segment lengths', \
                                                    'For randomized track(%s) (%s), preserve segment lengths']]

    @staticmethod
    def _getRandomizationAnalysisOption(choices):
        rtc = 'PermutedSegsAndIntersegsTrack' if 'inter-segment' in choices.PreserveProperties else 'PermutedSegsAndSampledIntersegsTrack'
        if choices.PreserveRelations == 'Do not preserve any pair-wise relations':
            randTrackClassTemplate = rtc+'_'+rtc
        elif choices.PreserveRelations == 'Preserve pair-wise relation between Track 1 and Track 3':
            randTrackClassTemplate = '_'+rtc
        elif choices.PreserveRelations == 'Preserve pair-wise relation between Track 2 and Track 3':
            randTrackClassTemplate = rtc+'_'
        else:
            raise
        return '[assumptions=%s]' % randTrackClassTemplate

    @staticmethod
    def getOptionsBoxNumResamplings(prevChoices):
        if prevChoices.Analysis == MultiTrackAnalysisTool.LBL_HYPOTHESIS_TESTING_MULTI:
            return ['2','10','100','1000']

    @staticmethod
    def getOutputFormat(choices=None):
        return 'customhtml'

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

        trackTitles, tracks, genome = getGSuiteDataFromGalaxyTN(choices.histElement)

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        multiTrackAnalysis = None
        if choices.Analysis == cls.LBL_BP_COVERAGE_BPS:
            multiTrackAnalysis = MultiTrackBasePairCoverage(
                                                            tracks,
                                                            trackTitles,
                                                            regSpec,
                                                            binSpec,
                                                            genome,
                                                            galaxyFn)

        elif choices.Analysis == cls.LBL_BP_COVERAGE_PROPORTIONAL:
            multiTrackAnalysis = MultiTrackBasePairCoverageProportional(
                                                            tracks,
                                                            trackTitles,
                                                            regSpec,
                                                            binSpec,
                                                            genome,
                                                            galaxyFn)
        elif choices.Analysis == cls.LBL_FACTORS_OBSERVED_VS_EXPECTED:
            multiTrackAnalysis = MultiTrackFactorsOfObserevedVsExpectedOverlap(
                                                            tracks,
                                                            trackTitles,
                                                            regSpec,
                                                            binSpec,
                                                            genome,
                                                            galaxyFn)
        elif choices.Analysis == cls.LBL_OBSERVED_VS_EXPECTED_GIVEN_BIN_PRESENCE:
            multiTrackAnalysis = MultiTrackExpectedOverlapGivenBinPresence(
                                                            tracks,
                                                            trackTitles,
                                                            regSpec,
                                                            binSpec,
                                                            genome,
                                                            galaxyFn)
        elif choices.Analysis == cls.LBL_HYPOTHESIS_TESTING_MULTI:
            randOption = cls._getRandomizationAnalysisOption(choices)
            numResamplingsOption = '[numResamplings=%s]' % choices.NumResamplings
            multiTrackAnalysis = MultiTrackHypothesisTesting(
                                                            tracks,
                                                            trackTitles,
                                                            regSpec,
                                                            binSpec,
                                                            genome,
                                                            galaxyFn,
                                                            randOption=randOption,
                                                            numResamplingsOption=numResamplingsOption)

        elif choices.Analysis == cls.LBL_COVERAGE_DEPTH_BPS:
            multiTrackAnalysis = MultiTrackCoverageDepthBps(
                                                            tracks,
                                                            trackTitles,
                                                            regSpec,
                                                            binSpec,
                                                            genome,
                                                            galaxyFn)

        elif choices.Analysis == cls.LBL_COVERAGE_DEPTH_PROPORTIONAL:
            multiTrackAnalysis = MultiTrackCoverageDepthProportional(
                                                            tracks,
                                                            trackTitles,
                                                            regSpec,
                                                            binSpec,
                                                            genome,
                                                            galaxyFn)

        elif choices.Analysis == cls.LBL_COVERAGE_DEPTH_PROPORTIONAL_TO_EACHOTHER:
            multiTrackAnalysis = MultiTrackCoverageDepthProportionalToAny(
                                                            tracks,
                                                            trackTitles,
                                                            regSpec,
                                                            binSpec,
                                                            genome,
                                                            galaxyFn)

        elif choices.Analysis == cls.LBL_COVERAGE_DEPTH_EXTRA:
            multiTrackAnalysis = MultiTrackCoverageDepthExtra(
                                                            tracks,
                                                            trackTitles,
                                                            regSpec,
                                                            binSpec,
                                                            genome,
                                                            galaxyFn)

        elif choices.Analysis == cls.LBL_TRACK_COVERAGE_PROPORTION_TO_OTHERS:
            multiTrackAnalysis = MultiTrackCoverageProportionToOthers(
                                                            tracks,
                                                            trackTitles,
                                                            regSpec,
                                                            binSpec,
                                                            genome,
                                                            galaxyFn)

        elif choices.Analysis == cls.LBL_INCLUSION_STRUCTURE:
            multiTrackAnalysis = MultiTrackInclusionStructure(
                                                            tracks,
                                                            trackTitles,
                                                            regSpec,
                                                            binSpec,
                                                            genome,
                                                            galaxyFn)

        elif choices.Analysis == cls.LBL_FOCUSED_TRACK_DEPTH_COVERAGE:
            multiTrackAnalysis = MultiTrackFocusedTrackDepthCoverage(
                                                            tracks,
                                                            trackTitles,
                                                            regSpec,
                                                            binSpec,
                                                            genome,
                                                            galaxyFn)

        elif choices.Analysis == cls.LBL_FOCUSED_TRACK_DEPTH_COVERAGE_PROPORTIONAL:
            multiTrackAnalysis = MultiTrackFocusedTrackDepthCoverageProportional(
                                                            tracks,
                                                            trackTitles,
                                                            regSpec,
                                                            binSpec,
                                                            genome,
                                                            galaxyFn)
        else:
            raise Exception(repr(choices.Analysis))
        multiTrackAnalysis.execute(printHtmlBeginEnd=False)

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

        if not choices.histElement:
            return ToolGuideController.getHtml(cls.toolId, [ToolGuideConfig.GSUITE_INPUT], choices.isBasic)
        errorString = GeneralGuiTool._checkGSuiteFile(choices.histElement)
        if errorString:
            return errorString

        gSuite = getGSuiteFromGalaxyTN(choices.histElement)

        if choices.Analysis in (MultiTrackAnalysisTool.LBL_FACTORS_OBSERVED_VS_EXPECTED,
                                MultiTrackAnalysisTool.LBL_HYPOTHESIS_TESTING_MULTI):
            errorString = GeneralGuiTool._checkGSuiteTrackListSize(gSuite, minSize=3, maxSize=3)
            if errorString:
                return errorString

        errorString = GeneralGuiTool._checkGSuiteRequirements \
                (gSuite,
                 MultiTrackAnalysisTool.GSUITE_ALLOWED_FILE_FORMATS,
                 MultiTrackAnalysisTool.GSUITE_ALLOWED_LOCATIONS,
                 MultiTrackAnalysisTool.GSUITE_ALLOWED_TRACK_TYPES,
                 MultiTrackAnalysisTool.GSUITE_DISALLOWED_GENOMES)
        if errorString:
            return errorString

        errorString = cls.validateUserBins(choices)
        if errorString:
            return errorString

#         regSpec, binSpec = UserBinSelector.getRegsAndBinsSpec(choices)
#         if regSpec.strip() is '' or binSpec.strip() is '':
#             return 'Region and bin must be specified'
#         ubSource = GalaxyInterface._getUserBinSource(regSpec, binSpec, gSuite.genome)
#
#         hasBins = False
#         for bin in ubSource:
#             hasBins = True
#             break
#
#         if not hasBins:
#             return 'Zero analysis bins specified. This may be caused by entering an incorrect filtering condition, e.g. a mistyped chromosome.'
#
        return None

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
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()

        core.paragraph('The tool offers a set of thirteen analysis options on genome-wide '
                       'datasets (tracks), divided in four categories. The analyses can be '
                       'executed on multiple datasets (as opposed to single and pair-wise).')

        core.paragraph('The input of each analysis is a GSuite which contains three or more '
                       'datasets in analysis ready format. To start using the tool, follow these steps:')

        core.orderedList(['Select a GSuite file in history',
                          'Select an analysis option',
                          'Select the genome region under analysis',
                          'Click "Execute"'])

        core.paragraph('The results are displayed in a result table corresponding to the '
                       'selected analysis. Combinations of tracks are denoted in binary '
                       'representation (e.g 1001 represents the combination of '
                       'the first and last track from a 4-element dataset).')

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
                                      disallowedGenomes=cls.GSUITE_DISALLOWED_GENOMES)

        return str(core)

        #return '''
        #The tool offers a set of thirteen analysis options on genome-wide datasets (tracks), divided in four categories.<br>
        #The analyses can be executed on multiple datasets (as opposed to single and pair-wise).<br>
        #<br>
        #The input of each analysis is a GSuite which contains three or more datasets in analysis ready format.<br>
        #To start using the tool, import a GSuite file in history.<br>
        #Select an analysis option and the genome region under analysis, and press execute.<br>
        #<br>
        #The results are displayed in a result table corresponding to the selected analysis.<br>
        #Combinations of tracks are denoted in binary representation (e.g 1001 represents the combination of<br>
        #the first and last track from a 4-element dataset).
        #'''
        
    @staticmethod
    def getFullExampleURL():
        return 'u/hb-superuser/p/analyse-relations-of-datasets-in-gsuite'
