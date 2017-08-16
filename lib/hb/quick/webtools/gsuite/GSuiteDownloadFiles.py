from gold.gsuite.GSuiteConstants import REMOTE, LOCAL, UNKNOWN, PRIMARY, PREPROCESSED, \
                                        GSUITE_SUFFIX, GSUITE_STORAGE_SUFFIX
from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin

class GSuiteDownloadFiles(GeneralGuiTool, GenomeMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['history']
    ALLOW_GENOME_OVERRIDE = True
    ALLOW_MULTIPLE_GENOMES = True

    GSUITE_ALLOWED_LOCATIONS = [REMOTE]

    GSUITE_OUTPUT_LOCATION = LOCAL
    GSUITE_OUTPUT_FILE_FORMAT = ', '.join([UNKNOWN, PRIMARY, PREPROCESSED])
    GSUITE_OUTPUT_TRACK_TYPE = 'any, dependent on file format'

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Convert GSuite tracks from remote to primary (Download the tracks to the server)"

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
        return [('Select GSuite file from history:', 'history'),
                ('Preprocess fetched tracks?', 'preProcess')] + \
                cls.getInputBoxNamesForGenomeSelection()

    @staticmethod
    def getOptionsBoxHistory():
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
        return '__history__','gsuite'

    @staticmethod
    def getOptionsBoxPreProcess(prevChoices):
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        if prevChoices.history:
            return ['No', 'Yes']

    @classmethod
    def _allowUnknownGenome(cls, prevChoices):
        return prevChoices.preProcess != 'Yes'

    #@staticmethod
    #def getOptionsBoxSelectGenome(prevChoices):
    #    if prevChoices.history:
    #        try:
    #            from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
    #            gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
    #        except:
    #            return None
    #
    #        noMsg = 'No'
    #        if gSuite.genome == UNKNOWN:
    #            yesMsg = 'Yes (no genome specified in GSuite)'
    #        else:
    #            yesMsg = 'Yes (override genome specified in GSuite: %s)' % gSuite.genome
    #
    #        if prevChoices.preProcess == 'Yes':
    #            if gSuite.genome == UNKNOWN:
    #                return [yesMsg]
    #            else:
    #                return [noMsg, yesMsg]
    #        else:
    #            return [noMsg, yesMsg]

    #@staticmethod
    #def getOptionsBoxGenome(prevChoices):
    #    if prevChoices.selectGenome.startswith('Yes'):
    #        return '__genome__'

    #@staticmethod
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @classmethod
    def getExtraHistElements(cls, choices):
        from quick.webtools.GeneralGuiTool import HistElement
        fileList = [HistElement(getGSuiteHistoryOutputName('nodownload', datasetInfo=choices.history),
                                GSUITE_SUFFIX)]
        fileList += [HistElement(getGSuiteHistoryOutputName('primary', datasetInfo=choices.history),
                                GSUITE_SUFFIX)]
        if choices.preProcess == 'Yes':
            fileList += [HistElement(getGSuiteHistoryOutputName('nopreprocessed', datasetInfo=choices.history),
                                     GSUITE_SUFFIX)]
            fileList += [HistElement(getGSuiteHistoryOutputName('preprocessed', datasetInfo=choices.history),
                                     GSUITE_SUFFIX)]
        fileList += [HistElement(getGSuiteHistoryOutputName('storage', datasetInfo=choices.history),
                                 GSUITE_STORAGE_SUFFIX, hidden=True)]

        # if choices.history:
            #from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
            #gSuite = getGSuiteFromGalaxyTN(choices.history)
            #
            #for track in gSuite.allTracks():
            #    from gold.gsuite.GSuiteDownloader import getTitleAndSuffixWithCompressionSuffixesRemoved
            #    title, suffix = getTitleAndSuffixWithCompressionSuffixesRemoved(track)
            #    fileList.append( HistElement(title, suffix, hidden=True) )


        return fileList

    @classmethod
    def execute(cls,choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        from gold.gsuite.GSuitePreprocessor import GSuitePreprocessor
        import gold.gsuite.GSuiteComposer as GSuiteComposer
        from quick.gsuite.GSuiteHbIntegration import \
            writeGSuiteHiddenTrackStorageHtml
        from quick.extra.ProgressViewer import ProgressViewer
        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN

        inGSuite = getGSuiteFromGalaxyTN(choices.history)
        trackCount = inGSuite.numTracks()

        progressViewer = ProgressViewer(
             [('Download tracks', trackCount)] +
             ([('Preprocess tracks', trackCount)] if choices.preProcess == 'Yes' else []),
             galaxyFn)

        #from gold.gsuite.GSuiteDownloader import GSuiteMultipleGalaxyFnDownloader
        #gSuiteDownloader = GSuiteMultipleGalaxyFnDownloader()
        #outGSuite, errorGSuite = \
        #    gSuiteDownloader.visitAllGSuiteTracksAndReturnOutputAndErrorGSuites(inGSuite, progressViewer, cls.extraGalaxyFn)

        from gold.gsuite.GSuiteDownloader import GSuiteSingleGalaxyFnDownloader
        gSuiteDownloader = GSuiteSingleGalaxyFnDownloader()
        hiddenStorageFn = cls.extraGalaxyFn\
            [getGSuiteHistoryOutputName('storage', datasetInfo=choices.history)]
        outGSuite, errorGSuite = \
            gSuiteDownloader.visitAllGSuiteTracksAndReturnOutputAndErrorGSuites \
                (inGSuite, progressViewer, hiddenStorageFn, [])
        writeGSuiteHiddenTrackStorageHtml(hiddenStorageFn)

        #outGSuite, errorGSuite = \
        #    inGSuite.downloadAllRemoteTracksAsMultipleDatasetsAndReturnOutputAndErrorGSuites(cls.extraGalaxyFn, progressViewer)

        #outGSuite, errorGSuite = \
        #    inGSuite.downloadAllRemoteTracksAsSingleDatasetAndReturnOutputAndErrorGSuites(galaxyFn, ['cell', 'title'], progressViewer=progressViewer)

        errorFn = cls.extraGalaxyFn\
            [getGSuiteHistoryOutputName('nodownload', datasetInfo=choices.history)]
        GSuiteComposer.composeToFile(errorGSuite, errorFn)

        outGSuite.setGenomeOfAllTracks(choices.genome)
        downloadFn = cls.extraGalaxyFn\
            [getGSuiteHistoryOutputName('primary', datasetInfo=choices.history)]
        GSuiteComposer.composeToFile(outGSuite, downloadFn)


        if choices.preProcess == 'Yes':
            progressViewer.updateProgressObjectElementCount('Preprocess tracks', outGSuite.numTracks())

            gSuitePreprocessor = GSuitePreprocessor()
            outGSuite, errorGSuite = gSuitePreprocessor.visitAllGSuiteTracksAndReturnOutputAndErrorGSuites\
                                                        (outGSuite, progressViewer)

            #outGSuite, errorGSuite = outGSuite.preProcessAllLocalTracksAndReturnOutputAndErrorGSuites(progressViewer)

            noPreprocessedFn = cls.extraGalaxyFn\
                [getGSuiteHistoryOutputName('nopreprocessed', datasetInfo=choices.history)]
            GSuiteComposer.composeToFile(errorGSuite, noPreprocessedFn)

            preprocessedFn = cls.extraGalaxyFn\
                [getGSuiteHistoryOutputName('preprocessed', datasetInfo=choices.history)]
            GSuiteComposer.composeToFile(outGSuite, preprocessedFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.

        '''
        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN

        errorString = GeneralGuiTool._checkGSuiteFile(choices.history)
        if errorString:
            return errorString

        gSuite = getGSuiteFromGalaxyTN(choices.history)

        errorString = cls._validateGenome(choices)
        if errorString:
            return errorString

        errorString = GeneralGuiTool._checkGSuiteRequirements(gSuite,
            allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS)
        if errorString:
            return errorString

        errorString = GeneralGuiTool._checkGSuiteTrackListSize(gSuite, minSize=1)
        if errorString:
            return errorString

    @classmethod
    def getOutputName(cls, choices):
        return getGSuiteHistoryOutputName('progress', datasetInfo=choices.history)

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
        core.paragraph('This tool takes a GSuite file as an input, and downloads the '
                       'remote datasets which are referred to in this file onto the HyperBrowser '
                       'server, returning a GSuite file referencing these local datasets. '
                       'The datasets will be downloaded into hidden history elements, which can be '
                       'shown using the menu option "Show hidden datasets" in the history "Options" menu.')
        core.divider()
        core.paragraph('The tool supports the following protocols for downloading:')
        core.unorderedList(['Rsync', 'FTP', 'HTTP', 'HTTPS'])
        core.paragraph('Also,  gzip files ("*.gz) are automatically decompressed.')

        cls._addGSuiteFileDescription(core,
                                      outputLocation=cls.GSUITE_OUTPUT_LOCATION,
                                      outputFileFormat=cls.GSUITE_OUTPUT_FILE_FORMAT,
                                      outputTrackType=cls.GSUITE_OUTPUT_TRACK_TYPE,
                                      errorFile=True)

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
    # @staticmethod
    # def getFullExampleURL():
    #     return 'https://hyperbrowser.uio.no/nar/u/hb-superuser/p/fetch-remote-gsuite-datasets---user-guide'

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
    @classmethod
    def getOutputFormat(cls,choices):
        return 'customhtml'
