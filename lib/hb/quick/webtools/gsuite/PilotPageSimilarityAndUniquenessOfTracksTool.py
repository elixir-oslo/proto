from gold.gsuite import GSuiteConstants
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util.TrackReportCommon import generatePilotPageThreeParagraphs, generatePilotPageTwoParagraphs
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.BasicModeAnalysisInfoMixin import BasicModeAnalysisInfoMixin
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class PilotPageSimilarityAndUniquenessOfTracksTool\
            (GeneralGuiTool, UserBinMixin, BasicModeAnalysisInfoMixin,
             GenomeMixin, DebugMixin):
    '''
        https://docs.google.com/document/d/1c03750V_xDXfdTYrHOoAZPIjVihtOUpfXlWQm7dO95Q/edit
        
        TOOL 3 - similarity and uniqueness of tracks:
        Out of the **X** tracks, the track **gm12878** is the one that shows the highest degree of 
        covering locations covered by the remaining tracks 
        (being most like a superset of all other experiments). 
        The track **HepG1** is the one covering the least locations unique to this dataset 
        (not covered by other tracks). The track **CD4+** is the most typical track, 
        i.e. the one showing the strongest preference for locating to positions covered by other tracks 
        in the collection.

    '''

    WHAT_GENOME_IS_USED_FOR = 'the input GSuite'
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
        return "Similarity and uniqueness of tracks"

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
        return cls.getInputBoxNamesForAnalysisInfo() + \
               [('Basic user mode', 'isBasic'),
                ('', 'basicQuestionId'),
                ('Select GSuite', 'gsuite')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               cls.getInputBoxNamesForUserBinSelection() + \
               cls.getInputBoxNamesForDebug()

    @staticmethod
    def getOptionsBoxIsBasic(prevChoices):
        return False

    @staticmethod
    def getOptionsBoxBasicQuestionId(prevChoices):
        return '__hidden__', None
    
    @staticmethod
    def getOptionsBoxGsuite(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        
        cls._setDebugModeIfSelected(choices)
        
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        if gSuite.genome != choices.genome:
            gSuite.setGenomeOfAllTracks(choices.genome)
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        paragraphs = []
        paragraphs += generatePilotPageTwoParagraphs(gSuite, galaxyFn, regSpec=regSpec, binSpec=binSpec)
        paragraphs += generatePilotPageThreeParagraphs(gSuite, galaxyFn, regSpec=regSpec, binSpec=binSpec)

        core = HtmlCore()
        core.begin()
        core.divBegin(divId='results-page')
        core.divBegin(divClass='results-section')
        core.header('Similarity and uniqueness of tracks')
        for prg in paragraphs:
            core.paragraph(prg)
        core.divEnd()
        core.divEnd()
        core.end()
         
        print core

    @classmethod
    def validateAndReturnErrors(cls, choices):
        errMessage = GeneralGuiTool._checkGSuiteFile(choices.gsuite)
        if errMessage:
            return errMessage
        
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        errorString = GeneralGuiTool._checkGSuiteRequirements \
            (gSuite,
             cls.GSUITE_ALLOWED_FILE_FORMATS,
             cls.GSUITE_ALLOWED_LOCATIONS,
             cls.GSUITE_ALLOWED_TRACK_TYPES,
             cls.GSUITE_DISALLOWED_GENOMES)
        
        if errorString:
            return errorString
        
        errorStr = cls._validateGenome(choices)
        if errorStr:
            return errorStr
        
        errorString = cls.validateUserBins(choices)
        if errorString:
            return errorString

        errorString = cls._checkGSuiteTrackListSize(gSuite=gSuite, minSize=2)
        if errorString:
            return errorString
        
    @staticmethod
    def getOutputFormat(choices=None):
        return 'customhtml'
    
    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True

    @staticmethod
    def isDebugMode():
        '''
        Specifies whether debug messages are printed.
        '''
        return False
