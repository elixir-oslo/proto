from gold.gsuite import GSuiteConstants
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util.TrackReportCommon import generatePilotPageOneParagraphs
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class PilotPageBasicOverviewOfTracksInGSuiteTool(GeneralGuiTool, UserBinMixin,
                                                 GenomeMixin):
    
    '''
        https://docs.google.com/document/d/1c03750V_xDXfdTYrHOoAZPIjVihtOUpfXlWQm7dO95Q/edit
        
        TOOL1 - basic overview of tracks in collection:
            The tracks in the collection contain on average X elements (median: Y elements), 
            ranging from Z to W between the tracks. The tracks cover on average X Mbps (median: Y Mbps), 
            ranging from X to Y Mbps between experiments. This amounts to on average covering X% of the genome, ranging from Y% to Z% between tracks. 
            The average coverage (across tracks) is lowest in chrA (B%) and highest in chrC (D%). 
            Detailed numbers per track can be inspected in a table of coverage proportion per track per chromosome, 
            and in a table of element count per track per chromosome.
            
            In total, the regions of the X tracks encompass Y bps (plain sum of covered bps per track), 
            representing Z unique bps of the genome (union of coverage per track).
            
            The segments of the tracks are on average X bps long (median: Y bps), ranging from average length of X bps to Y bps between tracks.
            
            On average, the tracks show a strong local clustering tendency as measured by a Ripleys K  of X at scale 1Kbp and Y at scale 1Mbp 
            (on average across tracks). Between tracks, these numbers range from X to Y at scale 1Kbp and from Z to W at scale 1Mbp.
            
            On average, X% of the tracks fall within exonic regions, ranging from Y% to Z% between tracks. 
            This corresponds to an enrichment factor of X, ranging from Y to Z between tracks. 
            Further details can be inspected in a table showing distribution of each track between exons, introns and intergenic regions.
    '''
    WHAT_GENOME_IS_USED_FOR = 'the input GSuite'
    ALLOW_UNKNOWN_GENOME = False
    ALLOW_GENOME_OVERRIDE = False

    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS,
                                  GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS]

    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Summary statistics per track in a GSuite"

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
                ('', 'basicQuestionId'),
                ('Select GSuite', 'gsuite')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               cls.getInputBoxNamesForUserBinSelection()

    @staticmethod
    def getOptionsBoxIsBasic():
        return False

    @staticmethod
    def getOptionsBoxBasicQuestionId(prevChoices):
        return '__hidden__', None

    @staticmethod
    def getOptionsBoxGsuite(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        if gSuite.genome != choices.genome:
            gSuite.setGenomeOfAllTracks(choices.genome)
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        paragraphs = generatePilotPageOneParagraphs(gSuite, galaxyFn, regSpec=regSpec, binSpec=binSpec, username=username)

        core = HtmlCore()
        core.begin()
        core.divBegin(divId='results-page')
        core.divBegin(divClass='results-section')
        core.header('Basic overview of tracks in collection')
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

#     @staticmethod
#     def isDebugMode():
#         '''
#         Specifies whether the debug mode is turned on.
#         '''
#         return True
