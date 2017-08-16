from gold.gsuite import GSuiteConstants
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import MultiGeneralGuiTool, GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin

# This is a template prototyping GUI that comes together with a corresponding
# web page.

snps = [[] for chromosome in range(0,25)]
peaks = [[] for chromosome in range(0,25)]
motif = None

BINDING_PROB_TRESHOLD = 0.5
BINDING_A_PRIORI_PROB = 0.01


class TfBindingDisruption(GeneralGuiTool, UserBinMixin, GenomeMixin):
    ALLOW_UNKNOWN_GENOME = False
    ALLOW_GENOME_OVERRIDE = False
    ALLOW_MULTIPLE_GENOMES = False
    WHAT_GENOME_IS_USED_FOR = 'the analysis'  # Other common possibility: 'the analysis'

    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_FILE_TYPES = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Scan for loss or gain of TF function due to point mutations"

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

        return [('', 'basicQuestionId'),
                ('Point mutation data set','snp'),
                ('Transcription factors (GSuite file from history)', 'gsuite')] +\
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
    def getOptionsBoxBasicQuestionId():
        return '__hidden__', None

    # @staticmethod
    # def getOptionsBoxGenome(): # Alternatively: getOptionsBox1()
    #     return '__genome__'

    @staticmethod
    def getOptionsBoxSnp(prevChoices): # Alternatively: getOptionsBox1()
         # if prevChoices.genome or True:
        #return ('__history__', 'category.bed', 'bed')
        from gold.application.DataTypes import getSupportedFileSuffixesForPointsAndSegments #for example
        return ('__history__',) + tuple(getSupportedFileSuffixesForPointsAndSegments())
        #return '__history__', getSupportedFileSuffixesForPointsAndSegments()

    @staticmethod
    def getOptionsBoxGsuite(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return ('__history__',)

    @staticmethod
    def getOptionsBoxMotif(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return ('__history__',)

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
        """
        print 'Some debug:'
        initAnalysis(choices)
        findMotifBindings()
        output()
        """
        import quick.webtools.article.MutationAffectingGeneRegulation as m
        analysis = m.MutationAffectingGeneRegulation(choices)
        html = analysis.presentResults()

        print str(html)
        #m.run()

    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        errorString = cls._checkHistoryTrack(choices, 'snp', choices.genome)
        if errorString:
            return errorString

        from quick.application.ExternalTrackManager import ExternalTrackManager
        fileName = choices.snp
        if fileName != None and fileName != "":
            fName = ExternalTrackManager.extractFnFromGalaxyTN(fileName)
            suffix = ExternalTrackManager.extractFileSuffixFromGalaxyTN(fileName)
            from gold.origdata.GenomeElementSource import GenomeElementSource
            geSource = GenomeElementSource(fName, suffix=suffix)


            # Hacky way to check validity:
            # Check for errors when reading first column
            # Probably more correct ways to do this?
            try:
                for ge in geSource:
                    chr = ge.chr
                    start = ge.mutated_from_allele
                    from_allele = ge.mutated_to_allele
                    to_allele = ge.mutated_to_allele
                    break
            except:
                return "Invalid SNP data file. The SNP data file should as a minimum contain the following columns:" + \
                        " seqid, start, end, mutated_from_allele, mutated_to_allele"

        errorString = cls._checkGSuiteFile(choices.gsuite)
        if errorString:
            return errorString

        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        errorString = cls._checkGSuiteRequirements(
            gSuite,
            allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
            allowedFileFormats=cls.GSUITE_ALLOWED_FILE_TYPES,
            allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES)

        if errorString:
            return errorString

        errorString = cls._validateGenome(choices.genome)
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
