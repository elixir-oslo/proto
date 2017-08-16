from gold.gsuite import GSuiteConstants
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util.TrackReportCommon import generatePilotPageTwoParagraphs
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.BasicModeAnalysisInfoMixin import BasicModeAnalysisInfoMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


# This is a template prototyping GUI that comes together with a corresponding
# web page.

#Unused
class PilotPageOverlapBetweenTracksTool(GeneralGuiTool, UserBinMixin,
                                        BasicModeAnalysisInfoMixin, GenomeMixin):
    '''
        https://docs.google.com/document/d/1c03750V_xDXfdTYrHOoAZPIjVihtOUpfXlWQm7dO95Q/edit
        
        TOOL 2 - Overlap between tracks:
        On average, around 15%  (~1.4Mbps) of the basepairs of a single track are unique to that track 
        (not present in any of the other X tracks). Around 11% (1.0Mbps) are shared with at least half (X) 
        of the other tracks, while around 0.5% (60Kbps) is shared with all the other tracks. 
        Details are available in the form of a plot showing the percentage of an average track shared 
        with a varying numbers of other tracks, as well as plots showing the same for an individual track. 
        There is also available a plot showing how many base pairs are covered by 1, 2, 3 and up to X of 
        the tracks
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
        return "Overlap between tracks"

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
               [('Select GSuite', 'gsuite')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               cls.getInputBoxNamesForUserBinSelection()


    @staticmethod
    def getOptionsBoxGsuite(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')


    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        if gSuite.genome != choices.genome:
            gSuite.setGenomeOfAllTracks(choices.genome)
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        paragraphs = generatePilotPageTwoParagraphs(gSuite, galaxyFn, regSpec=regSpec, binSpec=binSpec)

        core = HtmlCore()
        core.begin()
        core.header('Overlap between tracks')
        for prg in paragraphs:
            core.paragraph(prg)
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
        
        errorString = cls.validateUserBins(choices)
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
