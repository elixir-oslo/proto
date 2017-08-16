from collections import namedtuple, OrderedDict

from gold.application.DataTypes import getSupportedFileSuffixes
from gold.description.TrackInfo import TrackInfo
from gold.gsuite import GSuiteConstants
from gold.origdata.FileFormatComposer import getComposerClsFromFileSuffix
from quick.extra.TrackExtractor import TrackExtractor
from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin


# This is a template prototyping GUI that comes together with a corresponding
# web page.

FileFormatInfo = \
        namedtuple('FileFormatInfo',
                   ('fileFormatName', 'asOriginal', 'allowOverlaps', 'suffix'))


class GSuiteConvertFromPreprocessedToPrimaryTool(GeneralGuiTool, GenomeMixin):
    GSUITE_MIN_TRACK_COUNT = 1

    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_TRACK_TYPES = []

    GSUITE_OUTPUT_LOCATION = GSuiteConstants.LOCAL
    GSUITE_OUTPUT_FILE_FORMAT = GSuiteConstants.PRIMARY
    GSUITE_OUTPUT_TRACK_TYPE = ''

    HISTORY_PROGRESS_TITLE = 'Progress'
    HISTORY_PROGRESS_SUFFIX = 'customhtml'
    HISTORY_HIDDEN_TRACK_STORAGE = 'GSuite track storage'

    PROGRESS_PROCESS_DESCRIPTION = 'Converting tracks'

    OUTPUT_FORMAT_ORIGINAL = 'File formats as in original files'
    OUTPUT_FORMAT_OTHER = 'Select file format...'

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Convert preprocessed tracks in GSuite to primary tracks"

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

        Note: the key has to be camelCase and start with a non-capital letter (e.g. "firstKey")
        '''
        return [('Select GSuite file from history:', 'gsuite')] + \
                GenomeMixin.getInputBoxNamesForGenomeSelection() + \
                [('Convert tracks using:', 'changeFormat'),
                 ('Select file format to convert to (for all tracks):', 'outputFormat')]

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
    def getOptionsBoxGsuite(): # Alternatively: getOptionsBox1()
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
        return '__history__', GSuiteConstants.GSUITE_SUFFIX

    @classmethod
    def _allTracksHasOriginalFormat(cls, gSuite, genome):
        for track in gSuite.allTracks():
            if not TrackInfo(genome, track.trackName).fileType in \
                    getSupportedFileSuffixes():
                return False
        return True

    @classmethod
    def getOptionsBoxChangeFormat(cls, prevChoices):
        if prevChoices.gsuite and prevChoices.genome:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            if cls._allTracksHasOriginalFormat(gSuite, prevChoices.genome):
                return [cls.OUTPUT_FORMAT_ORIGINAL,
                        cls.OUTPUT_FORMAT_OTHER]
            else:
                return [cls.OUTPUT_FORMAT_OTHER]

    @classmethod
    def getOptionsBoxOutputFormat(cls, prevChoices): # Alternatively: getOptionsBox2()
        if prevChoices.changeFormat == cls.OUTPUT_FORMAT_OTHER:
            try:
                gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                genome = prevChoices.genome

                outputFormatDict = cls._getOutputFormatDict(gSuite, genome)
                return outputFormatDict.keys()
            except:
                return []

    @classmethod
    def _getOutputFormatDict(cls, gSuite, genome):
        outputFormatsPerTrack = []
        for track in gSuite.allTracks():
            outputFormatsPerTrack.append(
                cls._getAllOutputFormatsForTrack(genome, track))

        commonOutputFormats = reduce(set.intersection, outputFormatsPerTrack)
        outputFormatsDict = {}
        for fi in commonOutputFormats:
            # To remove duplicates where the only difference is that
            # the whole format is marked as the original format
            if not fi.asOriginal:
                originalFI = FileFormatInfo(fi.fileFormatName,
                                            True,
                                            fi.allowOverlaps,
                                            fi.suffix)
                if originalFI in commonOutputFormats:
                    continue

            outputFormatsDict[cls._getStrFromFileFormatInfo(fi)] = fi

        return OrderedDict(sorted(outputFormatsDict.items(), key=lambda t: t[0]))

    @staticmethod
    def _getAllOutputFormatsForTrack(genome, track):
        from quick.application.GalaxyInterface import GalaxyInterface

        trackOutputFormats = set()

        extractionOptions = \
            GalaxyInterface.getTrackExtractionOptions(
                genome, track.trackName)

        for opt in extractionOptions:
            extFormat, suffix = opt
            formatInfo = FileFormatInfo(
                *TrackExtractor.getAttrsFromExtractionFormat(extFormat),
                suffix=suffix)
            trackOutputFormats.add(formatInfo)

        return trackOutputFormats

    @classmethod
    def _getStrFromFileFormatInfo(cls, fi):
        allowOverlapsStr = TrackExtractor.ALLOW_OVERLAPS_TRUE_TEXT \
            if fi.allowOverlaps else TrackExtractor.ALLOW_OVERLAPS_FALSE_TEXT
        origFormatStr = ' [%s]' % TrackExtractor.ORIG_FILE_FORMAT_TEXT \
            if fi.asOriginal else ''
        fileFormatStr = '%s (%s)%s' % (fi.fileFormatName,
                                       allowOverlapsStr, origFormatStr)
        return fileFormatStr


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
    #
    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @classmethod
    def getExtraHistElements(cls, choices):
        from quick.webtools.GeneralGuiTool import HistElement
        histList = []
        histList.append(
            HistElement(getGSuiteHistoryOutputName('primary', datasetInfo=choices.gsuite),
                                                   GSuiteConstants.GSUITE_SUFFIX))
        histList.append(
            HistElement(getGSuiteHistoryOutputName('storage', datasetInfo=choices.gsuite),
                                                   GSuiteConstants.GSUITE_SUFFIX, hidden=True))
        return histList

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

        import gold.gsuite.GSuiteComposer as GSuiteComposer
        from gold.gsuite.GSuite import GSuite
        from gold.gsuite.GSuiteTrack import GSuiteTrack, GalaxyGSuiteTrack
        from quick.application.UserBinSource import GlobalBinSource
        from quick.extra.ProgressViewer import ProgressViewer
        from quick.extra.TrackExtractor import TrackExtractor

        genome = choices.genome
        fullGenomeBins = GlobalBinSource(genome)
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        progressViewer = ProgressViewer(
            [(cls.PROGRESS_PROCESS_DESCRIPTION, len(gSuite))], galaxyFn)

        outGSuite = GSuite()
        hiddenStorageFn = cls.extraGalaxyFn[
            getGSuiteHistoryOutputName('storage', datasetInfo=choices.gsuite)]

        fileNameSet = set()
        for track in gSuite.allTracks():
            fileName = cls._getUniqueFileName(fileNameSet, track.trackName)
            title = track.title
            attributes = track.attributes
            fi = cls._getFileFormatInfo(choices, gSuite, genome, track)

            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=hiddenStorageFn,
                                                extraFileName=fileName,
                                                suffix=fi.suffix)

            gSuiteTrack = GSuiteTrack(uri, title=title,
                                      genome=genome, attributes=attributes)

            TrackExtractor.extractOneTrackManyRegsToOneFile(
                track.trackName, fullGenomeBins,
                gSuiteTrack.path,
                fileFormatName=fi.fileFormatName,
                globalCoords=True,
                asOriginal=fi.asOriginal,
                allowOverlaps=fi.allowOverlaps)

            outGSuite.addTrack(gSuiteTrack)
            progressViewer.update()

        primaryFn = cls.extraGalaxyFn[
            getGSuiteHistoryOutputName('primary', datasetInfo=choices.gsuite)]
        GSuiteComposer.composeToFile(outGSuite, primaryFn)

    @staticmethod
    def _getUniqueFileName(fileNameSet, trackName):
        from gold.gsuite.GSuiteFunctions import \
            renameBaseFileNameWithDuplicateIdx

        candFileName = trackName[-1]
        duplicateIdx = 1

        while candFileName in fileNameSet:
            duplicateIdx += 1
            candFileName = renameBaseFileNameWithDuplicateIdx(candFileName,
                                                              duplicateIdx)
        fileNameSet.add(candFileName)
        return candFileName

    @classmethod
    def _getFileFormatInfo(cls, choices, gSuite, genome, track):
        if choices.changeFormat == cls.OUTPUT_FORMAT_ORIGINAL:
            suffix = TrackInfo(genome, track.trackName).fileType
            fileFormatName = \
                getComposerClsFromFileSuffix(suffix).FILE_FORMAT_NAME
            asOriginal = True
            allowOverlaps = True

            return FileFormatInfo(fileFormatName,
                                  asOriginal,
                                  allowOverlaps,
                                  suffix)
        else:
            outputFormatDict = cls._getOutputFormatDict(gSuite, genome)
            return outputFormatDict[choices.outputFormat]

    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        errorString = cls._checkGSuiteFile(choices.gsuite)
        if errorString:
            return errorString

        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        errorString = cls._checkGSuiteRequirements(
             gSuite,
             allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
             allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
             allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES)

        if errorString:
            return errorString

        errorStr = cls._validateGenome(choices)
        if errorStr:
            return errorStr

        errorString = GeneralGuiTool._checkGSuiteTrackListSize(
            gSuite, minSize=cls.GSUITE_MIN_TRACK_COUNT)
        if errorString:
            return errorString

    @classmethod
    def getOutputName(cls, choices):
        return getGSuiteHistoryOutputName('progress', datasetInfo=choices.gsuite)

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
    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()
        core.paragraph('Description of what my tool does.')

        cls._addGSuiteFileDescription(
            core,
            allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
            allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
            allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
            outputLocation=cls.GSUITE_OUTPUT_LOCATION,
            outputFileFormat=cls.GSUITE_OUTPUT_FILE_FORMAT,
            outputTrackType=cls.GSUITE_OUTPUT_TRACK_TYPE,
            errorFile=False,
            minTrackCount=cls.GSUITE_MIN_TRACK_COUNT)

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
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether the debug mode is turned on.
    #    '''
    #    return False

    @classmethod
    def getOutputFormat(cls, choices):
       '''
       The format of the history element with the output of the tool. Note
       that html output shows print statements, but that text-based output
       (e.g. bed) only shows text written to the galaxyFn file.In the latter
       case, all all print statements are redirected to the info field of the
       history item box.
       '''
       return cls.HISTORY_PROGRESS_SUFFIX
