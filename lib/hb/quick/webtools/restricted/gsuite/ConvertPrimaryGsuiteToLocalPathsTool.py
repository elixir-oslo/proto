from gold.gsuite import GSuiteConstants
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class ConvertPrimaryGsuiteToLocalPathsTool(GeneralGuiTool):
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PRIMARY]
    GSUITE_ALLOWED_TRACK_TYPES = []

    GSUITE_OUTPUT_LOCATION = GSuiteConstants.LOCAL
    GSUITE_OUTPUT_FILE_FORMAT = GSuiteConstants.PRIMARY
    GSUITE_OUTPUT_TRACK_TYPE = ''

    @classmethod
    def getToolName(cls):
        return "Convert primary GSuite with Galaxy URI to GSuite with local paths"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select a primary GSuite from history', 'gsuite')]

    # @classmethod
    # def getInputBoxOrder(cls):
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     return None

    @classmethod
    def getOptionsBoxGsuite(cls):
        return '__history__', 'gsuite'

    # @classmethod
    # def getInfoForOptionsBoxKey(cls, prevChoices):
    #     return None
    #
    # @classmethod
    # def getDemoSelections(cls):
    #     return ['testChoice1', '..']
    #
    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     return None

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        from quick.util.CommonFunctions import getFileSuffix
        import gold.gsuite.GSuiteComposer as GSuiteComposer
        from gold.gsuite.GSuite import GSuite
        from gold.gsuite.GSuiteTrack import registerGSuiteTrackClass, GSuiteTrack, FileGSuiteTrack

        registerGSuiteTrackClass(FileGSuiteTrack)

        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        outGSuite = GSuite()

        for track in gSuite.allTracks():
            path = track.path
            suffix = track.suffix if track.suffix != getFileSuffix(path) else ''
            uri = FileGSuiteTrack.generateURI(path=path, suffix=suffix)

            newTrack = GSuiteTrack(uri, title=track.title, trackType=track.trackType,
                                   genome=track.genome, attributes=track.attributes)

            outGSuite.addTrack(newTrack)

        GSuiteComposer.composeToFile(outGSuite, galaxyFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        errorString = GeneralGuiTool._checkGSuiteFile(choices.gsuite)
        if errorString:
            return errorString

        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        errorString = GeneralGuiTool._checkGSuiteRequirements(
            gSuite,
            allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
            allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
            allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES
        )

        if errorString:
            return errorString

    # @classmethod
    # def getSubToolClasses(cls):
    #     return None

    @classmethod
    def isPublic(cls):
        return False

    # @classmethod
    # def isRedirectTool(cls):
    #     return False
    #
    # @classmethod
    # def getRedirectURL(cls, choices):
    #     return ''
    #
    # @classmethod
    # def isHistoryTool(cls):
    #     return True
    #
    # @classmethod
    # def isBatchTool(cls):
    #     return cls.isHistoryTool()
    #
    # @classmethod
    # def isDynamic(cls):
    #     return True
    #
    # @classmethod
    # def getResetBoxes(cls):
    #     return []
    #
    @classmethod
    def getToolDescription(cls):
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()
        core.paragraph('Converts a GSuite file with primary and locally stored tracks to an equal '
                       'GSuite file with the absolute paths from local storage.')

        core.divider()
        core.paragraph(str(HtmlCore().highlight('NOTE: SHOULD NOT BE MADE PUBLIC FOR SECURITY '
                                            'REASONS.')))

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
                                      outputLocation=cls.GSUITE_OUTPUT_LOCATION,
                                      outputFileFormat=cls.GSUITE_OUTPUT_FILE_FORMAT,
                                      outputTrackType=cls.GSUITE_OUTPUT_TRACK_TYPE)

        return str(core)
    #
    # @classmethod
    # def getToolIllustration(cls):
    #     return None
    #
    # @classmethod
    # def getFullExampleURL(cls):
    #     return None
    #
    # @classmethod
    # def isDebugMode(cls):
    #     return False

    @classmethod
    def getOutputFormat(cls, choices):
        return 'gsuite'

    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
