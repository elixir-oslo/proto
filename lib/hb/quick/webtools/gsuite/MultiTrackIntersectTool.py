import os

import gold.gsuite.GSuiteConstants as GSuiteConstants
from gold.gsuite.GSuiteFunctions import changeSuffixIfPresent, getTitleWithSuffixReplaced
from gold.gsuite.GSuitePreprocessor import GSuitePreprocessor
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack
from quick.webtools.GeneralGuiTool import GeneralGuiTool, HistElement
from quick.extra.ProgressViewer import ProgressViewer
from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName, \
    writeGSuiteHiddenTrackStorageHtml
from quick.webtools.mixin.GenomeMixin import GenomeMixin


class MultiTrackIntersectTool(GeneralGuiTool, GenomeMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gSuite']
    ALLOW_UNKNOWN_GENOME = False
    ALLOW_GENOME_OVERRIDE = False
    ALLOW_MULTIPLE_GENOMES = False
    WHAT_GENOME_IS_USED_FOR = 'the output GSuite file' # Other common possibility: 'the analysis'

    FROM_HISTORY_TEXT = 'From history'
    FROM_HYPERBROWSER_TEXT = 'From HyperBrowser repository'

    WITH_OVERLAPS = 'Allow multiple overlapping points/segments within the same track'
    NO_OVERLAPS = 'Merge any overlapping points/segments within the same track'

    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]
    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    OUTPUT_TRACKS_SUFFIX = 'bed'
    GSUITE_OUTPUT_LOCATION = GSuiteConstants.LOCAL
    GSUITE_OUTPUT_FILE_FORMAT = GSuiteConstants.PREPROCESSED
    GSUITE_OUTPUT_TRACK_TYPE = GSuiteConstants.SEGMENTS

    OUTPUT_GSUITE_DESCRIPTION = ', intersected'
    PROGRESS_INTERSECT_MSG = 'Intersect tracks'
    PROGRESS_PREPROCESS_MSG = 'Preprocess tracks'

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Intersect preprocessed tracks in GSuite with a single track"

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
        return [('Select GSuite file from history:', 'gSuite')] +\
               cls.getInputBoxNamesForGenomeSelection() +\
               [('Select source of filtering track:', 'trackSource'),
                ('Select track from history:', 'trackHistory'),
                ('Select track:', 'track'),
                ('Overlap handling:', 'withOverlaps')]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @classmethod
    def getOptionsBoxGSuite(cls): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return cls.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxTrackSource(cls, prevChoices):
        return [cls.FROM_HISTORY_TEXT, cls.FROM_HYPERBROWSER_TEXT]

    @classmethod
    def getOptionsBoxTrackHistory(cls, prevChoices):
        if prevChoices.trackSource == cls.FROM_HISTORY_TEXT:
            from gold.application.DataTypes import getSupportedFileSuffixesForPointsAndSegments
            return cls.getHistorySelectionElement(*getSupportedFileSuffixesForPointsAndSegments())

    @classmethod
    def getOptionsBoxTrack(cls, prevChoices):
        if prevChoices.trackSource == cls.FROM_HYPERBROWSER_TEXT:
            return cls.TRACK_SELECT_ELEMENT

    @classmethod
    def getOptionsBoxWithOverlaps(cls, prevChoices):
        if prevChoices.trackHistory or prevChoices.track:
            return [cls.NO_OVERLAPS, cls.WITH_OVERLAPS]

    #@staticmethod
    #def getInfoForOptionsBoxKey(prevChoices):
    #    '''
    #    If not None, defines the string content of an clickable info box beside
    #    the corresponding input box. HTML is allowed.
    #    '''
    #    return None

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @classmethod
    def getExtraHistElements(cls, choices):
        desc = cls.OUTPUT_GSUITE_DESCRIPTION
        return [HistElement(getGSuiteHistoryOutputName(
                                'nointersect', description=desc, datasetInfo=choices.gSuite),
                            GSuiteConstants.GSUITE_SUFFIX),
                HistElement(getGSuiteHistoryOutputName(
                                'primary', description=desc, datasetInfo=choices.gSuite),
                            GSuiteConstants.GSUITE_SUFFIX),
                HistElement(getGSuiteHistoryOutputName(
                                'nopreprocessed', description=desc, datasetInfo=choices.gSuite),
                            GSuiteConstants.GSUITE_SUFFIX),
                HistElement(getGSuiteHistoryOutputName(
                                'preprocessed', description=desc, datasetInfo=choices.gSuite),
                            GSuiteConstants.GSUITE_SUFFIX),
                HistElement(getGSuiteHistoryOutputName(
                                'storage', description=desc, datasetInfo=choices.gSuite),
                            GSuiteConstants.GSUITE_STORAGE_SUFFIX, hidden=True)]

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
        from gold.gsuite.GSuite import GSuite
        from gold.gsuite.GSuiteTrack import GSuiteTrack, HbGSuiteTrack
        from gold.origdata.TrackGenomeElementSource import TrackViewListGenomeElementSource
        from gold.origdata.FileFormatComposer import getComposerClsFromFileSuffix
        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from quick.application.GalaxyInterface import GalaxyInterface
        from quick.application.UserBinSource import UserBinSource
        from quick.extra.TrackExtractor import TrackExtractor

        genome = choices.genome
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)

        if choices.withOverlaps == cls.NO_OVERLAPS:
            if choices.trackSource == cls.FROM_HISTORY_TEXT:
                filterTrackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, choices.trackHistory)
            else:
                filterTrackName = choices.track.split(':')
        else:
            if choices.trackSource == cls.FROM_HISTORY_TEXT:
                regSpec = ExternalTrackManager.extractFileSuffixFromGalaxyTN(choices.trackHistory)
                binSpec = ExternalTrackManager.extractFnFromGalaxyTN(choices.trackHistory)
            else:
                regSpec = 'track'
                binSpec = choices.track

            userBinSource = UserBinSource(regSpec, binSpec, genome)

        desc = cls.OUTPUT_GSUITE_DESCRIPTION
        emptyFn = cls.extraGalaxyFn \
            [getGSuiteHistoryOutputName('nointersect', description=desc, datasetInfo=choices.gSuite)]
        primaryFn = cls.extraGalaxyFn \
            [getGSuiteHistoryOutputName('primary', description=desc, datasetInfo=choices.gSuite)]
        errorFn = cls.extraGalaxyFn \
            [getGSuiteHistoryOutputName('nopreprocessed', description=desc, datasetInfo=choices.gSuite)]
        preprocessedFn = cls.extraGalaxyFn \
            [getGSuiteHistoryOutputName('preprocessed', description=desc, datasetInfo=choices.gSuite)]
        hiddenStorageFn = cls.extraGalaxyFn \
            [getGSuiteHistoryOutputName('storage', description=desc, datasetInfo=choices.gSuite)]

        analysisDef = '-> TrackIntersectionStat'
#         analysisDef = '-> TrackIntersectionWithValStat'

        numTracks = gSuite.numTracks()
        progressViewer = ProgressViewer([(cls.PROGRESS_INTERSECT_MSG, numTracks),
                                         (cls.PROGRESS_PREPROCESS_MSG, numTracks)], galaxyFn)
        emptyGSuite = GSuite()
        primaryGSuite = GSuite()

        for track in gSuite.allTracks():
            newSuffix = cls.OUTPUT_TRACKS_SUFFIX
            extraFileName = os.path.sep.join(track.trackName)
            extraFileName = changeSuffixIfPresent(extraFileName, newSuffix=newSuffix)
            title = getTitleWithSuffixReplaced(track.title, newSuffix)

            primaryTrackUri = GalaxyGSuiteTrack.generateURI(
                galaxyFn=hiddenStorageFn, extraFileName=extraFileName,
                suffix=newSuffix if not extraFileName.endswith(newSuffix) else '')
            primaryTrack = GSuiteTrack(primaryTrackUri, title=title,
                                       genome=track.genome, attributes=track.attributes)

            if choices.withOverlaps == cls.NO_OVERLAPS:
                res = GalaxyInterface.runManual([track.trackName, filterTrackName], analysisDef, '*', '*',
                                                 genome=genome, galaxyFn=galaxyFn, username=username)

                trackViewList = [res[key]['Result'] for key in sorted(res.keys())]

                tvGeSource = TrackViewListGenomeElementSource(genome, trackViewList)

                composerCls = getComposerClsFromFileSuffix(cls.OUTPUT_TRACKS_SUFFIX)
                composerCls(tvGeSource).composeToFile(primaryTrack.path)
            else:
                TrackExtractor.extractOneTrackManyRegsToOneFile( \
                    track.trackName, userBinSource, primaryTrack.path, fileFormatName=cls.OUTPUT_TRACKS_SUFFIX, \
                    globalCoords=True, asOriginal=False, allowOverlaps=True)

            # Temporary hack until better solution for empty result tracks have been implemented

            from gold.origdata.GenomeElementSource import GenomeElementSource
            geSource = GenomeElementSource(primaryTrack.path, genome=genome, suffix=cls.OUTPUT_TRACKS_SUFFIX)

            try:
                geSource.parseFirstDataLine()
                primaryGSuite.addTrack(primaryTrack)
            except Exception, e: # Most likely empty file
                primaryTrack.comment = e.message
                emptyGSuite.addTrack(primaryTrack)
                numTracks -= 1
                progressViewer.updateProgressObjectElementCount(
                    cls.PROGRESS_PREPROCESS_MSG, numTracks)
            #

            progressViewer.update()

        gSuitePreprocessor = GSuitePreprocessor()
        preprocessedGSuite, errorGSuite = gSuitePreprocessor.\
            visitAllGSuiteTracksAndReturnOutputAndErrorGSuites \
                (primaryGSuite, progressViewer)

        GSuiteComposer.composeToFile(emptyGSuite, emptyFn)
        GSuiteComposer.composeToFile(primaryGSuite, primaryFn)
        GSuiteComposer.composeToFile(preprocessedGSuite, preprocessedFn)
        GSuiteComposer.composeToFile(errorGSuite, errorFn)
        writeGSuiteHiddenTrackStorageHtml(hiddenStorageFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        errorStr = cls._validateGenome(choices)
        if errorStr:
            return errorStr

        errorStr = cls._checkGSuiteFile(choices.gSuite)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)

        errorStr = cls._checkGSuiteTrackListSize(gSuite)
        if errorStr:
            return errorStr

        errorStr = cls._checkGSuiteRequirements(
            gSuite,
            allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
            allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
            allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
            disallowedGenomes=cls.GSUITE_DISALLOWED_GENOMES)
        if errorStr:
            return errorStr

        if choices.trackSource == cls.FROM_HISTORY_TEXT:
            trackChoice = 'trackHistory'
        else:
            trackChoice = 'track'

        errorStr = cls._checkTrack(choices, trackChoice, 'genome')
        if errorStr:
            return errorStr

        errorStr = cls._checkBasicTrackType(choices, cls.GSUITE_ALLOWED_TRACK_TYPES,
                                                  trackChoice, 'genome')
        if errorStr:
            return errorStr

    @classmethod
    def getOutputName(cls, choices):
        return getGSuiteHistoryOutputName('progress', description=cls.OUTPUT_GSUITE_DESCRIPTION,
                                          datasetInfo=choices.gSuite)


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
        core.paragraph('Loops through all the tracks in the selected GSuite file and intersects all '
                       'tracks with the specified single filtering track. Only the parts of the '
                       'segments that are intersecting with the filtering track are kept.')

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
                                      disallowedGenomes=cls.GSUITE_DISALLOWED_GENOMES,
                                      outputLocation=cls.GSUITE_OUTPUT_LOCATION,
                                      outputFileFormat=cls.GSUITE_OUTPUT_FILE_FORMAT,
                                      outputTrackType=cls.GSUITE_OUTPUT_TRACK_TYPE)

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
    #     return 'u/hb-superuser/p/compile-gsuite-from-hyperbrowser-repository--intersect-preprocessed-tracks-in-gsuite-with-a-single-track---example'
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
