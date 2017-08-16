import shutil

from gold.gsuite import GSuiteConstants
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool, HistElement


#from quick.util.debug import DebugUtil

# This is a template prototyping GUI that comes together with a corresponding
# web page.

class GSuiteExportToHistoryTool(GeneralGuiTool):
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PRIMARY, GSuiteConstants.UNKNOWN]
    GSUITE_ALLOWED_TRACK_TYPES = []

    GSUITE_OUTPUT_LOCATION = GSuiteConstants.LOCAL
    GSUITE_OUTPUT_FILE_FORMAT = ''
    GSUITE_OUTPUT_TRACK_TYPE = ''
    
    TRACK_SELECT_ALL = 'All tracks in GSuite'
    TRACK_SELECT_CHOOSE = 'Custom selection of tracks'
    PREVIEW_NO = 'No'
    PREVIEW_YES = 'Yes'
    OUTPUT_FORMAT_ORIGINAL = 'Original file format'
    OUTPUT_FORMAT_CONVERT = 'Converted file format...'

    NUM_PREVIEW_LINES = 15

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Export local tracks in GSuite to history"

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
        return [('Select a GSuite from history:','gsuite'),
                ('Show preview of track content:', 'showPreview'),
                ('Select track to preview:', 'previewSelect'),
                ('Preview of first ' + str(cls.NUM_PREVIEW_LINES) + ' lines of the selected track', 'preview'),
                ('Select which tracks to export:', 'trackSelect'),
                ('Tracks to export:', 'tracks'),
                ('Export tracks using:', 'changeFormat'),
                ('Select file format to convert to (for all tracks):', 'outputFormat') ]

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
        return GeneralGuiTool.getHistorySelectionElement('gsuite')
    
    @classmethod
    def getOptionsBoxShowPreview(cls, prevChoices):
        if prevChoices.gsuite:
            return [cls.PREVIEW_NO, cls.PREVIEW_YES]

    @classmethod
    def getOptionsBoxPreviewSelect(cls, prevChoices):
        if prevChoices.showPreview == cls.PREVIEW_YES:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            return [title for title in gSuite.allTrackTitles()]

    @classmethod
    def getOptionsBoxPreview(cls, prevChoices):
        if prevChoices.showPreview == cls.PREVIEW_YES:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            gSuiteTrack = gSuite.getTrackFromTitle(prevChoices.previewSelect)
            if not gSuiteTrack.path:
                return
            
            output = ''
            with open(gSuiteTrack.path) as f:
                for i in xrange(cls.NUM_PREVIEW_LINES):
                    line = f.readline()
                    if line:
                        output += line
                    else:
                        break
            
            return (output, cls.NUM_PREVIEW_LINES, True)

    @classmethod
    def getOptionsBoxTrackSelect(cls, prevChoices):
        if prevChoices.gsuite:
            return [cls.TRACK_SELECT_ALL, cls.TRACK_SELECT_CHOOSE]

    @classmethod
    def getOptionsBoxTracks(cls, prevChoices):
        if prevChoices.trackSelect == cls.TRACK_SELECT_CHOOSE:
            from collections import OrderedDict
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            return OrderedDict([(title, True) for title in gSuite.allTrackTitles()])

    @classmethod
    def getOptionsBoxChangeFormat(cls, prevChoices):
        if prevChoices.gsuite and \
            (prevChoices.trackSelect == cls.TRACK_SELECT_ALL or any(selected for title,selected in prevChoices.tracks.iteritems())):
                return [cls.OUTPUT_FORMAT_ORIGINAL, cls.OUTPUT_FORMAT_CONVERT]

    @classmethod
    def getOptionsBoxOutputFormat(cls, prevChoices):
        if prevChoices.changeFormat == cls.OUTPUT_FORMAT_CONVERT:
            try:
                from gold.origdata.GenomeElementSource import GenomeElementSource
                from gold.origdata.FileFormatComposer import findMatchingFileFormatComposers
                from gold.track.TrackFormat import TrackFormat

                gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                selectedTracks = cls._getSelectedTracks(prevChoices, gSuite)

                allGeSources = [GenomeElementSource(track.path, genome=track.genome, printWarnings=False, suffix=track.suffix)
                                for track in selectedTracks]
                matchingComposersForAllSelectedTracks = \
                    [findMatchingFileFormatComposers(TrackFormat.createInstanceFromGeSource(geSource)) for geSource in allGeSources]

                commonComposers = reduce(set.intersection, map(set, matchingComposersForAllSelectedTracks))
                return [composer.fileFormatName for composer in commonComposers]
            except:
                return []
            
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

    @classmethod
    def _getSelectedTracks(cls, choices, gSuite):
        if choices.trackSelect == cls.TRACK_SELECT_ALL:
            return gSuite.allTracks()
        else:
            return [gSuite.getTrackFromTitle(title) for title,selected in choices.tracks.iteritems() if selected]

    @classmethod
    def _getNewSuffixIfAny(cls, choices):
        if choices.changeFormat == cls.OUTPUT_FORMAT_CONVERT:
            from gold.origdata.FileFormatComposer import getComposerClsFromFileFormatName
            composerCls = getComposerClsFromFileFormatName(choices.outputFormat)
            return composerCls.getDefaultFileNameSuffix()
        else:
            return None

    @staticmethod
    def _getExportTrackTitleAndSuffix(gSuiteTrack, newSuffix):
        from gold.gsuite.GSuiteFunctions import getTitleWithSuffixReplaced
        if newSuffix:
            newSuffix = newSuffix.lower()
            return getTitleWithSuffixReplaced(gSuiteTrack.title, newSuffix), newSuffix
        else:
            return gSuiteTrack.title, (gSuiteTrack.suffix.lower() if gSuiteTrack.suffix else None)

    @classmethod
    def getExtraHistElements(cls, choices):
        if choices.gsuite:
            gSuite = getGSuiteFromGalaxyTN(choices.gsuite)

            newSuffix = cls._getNewSuffixIfAny(choices)

            return [HistElement(*cls._getExportTrackTitleAndSuffix(track, newSuffix))
                    for track in cls._getSelectedTracks(choices, gSuite)]

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

        inGSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        outGSuite = GSuite()
        
        newSuffix = cls._getNewSuffixIfAny(choices)

        for track in cls._getSelectedTracks(choices, inGSuite):
            title, suffix = cls._getExportTrackTitleAndSuffix(track, newSuffix)
            trackGalaxyFn = cls.extraGalaxyFn[title]

            if choices.changeFormat == cls.OUTPUT_FORMAT_CONVERT:
                from gold.origdata.FileFormatComposer import getComposerClsFromFileFormatName
                geSource = track.getGenomeElementSource(printWarnings=False)
                composerCls = getComposerClsFromFileFormatName(choices.outputFormat)
                composer = composerCls(geSource)
                composer.composeToFile(trackGalaxyFn)
            else:
                shutil.copy(track.path, trackGalaxyFn)
            
            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=trackGalaxyFn,
                                                suffix=suffix)
            gSuiteTrack = GSuiteTrack(uri,
                                      title=title,
                                      genome=track.genome,
                                      attributes=track.attributes)
            outGSuite.addTrack(gSuiteTrack)

        GSuiteComposer.composeToFile(outGSuite, galaxyFn)


    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        errorString = GeneralGuiTool._checkGSuiteFile(choices.gsuite)
        if errorString:
            return errorString
        
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        errorString = GeneralGuiTool._checkGSuiteRequirements \
            (gSuite,
             allowedLocations=GSuiteExportToHistoryTool.GSUITE_ALLOWED_LOCATIONS,
             allowedFileFormats=GSuiteExportToHistoryTool.GSUITE_ALLOWED_FILE_FORMATS,
             allowedTrackTypes=GSuiteExportToHistoryTool.GSUITE_ALLOWED_TRACK_TYPES)
        
        if errorString:
            return errorString

        if choices.changeFormat == cls.OUTPUT_FORMAT_CONVERT and choices.outputFormat is None:
            return 'There are no common supported file formats that all selected tracks can be converted to.'

    @classmethod
    def getOutputName(cls, choices):
        from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
        return getGSuiteHistoryOutputName('primary', ', tracks exported', choices.gsuite)

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
        core.smallHeader('General')
        core.paragraph('This tool exports selected tracks in a local GSuite file to the Galaxy history. '
                       'The tool creates a new GSuite file with points to the exported tracks. '
                       ' In addition, the tool can provide a preview of the the beginning of any track '
                       'directly from the tool interface.')
        core.divider()
        core.smallHeader('Conversion')
        core.paragraph('As part of the export process, the tracks can be converted into another file format. '
                       'The list of file formats are dynamically created based upon the selected tracks. The list '
                       'contains only file formats that allow conversion from all the selected tracks.')

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
                                      outputLocation=cls.GSUITE_OUTPUT_LOCATION,
                                      outputFileFormat=cls.GSUITE_OUTPUT_FILE_FORMAT,
                                      outputTrackType=cls.GSUITE_OUTPUT_TRACK_TYPE)

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
        return 'gsuite'
