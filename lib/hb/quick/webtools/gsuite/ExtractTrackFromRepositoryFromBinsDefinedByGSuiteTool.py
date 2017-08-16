from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util.CommonFunctions import ensurePathExists
from quick.webtools.GeneralGuiTool import GeneralGuiTool

# This is a template prototyping GUI that comes together with a corresponding
# web page.


class ExtractTrackFromRepositoryFromBinsDefinedByGSuiteTool(GeneralGuiTool):

    @staticmethod
    def getToolName():
        return 'Extract tracks from repository in regions defined by GSute tracks'

    @classmethod
    def getInputBoxNames(cls):
        return [
            ('Select gsuite', 'gsuite')] + \
            [('Select genome', 'genome')] + \
            [('Select basis track', 'basisTrack'),
             ('Select extraction format', 'extFormatLbl')]

    @staticmethod
    def getOptionsBoxGsuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxGenome(prevChoices):
        return '__genome__'

    @staticmethod
    def getOptionsBoxBasisTrack(prevChoices):
        if prevChoices.gsuite and prevChoices.genome:
            # return GeneralGuiTool.getHistorySelectionElement()
            return '__track__'

    @staticmethod
    def getOptionsBoxExtFormatLbl(prevChoices):
        if prevChoices.genome and prevChoices.basisTrack:
            extrOpts = GalaxyInterface.getTrackExtractionOptions(
                prevChoices.genome, prevChoices.basisTrack.split(':')
            )
            return [x[0] for x in extrOpts if extrOpts]

    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     if choices.gsuite and choices.basisTrack:
    #         extractionOptions = dict(
    #             GalaxyInterface.getTrackExtractionOptions(choices.genome, choices.basisTrack.split(':')))
    #         extractionFormat = extractionOptions[choices.extFormatLbl] if extractionOptions else None
    #         gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
    #         return [HistElement(gsTrack.title, extractionFormat) for gsTrack in gsuite.allTracks()]

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        basisTrackNameAsList = choices.basisTrack.split(':')
        extractionOptions = dict(GalaxyInterface.getTrackExtractionOptions(choices.genome, basisTrackNameAsList))
        extractionFormat = extractionOptions[choices.extFormatLbl] if extractionOptions else None

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        outGSuite = GSuite()
        for gsTrack in gsuite.allTracks():
            # outputTrackFn = cls.extraGalaxyFn[gsTrack.title]
            # print '<br>\n<br>\n output track filename: ', outputTrackFn
            # print 'path: ', gsTrack.path
            # print 'parsed uri: ', gsTrack._parsedUri
            newTrackFileName = gsTrack.title + '.' + extractionFormat
            outGalaxyFn = ExternalTrackManager.createGalaxyFilesFn(galaxyFn, newTrackFileName)
            ensurePathExists(outGalaxyFn)
            uri = GalaxyGSuiteTrack.generateURI(galaxyFn, extraFileName=newTrackFileName)
            GalaxyInterface.parseExtFormatAndExtractTrackManyBins(choices.genome, basisTrackNameAsList,
                                                                  gsTrack.suffix, gsTrack.path, True,
                                                                  choices.extFormatLbl,
                                                                  outGalaxyFn)

            outGSuite.addTrack(GSuiteTrack(uri, title=gsTrack.title, fileFormat=gsTrack.fileFormat,
                                           trackType=gsTrack.trackType,
                                           genome=choices.genome, attributes=gsTrack.attributes))

        GSuiteComposer.composeToFile(outGSuite, galaxyFn)

        #FIXME: hyper_gui.py at line 362, genome is not set when GenomeMixin is used,
        #FIXME: BaseToolController.py line 74, there is no dbkey parameter.

        #filename = '/software/galaxy/galaxy-dist-hg-gsuite-submit/database/files/000/121/dataset_121468.dat'
        # if output != None:
        #     sys.stdout = open(output, "w", 0)
        # if params.has_key('sepFilePrRegion'):
        #     #args: genome, trackName, regSpec, binSpec, globalCoords, extractionFormat, galaxyFn
        #     # genome= 'mm9'
        #     # trackName = tracks1 = ['Sequence', 'DNA']
        #     # regSpec = region = 'valued.bed' (extracted from binfile parameter)
        #     # binSpec = binSize = '/software/galaxy/galaxy-dist-hg-gsuite-submit/database/files/120/dataset_120638.dat'
        #                           '/software/galaxy/galaxy-dist-hg-gsuite-submit/database/files/120/dataset_120642.dat'
        #     # globalCoords = True
        #     # extractionFormat = overlaps = 'Original file format (suffix: fa)'
        #     # galaxyFn = output = '/software/galaxy/galaxy-dist-hg-gsuite-submit/database/files/000/121/dataset_121416.dat'
        #
        #     # bins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome, trackName)
        #
        #     #uri = GalaxyGSuiteTrack.generateURI(self._galaxyFn, extraFileName=extraFileName)
        #
        #     GalaxyInterface.parseExtFormatAndExtractTrackManyBinsToRegionDirsInZipFile(genome, tracks1, region, binSize, True, overlaps, output)
        # else:
        #     GalaxyInterface.parseExtFormatAndExtractTrackManyBins(genome, tracks1, region, binSize, True, overlaps, output)

    @staticmethod
    def validateAndReturnErrors(choices):
        if not choices.gsuite:
            return "Please select a GSuite from history"
        if not choices.genome:
            return "Please select a genome for the basis track"

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        if choices.genome != gsuite.genome:
            return "The selected genome and the gsuite genome must be equal. Selected = %s; GSuite = %s" % (choices.genome, gsuite.genome)

    # @staticmethod
    # def _getGenome(choices):
    #     DebugUtil.insertBreakPoint()
    #     return choices.genome

    @staticmethod
    def getOutputFormat(choices=None):
        return 'gsuite'

    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    #@staticmethod
    #def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
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
    #    name. The base directory is STATIC_PATH as defined by AutoConfig.py. The
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
    #
    #@staticmethod
    #def getOutputFormat(choices):
    #    '''
    #    The format of the history element with the output of the tool. Note
    #    that html output shows print statements, but that text-based output
    #    (e.g. bed) only shows text written to the galaxyFn file.In the latter
    #    case, all all print statements are redirected to the info field of the
    #    history item box.
    #    '''
    #    return 'html'
