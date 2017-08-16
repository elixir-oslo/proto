import gold.gsuite.GSuiteConstants as GSuiteConstants
from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class PreprocessGSuiteTracksTool(GeneralGuiTool, GenomeMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['history']
    ALLOW_UNKNOWN_GENOME = False
    ALLOW_GENOME_OVERRIDE = True
    ALLOW_MULTIPLE_GENOMES = True
    WHAT_GENOME_IS_USED_FOR = 'preprocessing'

    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PRIMARY]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]

    GSUITE_OUTPUT_LOCATION = GSuiteConstants.LOCAL
    GSUITE_OUTPUT_FILE_FORMAT = GSuiteConstants.PREPROCESSED

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return """Convert GSuite tracks from primary to preprocessed
        (Preprocess tracks to prepare them for use in the analysis tools)"""

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
        return [('Select GSuite file from history:', 'history')] +\
               cls.getInputBoxNamesForGenomeSelection()

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
    def getOptionsBoxHistory(): # Alternatively: getOptionsBox1()
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

    #@staticmethod
    #def getOptionsBoxSelectGenome(prevChoices): # Alternatively: getOptionsBox2()
    #    '''
    #    See getOptionsBoxFirstKey().
    #
    #    prevChoices is a namedtuple of selections made by the user in the
    #    previous input boxes (that is, a namedtuple containing only one element
    #    in this case). The elements can accessed either by index, e.g.
    #    prevChoices[0] for the result of input box 1, or by key, e.g.
    #    prevChoices.key (case 2).
    #    '''
    #    if prevChoices.history:
    #        try:
    #            from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
    #            gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
    #            if gSuite.genome == GSuiteConstants.UNKNOWN:
    #                return ['Yes']
    #        except:
    #            pass
    #
    #    return ['No', 'Yes']
    #
    #@staticmethod
    #def getOptionsBoxGenome(prevChoices):
    #    if prevChoices.selectGenome == 'Yes':
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
        return [HistElement(getGSuiteHistoryOutputName(
                    'nopreprocessed', datasetInfo=choices.history), 'gsuite'),
                HistElement(getGSuiteHistoryOutputName(
                    'preprocessed', datasetInfo=choices.history), 'gsuite')]

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
        from gold.gsuite.GSuitePreprocessor import GSuitePreprocessor
        from quick.extra.ProgressViewer import ProgressViewer
        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN

        inGSuite = getGSuiteFromGalaxyTN(choices.history)

        if choices.genome != inGSuite.genome:
            inGSuite.setGenomeOfAllTracks(choices.genome)

        progressViewer = ProgressViewer(
            [('Preprocess tracks', inGSuite.numTracks())], galaxyFn)

        gSuitePreprocessor = GSuitePreprocessor()
        outGSuite, errorGSuite = gSuitePreprocessor.visitAllGSuiteTracksAndReturnOutputAndErrorGSuites\
                                                    (inGSuite, progressViewer)

        #outGSuite, errorGSuite = inGSuite.preProcessAllLocalTracksAndReturnOutputAndErrorGSuites()

        nopreprocFn = cls.extraGalaxyFn[getGSuiteHistoryOutputName(
            'nopreprocessed', datasetInfo=choices.history)]
        GSuiteComposer.composeToFile(errorGSuite, nopreprocFn)

        preprocFn = cls.extraGalaxyFn[getGSuiteHistoryOutputName(
            'preprocessed', datasetInfo=choices.history)]
        GSuiteComposer.composeToFile(outGSuite, preprocFn)


    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.history)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite = getGSuiteFromGalaxyTN(choices.history)

        if gSuite.location == GSuiteConstants.REMOTE:
            return 'All tracks in GSuite file are remote. ' \
                   'Please download the tracks of the GSuite file before preprocessing.'

        errorStr = cls._validateGenome(choices)
        if errorStr:
            return errorStr

        errorStr = cls._checkGSuiteRequirements(
            gSuite,
            allowedFileFormats = cls.GSUITE_ALLOWED_FILE_FORMATS,
            allowedLocations = cls.GSUITE_ALLOWED_LOCATIONS)
        
        if errorStr:
            return errorStr

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

    @staticmethod
    def getResetBoxes():
        '''
        Specifies a list of input boxes which resets the subsequent stored
        choices previously made. The input boxes are specified by index
        (starting with 1) or by key.
        '''
        return ['history']

    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore
        from gold.origdata.GenomeElementSource import getAllGenomeElementSourceClasses

        core = HtmlCore()
        core.paragraph('This tool is used to preprocess the textual track files referred to by '
                       'a GSuite file into a indexed, binary format that is needed for '
                       'efficient analysis by the HyperBrowser analysis tools.')
        core.divider()
        core.smallHeader('Genome')
        core.paragraph('Preprocessing tracks requires that the specific genome build is selected. '
                       'If a genome build is defined within the GSuite file, it can still be overridden '
                       'by the user if another build is selected. If the GSuite file contains no '
                       'genome, the selection of a genome build is required.')
        core.divider()
        core.smallHeader('Supported file types')
        core.paragraph('The HyperBrowser preprocessor supports the following file types (name: file suffix):')

        geSourceClsList = getAllGenomeElementSourceClasses(forPreProcessor=True)
        core.unorderedList(['%s: "%s"' % (geSourceCls.FILE_FORMAT_NAME, ', '.join(geSourceCls.FILE_SUFFIXES))
                            for geSourceCls in geSourceClsList] + ['broadPeak: ".broadpeak"', 'narrowPeak: ".narrowpeak"'])

        cls._addGSuiteFileDescription(core,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      outputLocation=cls.GSUITE_OUTPUT_LOCATION,
                                      outputFileFormat=cls.GSUITE_OUTPUT_FILE_FORMAT,
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
    #     return 'u/hb-superuser/p/compile-gsuite-from-history-elements--preprocess-tracks-in-gsuite-for-analysis---example'
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
        return 'customhtml'
