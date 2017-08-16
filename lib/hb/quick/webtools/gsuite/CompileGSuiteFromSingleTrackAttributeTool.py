from collections import defaultdict

import gold.gsuite.GSuiteComposer as GSuiteComposer
import gold.gsuite.GSuiteConstants as GSuiteConstants
from gold.application.DataTypes import getSupportedFileSuffixes
from gold.origdata.FileFormatComposer import findMatchingFileFormatComposers, \
                                             getComposerClsFromFileFormatName
from gold.track.TrackFormat import TrackFormat
from gold.util.CommonFunctions import findKeysWithMaxVal, findKeysWithMinVal
from quick.application.ExternalTrackManager import ExternalTrackManager as etm
from quick.gsuite.GSuiteUtils import createGalaxyGSuiteBySplittingInputFileOnAttribute
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class CompileGSuiteFromSingleTrackAttributeTool(GeneralGuiTool):
    GSUITE_OUTPUT_LOCATION = GSuiteConstants.LOCAL
    GSUITE_OUTPUT_FILE_FORMAT = GSuiteConstants.PRIMARY
    GSUITE_OUTPUT_TRACK_TYPE = GSuiteConstants.SEGMENTS

    UNSUPPORTED_ATTRS = ['start', 'end', 'edges', 'weights']
    
    SHOW_STATISTICS_CHOICE_NO = 'No'
    SHOW_STATISTICS_CHOICE_YES = 'Yes (might be slow to load)'

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Create a GSuite by splitting a single track based on a category column/attribute"

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
        return [('Select genome:', 'genome'),
                ('Select an input track from history:', 'track'),
                ('Select column/attribute to split by', 'attr'),
                ('Show statistics of column/attribute values?', 'showStatistics'),
                ('Statistics of column/attribute values:', 'statistics'),
                ('Specify file format of tracks in output GSuite:', 'format')]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None
    #
    #@staticmethod
    #def getInputBoxGroups(choices=None):
    #    '''
    #    Creates a visual separation of groups of consecutive option boxes from the rest (fieldset).
    #    Each such group has an associated label (string), which is shown to the user. To define
    #    groups of option boxes, return a list of BoxGroup namedtuples with the label, the key
    #    (or index) of the first and last options boxes (inclusive).
    #
    #    Example:
    #        from quick.webtool.GeneralGuiTool import BoxGroup
    #        return [BoxGroup(label='A group of choices', first='firstKey', last='secondKey')]
    #    '''
    #    return None

    @staticmethod
    def getOptionsBoxGenome(): # Alternatively: getOptionsBox1()
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

    @staticmethod
    def getOptionsBoxTrack(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        if prevChoices.genome:
            return GeneralGuiTool.getHistorySelectionElement(*getSupportedFileSuffixes())

    @classmethod
    def getOptionsBoxAttr(cls, prevChoices):
        if prevChoices.track:
            geSource = etm.getGESourceFromGalaxyOrVirtualTN(prevChoices.track, prevChoices.genome)
            return [prefix for prefix in geSource.getPrefixList() \
                    if prefix not in cls.UNSUPPORTED_ATTRS ]

    @classmethod
    def getOptionsBoxShowStatistics(cls, prevChoices):
        if prevChoices.attr:
            return [cls.SHOW_STATISTICS_CHOICE_NO, cls.SHOW_STATISTICS_CHOICE_YES]

    @classmethod
    def getOptionsBoxStatistics(cls, prevChoices):
        if prevChoices.showStatistics == cls.SHOW_STATISTICS_CHOICE_YES:
            geSource = etm.getGESourceFromGalaxyOrVirtualTN(prevChoices.track, prevChoices.genome)

            valDict = defaultdict(int)
            numEls = 0
            for ge in geSource:
                valDict[str(getattr(ge, prevChoices.attr))] += 1
                numEls += 1

            return [['Statistic', 'Result'], \
                    ['Number of elements in track', str(numEls)],
                    ['Number of unique attribute values', str(len(valDict))],
                    ['Attribute(s) least represented in track (number of elements)', \
                     '|'.join(findKeysWithMinVal(valDict)) + ' (%s)' % min(valDict.values())],
                    ['Attribute(s) most represented in track (number of elements)', \
                     '|'.join(findKeysWithMaxVal(valDict)) + ' (%s)' % max(valDict.values())]]

    @staticmethod
    def getOptionsBoxFormat(prevChoices):
        if prevChoices.track:
            geSource = etm.getGESourceFromGalaxyOrVirtualTN(prevChoices.track, prevChoices.genome)
            tf = TrackFormat.createInstanceFromGeSource(geSource)
            matchingComposers = findMatchingFileFormatComposers(tf)
            conversions = [geSource.getFileFormatName() + \
                           ' (no conversion, track type: %s)' % tf.getFormatName()]
            conversions += ['%s -> %s (track type: %s)' % (geSource.getFileFormatName(), \
                            composerInfo.fileFormatName, composerInfo.trackFormatName) \
                            for composerInfo in matchingComposers \
                            if geSource.getFileFormatName() != composerInfo.fileFormatName]
            return conversions

    @staticmethod
    def _getComposerCls(choices):
        if ' -> ' in choices.format:
            fileFormatName = choices.format.split(' -> ')[1].split(' (')[0]
        else:
            fileFormatName = choices.format.split(' (')[0]
        return getComposerClsFromFileFormatName(fileFormatName)

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

    #@classmethod
    #def getExtraHistElements(cls, choices):
    #    from quick.webtools.GeneralGuiTool import HistElement
    #
    #    histList = []
    #    histList.append( HistElement(cls.HISTORY_HIDDEN_TRACK_STORAGE,
    #                                 GSuiteConstants.GSUITE_STORAGE_SUFFIX, hidden=True) )
    #    return histList

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
        genome = choices.genome
        geSource = etm.getGESourceFromGalaxyOrVirtualTN(choices.track, genome)
        #hiddenStorageFn = cls.extraGalaxyFn[cls.HISTORY_HIDDEN_TRACK_STORAGE]
        hiddenStorageFn = galaxyFn
        composerCls = cls._getComposerCls(choices)
        valAttr = choices.attr

        gSuite = createGalaxyGSuiteBySplittingInputFileOnAttribute\
            (hiddenStorageFn, geSource, genome, composerCls, valAttr)

        GSuiteComposer.composeToFile(gSuite, galaxyFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        errorStr = cls._checkTrack(choices, trackChoiceIndex='track', genomeChoiceIndex='genome')
        if errorStr:
            return errorStr
        
        if choices.track and not choices.attr:
            return 'You have chosen a track with no attributes (columns) supported for splitting. ' \
                   'Attributes that do not support splitting are: ' + ', '.join(cls.UNSUPPORTED_ATTRS)
        
        geSource = etm.getGESourceFromGalaxyOrVirtualTN(choices.track, choices.genome)
        trackFormat = TrackFormat.createInstanceFromGeSource(geSource)

        if trackFormat.isDense():
            return 'The track format of the selected track file is: %s' % trackFormat.getFormatName() +\
                   ' This tool only supports track types Points, Segments, or variations of these.'

    @classmethod
    def getOutputName(cls, choices):
        if choices.track:
            from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName

            description = ', splitted on column: %s' % choices.attr

            return getGSuiteHistoryOutputName('primary', description, choices.track)

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
        return True
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
    #def getInputBoxOrder():
    #    return None
    #
    #@staticmethod
    #def getInputBoxGroups():
    #    return None
    #
    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()
        core.paragraph('This tools takes a single track as input. The user then'
                       'selects one of the attributes of the track (typically a column).'
                       'The tools creates a range of separate output track files, '
                       'one for each of the different unique values for the selected '
                       'attribute (column) thar are present in the track. The tool thens '
                       'directs each track element (typically each line) into the '
                       'relevant output track, thus splitting all lines with a '
                       'particular value into a separate output track file. '
                       'The output track files are collected in a output GSuite file.')
        core.paragraph('In addition, the tool supports:')
        core.unorderedList(['Summary statistics of the selected attribute (column)',
                            'Conversion from the input file format into other supported '
                            'file formats (collected in the output GSuite)'])

        cls._addGSuiteFileDescription(core,
                                      outputLocation=cls.GSUITE_OUTPUT_LOCATION,
                                      outputFileFormat=cls.GSUITE_OUTPUT_FILE_FORMAT,
                                      outputTrackType=cls.GSUITE_OUTPUT_TRACK_TYPE,
                                      errorFile=False)

        return str(core)

    #
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by AutoConfig.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    #@staticmethod
    #def getFullExampleURL():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether the debug mode is turned on.
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
        return GSuiteConstants.GSUITE_SUFFIX
