from gold.gsuite import GSuiteConstants
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util.TrackReportCommon import generatePilotPageFiveParagraphs
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class PilotPageClusteringInTracksTool(GeneralGuiTool, GenomeMixin):#(UserBinMixin):
    '''
        https://docs.google.com/document/d/1c03750V_xDXfdTYrHOoAZPIjVihtOUpfXlWQm7dO95Q/edit
        
       TOOL 5 - Clustering of elements:
        On average, the tracks show a strong clustering tendency as measured by a Ripleys K  of X at scale 1Kbp and weak clustering tendency 
        measured by Y at scale 1Mbp (on average across tracks). 
        Between tracks, these numbers range from X to Y at scale 1Kbp and from Z to W at scale 1Mbp.

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
        return "Tendency of track elements to clump together along the genome (Ripleys K)"

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
        return [('Select GSuite', 'gsuite')] + \
               GenomeMixin.getInputBoxNamesForGenomeSelection()
        
    # + UserBinMixin.getInputBoxNamesForUserBinSelection()
    
    
    @staticmethod
    def getOptionsBoxGsuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')


    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        if gSuite.genome != choices.genome:
            gSuite.setGenomeOfAllTracks(choices.genome)
#         regSpec, binSpec = UserBinSelector.getRegsAndBinsSpec(choices)
        paragraphs = generatePilotPageFiveParagraphs(gSuite, galaxyFn)

        core = HtmlCore()
        core.begin()
        core.divBegin(divId='results-page')
        core.divBegin(divClass='results-section')
        core.header('Clustering of track elements')
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
#         errorString = cls.validateUserBins(choices)
#         if errorString:
#             return errorString
        
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

