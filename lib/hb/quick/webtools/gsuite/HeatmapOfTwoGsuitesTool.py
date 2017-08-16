from collections import OrderedDict
from urllib import quote

from gold.gsuite import GSuiteConstants
from gold.util.CommonConstants import TRACK_TITLES_SEPARATOR
from quick.multitrack.MultiTrackAnalysis import MultiTrackAnalysis
from quick.multitrack.MultiTrackCommon import getGSuiteDataFromGalaxyTN,\
    getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


class HeatmapOfTwoGsuitesTool(GeneralGuiTool, UserBinMixin, DebugMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['histElement1', 'histElement2']

    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]
    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    MIN_NUMBER_OF_TRACKS = 3
    MAX_NUMBER_OF_TRACKS = 1500

    STATISTIC_CHOICES = OrderedDict([
        ('Base pair overlap', 'TpRawOverlapStat'),
        ('Base pair overlap enrichment', 'SimpleObservedToExpectedBpOverlapStat')
    ])

    DIST_METHOD_CHOICES = OrderedDict([
        ('Euclidean distance', 'euclidean'),
        ('Euclidean distance of positive terms only', 'euclidean_positive'),
        ('Manhattan distance', 'manhattan'),
        ('Manhattan distance of positive terms only', 'manhattan_positive'),
        ('Cubic distance (Minkowski of power 3)', 'minkowski'),
        ('Cubic distance of positive terms only (Minkowski of power 3)', 'minkowski_positive')])

    CLUST_METHOD_CHOICES = OrderedDict([
        ('Average linkage', 'average'),
        ('Complete linkage (max distance)', 'complete'),
        ('Single linkage (min distance)', 'single'),
        ('Centroid linkage', 'centroid'),
        ('Ward\'s minimum-variance method', 'ward'),
        ('Divisive Analysis Clustering', 'diana')])

    DEFAULT_NUM_CLUSTERS = '1'

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Create heatmap over all combinations of tracks from two GSuites"

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
                ('Select first GSuite from history (rows)','histElement1'),
                ('Select second GSuite from history (columns)','histElement2'),
                ('Select descriptive statistic', 'statistic'),
                ('Distance measure for clustering', 'distMethod'),
                ('Hierarchical clustering method', 'clustMethod'),
                ('Divide row tracks into sub-clusters (separate heatmaps)?', 'divideRows'),
                ('Number of sub-clusters for row tracks', 'numClustersRows'),
                ('Divide column tracks into sub-clusters (separate heatmaps)?', 'divideCols'),
                ('Number of sub-clusters for column tracks', 'numClustersCols')] + \
               cls.getInputBoxNamesForUserBinSelection() + \
               cls.getInputBoxNamesForDebug()
        
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
    def getOptionsBoxIsBasic(): # Alternatively: getOptionsBox1()
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
        return False

    @staticmethod
    def getOptionsBoxHistElement1(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return '__history__', 'gsuite', 'tabular', 'txt'

    @staticmethod
    def getOptionsBoxHistElement2(prevChoices):
        return '__history__', 'gsuite', 'tabular', 'txt'

    @classmethod
    def getOptionsBoxStatistic(cls, prevChoices):
        return cls.STATISTIC_CHOICES.keys()

    @classmethod
    def getOptionsBoxDistMethod(cls, prevChoices):
        if not prevChoices.isBasic:
            return cls.DIST_METHOD_CHOICES.keys()

    @classmethod
    def getOptionsBoxClustMethod(cls, prevChoices):
        if not prevChoices.isBasic:
            return cls.CLUST_METHOD_CHOICES.keys()

    @classmethod
    def getOptionsBoxDivideRows(cls, prevChoices):
        if not prevChoices.isBasic:
            return ['No', 'Yes']

    @classmethod
    def getOptionsBoxNumClustersRows(cls, prevChoices):
        if not prevChoices.isBasic:
            if prevChoices.divideRows == 'Yes':
                return cls.DEFAULT_NUM_CLUSTERS, 1

    @classmethod
    def getOptionsBoxDivideCols(cls, prevChoices):
        if not prevChoices.isBasic:
            return ['No', 'Yes']

    @classmethod
    def getOptionsBoxNumClustersCols(cls, prevChoices):
        if not prevChoices.isBasic:
            if prevChoices.divideCols == 'Yes':
                return cls.DEFAULT_NUM_CLUSTERS, 1

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
    def _getTrackData(choices):
        trackTitles1, trackNames1, genome = getGSuiteDataFromGalaxyTN(choices.histElement1)
        trackTitles2, trackNames2 = getGSuiteDataFromGalaxyTN(choices.histElement2)[:2]
        trackTitles = trackTitles1 + trackTitles2
        trackNames = trackNames1 + trackNames2

        return trackTitles, trackNames, genome, len(trackNames1)

    @classmethod
    def _createAnalysisDef(cls, choices):
        analysisDef = ''

        for argument,conversionDict in [('distMethod', cls.DIST_METHOD_CHOICES),
                                        ('clustMethod', cls.CLUST_METHOD_CHOICES)]:

            choice = getattr(choices, argument)

            if not choice:
                choice = conversionDict.keys()[0]

            analysisDef += '[%s=%s]' % (argument, conversionDict[choice])

        for key,argument in [('divideRows', 'numClustersRows'),
                             ('divideCols', 'numClustersCols')]:

            choice = getattr(choices, key)

            if choice == 'Yes':
                choice = getattr(choices, argument)
            else:
                choice = cls.DEFAULT_NUM_CLUSTERS

            analysisDef += '[%s=%s]' % (argument, choice)

        analysisDef += '[childStat=CollectionVsCollectionStat]'

        trackTitles, trackNames, genome, firstCollectionTrackNr = cls._getTrackData(choices)

        analysisDef += '[trackTitles=%s]' % TRACK_TITLES_SEPARATOR.join(quote(t, safe='') for t in trackTitles)
        analysisDef += '[rawStatistic=%s]' % cls.STATISTIC_CHOICES[choices.statistic]
        analysisDef += '[firstCollectionTrackNr=%s]' % firstCollectionTrackNr
        analysisDef += '[extraTracks=%s]' % '&'.join(['|'.join(quote(part, safe='') for part in tn) for tn in trackNames[2:] ])

        analysisDef += ' -> ClusterMatrixStat'

        return analysisDef

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

        trackTitles, trackNames, genome, firstCollectionTrackNr = cls._getTrackData(choices)
        
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        multiTrackAnalysis = MultiTrackAnalysis(trackNames, trackTitles, regSpec,
                                                binSpec, genome, galaxyFn,
                                                analysisDef=cls._createAnalysisDef(choices))
        multiTrackAnalysis.execute(printTrackNamesTable=False)

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

        if not choices.histElement1 or not choices.histElement2:
            return ToolGuideController.getHtml(cls.toolId, [ToolGuideConfig.GSUITE_INPUT], choices.isBasic)
        
        gSuiteList = []
        for desc,histElement in [('first', choices.histElement1), ('second', choices.histElement2)]:
            errorString = cls._checkGSuiteFile(histElement)
            if errorString:
                return errorString

            gSuite = getGSuiteFromGalaxyTN(histElement)

            errorString = cls._checkGSuiteTrackListSize\
                (gSuite, minSize=cls.MIN_NUMBER_OF_TRACKS, maxSize=cls.MAX_NUMBER_OF_TRACKS)
            if errorString:
                return errorString

            errorString = cls._checkGSuiteRequirements \
                    (gSuite,
                     cls.GSUITE_ALLOWED_FILE_FORMATS,
                     cls.GSUITE_ALLOWED_LOCATIONS,
                     cls.GSUITE_ALLOWED_TRACK_TYPES,
                     cls.GSUITE_DISALLOWED_GENOMES)
            if errorString:
                return 'Error in the %s GSuite file: ' % desc + errorString

            gSuiteList.append(gSuite)

        errorString = cls._checkGenomeEquality(*[gSuite.genome for gSuite in gSuiteList])
        if errorString:
            return errorString

        for i, desc, divideChoice, numClustersChoice in \
                [(0, 'row', choices.divideRows, choices.numClustersRows),
                 (1, 'column', choices.divideCols, choices.numClustersCols)]:
            if divideChoice == 'Yes':
                try:
                    numClusters = int(numClustersChoice)
                except:
                    return numClustersChoice + ' is not an integer (number)'

                numTracks = gSuiteList[i].numTracks()
                if numClusters < 1 or numClusters > (numTracks / 2):
                    return 'The number of cluster for the %s tracks must be between 1 and %s' \
                        % (desc, numTracks / 2)

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

    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True

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
    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.paragraph('Loops through all combinations of tracks from two GSuite files '
                       'where the two tracks are from different GSuites. For all these '
                       'combination, a discrete statistic is calculated, and the resulting '
                       'table is clustered and shown both as a heatmap and a table.')

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
                                      disallowedGenomes=cls.GSUITE_DISALLOWED_GENOMES)

        return str(core)
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
    #
    #@staticmethod
    #def getFullExampleURL():
    #    return None
    #
    #@classmethod
    #def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    @staticmethod
    def isDebugMode():
        '''
        Specifies whether debug messages are printed.
        '''
        return False
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
