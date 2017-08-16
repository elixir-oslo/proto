import gold.gsuite.GSuiteConstants as GSuiteConstants
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.tools.GeneralGuiTool import BoxGroup
from quick.webtools.GeneralGuiTool import GeneralGuiTool

'''
Preprocess: Yes
Specify genome build for GSuite file: other... (genome is required but not previously specified)
Specify genome build for GSuite file: __genome__

Preprocess: Yes
Specify genome build for GSuite file: hg19 (already specified) / other... (override the specified genome)
Select genome build from full list: __genome__

Preprocess: No
Specify genome build for GSuite file: unknown (keep genome unspecified) / other... (specify genome)
Select genome build from full list: __genome__

Preprocess: No
Specify genome build for GSuite file: hg19 (already specified) / other... (override the specified genome)
Select genome build from full list: __genome__

2 tracks
Preprocess: Yes, track1: unknown, track2: unknown
Specify genome build for the analysis: other... (genome is required but not previously specified)
Specify genome build for GSuite file: __genome__

Preprocess: Yes, track1: hg19, track2: unknown
Specify genome build for the analysis: hg19 (specified in GSuite number 1) / other... (override the specified genome)
Select genome build from full list: __genome__

Preprocess: Yes, track1: unknown, track2: hg19
Specify genome build for theanalysis: hg19 (specified in GSuite number 2) / other... (override the specified genome)
Select genome build from full list: __genome__

Preprocess: Yes, track1: hg18, track2: hg19
Specify genome build for the analysis: hg18 (specified in GSuite number 1) / hg19 (specified in GSuite number 2) / other... (override the specified genomes)
Select genome build from full list: __genome__
Note: The two GSuite files specify different genome builds. Going ahead with tool execution will assume that one of the GSuites
have been annotated with the wrong genome build. If this is not correct, you will need to carry out a liftOver of the tracks in
one of your GSuite files prior to tool execution.

Preprocess: Yes, track1: hg19, track2: hg19
Specify genome build for GSuite file: hg19 (specified in all GSuites) / other... (override the specified genome)
Select genome build from full list: __genome__

Preprocess: No, track1: unknown, track2: unknown
Specify genome build for output GSuite file: unknown (keep genome unspecified) / other... (specify genome)
Select genome build from full list: __genome__

Preprocess: No, track1: hg19, track2: unknown
Specify genome build for output GSuite file: hg19 (specified in GSuite number 1) / unknown (unspecified, as in GSuite number 2) / other... (override the specified genome)
Select genome build from full list: __genome__

Preprocess: No, track1: unknown, track2: hg19
Specify genome build for output GSuite file: unknown (unspecified, as in GSuite number 1) / hg19 (specified in GSuite number 2) / other... (specify genome)
Select genome build from full list: __genome__

Preprocess: No, track1: hg18, track2: hg19
Specify genome build for GSuite file: hg18 (specified in GSuite number 1) / hg19 (specified in GSuite number 2) / other... (override the specified genomes)
Select genome build from full list: __genome__
Note: The two GSuite files specify different genome builds. Going ahead with tool execution will assume that one of the GSuites
have been annotated with the wrong genome build. If this is not correct, you will need to carry out a liftOver of the tracks in
one of your GSuite files prior to tool execution.

Preprocess: Yes, track1: hg19, track2: hg19
Specify genome build for GSuite file: hg19 (specified in all GSuites) / other... (override the specified genome)
Select genome build from full list: __genome__

'''


class GenomeMixin(object):
    # For subclass override
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gsuite']
    ALLOW_UNKNOWN_GENOME = True
    ALLOW_GENOME_OVERRIDE = True
    ALLOW_MULTIPLE_GENOMES = False
    WHAT_GENOME_IS_USED_FOR = 'the output GSuite file' # Other common possibility: 'the analysis'

    # Should not be overridden
    OPTIONS_BOX_MSG = 'Specify genome build for %s:'

    GENOME_UNSPECIFIED_MSG_SUFFIX = ' (keep genome unspecified)'
    GENOME_SPECIFIED_MSG_SUFFIX = ' (already specified)'
    GENOME_UNSPECIFIED_IN_ONE_GSUITE_MSG_SUFFIX = ' (unspecified, as in GSuite number %s)'
    GENOME_SPECIFIED_IN_ONE_GSUITE_MSG_SUFFIX = ' (specified in GSuite number %s)'
    GENOME_SPECIFIED_IN_ALL_GSUITES_MSG_SUFFIX = ' (specified in all GSuites)'
    GENOME_SPECIFIED_MISMATCH_MSG_SUFFIX = ' (genome mismatch, not allowed by tool)'

    OTHER_MSG_PREFIX = 'other...'
    OTHER_SPECIFY_MSG_SUFFIX = ' (specify genome)'
    OTHER_REQUIRED_AND_UNKNOWN_SUFFIX = ' (genome is required but not previously specified)'
    OTHER_OVERRIDE_MSG_SUFFIX = ' (override the specified genome)'
    OTHER_OVERRIDE_SEVERAL_MSG_SUFFIX = ' (override the specified genomes)'

    GENOME_MISMATCH_NOTE = 'The GSuite files specify different genome builds. Going ahead ' +\
                           'with tool execution will assume that at least of the GSuites has been annotated ' +\
                           'with the wrong genome build. If this is not correct, you might need to use ' +\
                           'the "liftOver" tool or similar to move some tracks from one genome build to ' +\
                           'another before running this tool again. The following genomes are specified: '

    ERROR_GENOME_BUILD_MISMATCH = 'The GSuite files specify different genome builds. ' +\
                                  'This is not allowed. The genome build(s) might be incorrectly specified, ' +\
                                  'or you might need to use the "liftOver" tool or similar to move the tracks ' +\
                                  'from one genome build to another. The following genomes are specified: '
    ERROR_MULTIPLE_GENOMES_NOT_ALLOWED = 'This tool does not allow multiple genomes to be defined in the same ' +\
                                         'GSuite file.'
    ERROR_PREPROCESSED_TRACK_INVALID = 'Preprocessed track "%s" is not a valid track. Often this is due to ' +\
                                 'specifying an incorrect genome build.'

    @classmethod
    def getInputBoxNamesForGenomeSelection(cls):
        return [(cls.OPTIONS_BOX_MSG % cls.WHAT_GENOME_IS_USED_FOR, 'specifyGenomeFromGsuites'),
                ('Genome mismatch note', 'genomeMismatchNote'),
                ('Genome build:', 'specifyGenomeFromList'),
                ('Genome', 'genome')]

    @classmethod
    def getInputBoxGroups(cls, choices=None):
        prevBoxGroups = None
        if hasattr(super(GenomeMixin, cls), 'getInputBoxGroups'):
            prevBoxGroups = super(GenomeMixin, cls).getInputBoxGroups(choices)

        if choices.specifyGenomeFromGsuites:
            if not prevBoxGroups:
                prevBoxGroups = []
            return prevBoxGroups + \
                   [BoxGroup(label='Genome', first='specifyGenomeFromGsuites', last='genome')]
        else:
            return prevBoxGroups

    @classmethod
    def _getGsuiteGenomes(cls, prevChoices):
        genomes = []
        for key in cls.GSUITE_FILE_OPTIONS_BOX_KEYS:
            galaxyTN = getattr(prevChoices, key)

            if galaxyTN:
                try:
                    from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
                    gSuite = getGSuiteFromGalaxyTN(galaxyTN)
                    genomes.append(gSuite.genome)
                except:
                    return None

        if genomes:
            return genomes
    
    @classmethod
    def _getNumSpecifiedGenomes(cls, prevChoices):
        genomes = cls._getGsuiteGenomes(prevChoices)
        if genomes:
            return len([genome for genome in genomes if genome != GSuiteConstants.UNKNOWN])
        else:
            return 0

    @classmethod
    def _getNumUniquelySpecifiedGenomes(cls, prevChoices):
        genomes = cls._getGsuiteGenomes(prevChoices)
        if genomes:
            return len(set([genome for genome in genomes if genome != GSuiteConstants.UNKNOWN]))
        else:
            return 0

    @classmethod
    def _allowUnknownGenome(cls, prevChoices):
        return cls.ALLOW_UNKNOWN_GENOME

    @classmethod
    def _allowGenomeOverride(cls, prevChoices):
        return cls.ALLOW_GENOME_OVERRIDE

    @classmethod
    def _allowMultipleGenomes(cls, prevChoices):
        return cls.ALLOW_MULTIPLE_GENOMES

    @classmethod
    def getOptionsBoxSpecifyGenomeFromGsuites(cls, prevChoices):
        selectionList = []

        genomes = cls._getGsuiteGenomes(prevChoices)
        if not genomes:
            return None

        numGSuites = len(genomes)

        if len(set(genomes)) == 1: # All GSuites specify the same genome
            genome = genomes[0]
            if genome == GSuiteConstants.UNKNOWN:
                if cls._allowUnknownGenome(prevChoices):
                    selectionList.append(GSuiteConstants.UNKNOWN + \
                                         cls.GENOME_UNSPECIFIED_MSG_SUFFIX)
                    selectionList.append(cls.OTHER_MSG_PREFIX + cls.OTHER_SPECIFY_MSG_SUFFIX)
                else:
                    selectionList.append(cls.OTHER_MSG_PREFIX + cls.OTHER_REQUIRED_AND_UNKNOWN_SUFFIX)
            else:
                if numGSuites == 1:
                    selectionList.append(genome + cls.GENOME_SPECIFIED_MSG_SUFFIX)
                else:
                    selectionList.append(genome + cls.GENOME_SPECIFIED_IN_ALL_GSUITES_MSG_SUFFIX)

                if cls._allowGenomeOverride(prevChoices):
                    selectionList.append(cls.OTHER_MSG_PREFIX + cls.OTHER_OVERRIDE_MSG_SUFFIX)
        else:
            for i,genome in enumerate(genomes):
                if genome == GSuiteConstants.UNKNOWN:
                    if cls._allowUnknownGenome(prevChoices):
                        selectionList.append(GSuiteConstants.UNKNOWN + \
                                             cls.GENOME_UNSPECIFIED_IN_ONE_GSUITE_MSG_SUFFIX % (i+1))
                else:
                    selectionList.append(genome + cls.GENOME_SPECIFIED_IN_ONE_GSUITE_MSG_SUFFIX % (i+1))

            if cls._allowGenomeOverride(prevChoices):
                if cls._getNumSpecifiedGenomes(prevChoices) == 1:
                    selectionList.append(cls.OTHER_MSG_PREFIX + cls.OTHER_OVERRIDE_MSG_SUFFIX)
                else:
                    selectionList.append(cls.OTHER_MSG_PREFIX + cls.OTHER_OVERRIDE_SEVERAL_MSG_SUFFIX)

        return selectionList

    @classmethod
    def getOptionsBoxGenomeMismatchNote(cls, prevChoices):
        if cls._allowGenomeOverride(prevChoices) and cls._getNumUniquelySpecifiedGenomes(prevChoices) > 1:
            core = HtmlCore()
            core.styleInfoBegin(styleClass="infomessagesmall")
            core.paragraph(cls.GENOME_MISMATCH_NOTE + ', '.join(cls._getGsuiteGenomes(prevChoices)))
            core.styleInfoEnd()
            return '__rawstr__', str(core)

    @classmethod
    def getOptionsBoxSpecifyGenomeFromList(cls, prevChoices):
        if prevChoices.specifyGenomeFromGsuites:
            if prevChoices.specifyGenomeFromGsuites.startswith(cls.OTHER_MSG_PREFIX):
                return '__genome__'

    @classmethod
    def getOptionsBoxGenome(cls, prevChoices):
        if prevChoices.specifyGenomeFromGsuites:
            if prevChoices.specifyGenomeFromGsuites.startswith(cls.OTHER_MSG_PREFIX):
                return '__hidden__', prevChoices.specifyGenomeFromList
            else:
                genome = prevChoices.specifyGenomeFromGsuites.split(' (')[0]
                return '__hidden__', genome

    @classmethod
    def _validateGenome(cls, choices, validateBinaryTracksIfPresent=True):
        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        from quick.application.ProcTrackOptions import ProcTrackOptions

        allGSuiteGalaxyTNs = [getattr(choices, key) for key in cls.GSUITE_FILE_OPTIONS_BOX_KEYS]
        if all(allGSuiteGalaxyTNs):
            if (not cls._allowGenomeOverride(choices)) and cls._getNumUniquelySpecifiedGenomes(choices) > 1:
                return cls.ERROR_GENOME_BUILD_MISMATCH + ', '.join(cls._getGsuiteGenomes(choices))
            
            errorStr = GeneralGuiTool._checkGenome(choices.genome)
            if errorStr:
                return errorStr

            if not cls._allowMultipleGenomes(choices) and choices.genome == GSuiteConstants.MULTIPLE:
                return cls.ERROR_MULTIPLE_GENOMES_NOT_ALLOWED

            if validateBinaryTracksIfPresent:
                for galaxyTN in allGSuiteGalaxyTNs:
                    gSuite = getGSuiteFromGalaxyTN(galaxyTN)
                    if gSuite.fileFormat == GSuiteConstants.PREPROCESSED and gSuite.location == GSuiteConstants.LOCAL:
                        for gSuiteTrack in gSuite.allTracks():
                            if not ProcTrackOptions.isValidTrack(choices.genome, gSuiteTrack.trackName, True):
                                return cls.ERROR_PREPROCESSED_TRACK_INVALID % gSuiteTrack.title

        #return repr(choices.genome)
