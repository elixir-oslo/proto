from collections import OrderedDict

from gold.gsuite import GSuiteConstants
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util.TrackReportCommon import generatePilotPageOneParagraphs,\
    generatePilotPageTwoParagraphs, generatePilotPageThreeParagraphs,\
    generatePilotPageFiveParagraphs
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class PilotPageCombinedOverviewOfTracksTool(GeneralGuiTool, UserBinMixin,
                                            GenomeMixin):
    '''
        https://docs.google.com/document/d/1c03750V_xDXfdTYrHOoAZPIjVihtOUpfXlWQm7dO95Q/edit
        
        This tool combines all pilot pages into one.
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
        return "Combined overview of track in GSuite"

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
                ('Select GSuite', 'gsuite')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               cls.getInputBoxNamesForUserBinSelection()

    @staticmethod
    def getOptionsBoxIsBasic():
        return False

    @staticmethod
    def getOptionsBoxGsuite(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        if gSuite.genome != choices.genome:
            gSuite.setGenomeOfAllTracks(choices.genome)
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        paragraphs = OrderedDict()
        paragraphs['Basic overview of tracks in collection'] = generatePilotPageOneParagraphs(gSuite, galaxyFn, regSpec=regSpec, binSpec=binSpec, username=username)
        paragraphs['Overlap between tracks'] = generatePilotPageTwoParagraphs(gSuite, galaxyFn, regSpec=regSpec, binSpec=binSpec)
        paragraphs['Similarity and uniqueness of tracks'] = generatePilotPageThreeParagraphs(gSuite, galaxyFn, regSpec=regSpec, binSpec=binSpec)
        paragraphs['Clustering of tracks'] = generatePilotPageFiveParagraphs(gSuite, galaxyFn)
        
        
        core = HtmlCore()
        core.begin()
        core.divBegin(divId='results-page', divClass='trackbook_main')
        for hdr, prgList in paragraphs.iteritems():
            core.divBegin(divClass='trackbook_section')
            core.divBegin(divClass='results-section')
            core.header(hdr)    
            for prg in prgList:
                core.paragraph(prg)
            core.divEnd()
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
