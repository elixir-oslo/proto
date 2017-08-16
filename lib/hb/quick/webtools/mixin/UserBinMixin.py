from proto.hyperbrowser.HtmlCore import HtmlCore
from gold.util.CustomExceptions import AbstractClassError, ShouldNotOccurError
from proto.tools.GeneralGuiTool import BoxGroup
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.application.UserBinManager import \
    getNameAndProtoRegSpecLabelsForAllUserBinSources, \
    getNameAndProtoBinSpecLabelsForAllUserBinSources
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN


class UserBinMixin(object):
    # For subclass override
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gsuite']

    # Local constants
    REG_SPEC_NAMES, REG_SPEC_LABELS = zip(*getNameAndProtoRegSpecLabelsForAllUserBinSources())
    BIN_SPEC_NAMES, BIN_SPEC_LABELS = zip(*getNameAndProtoBinSpecLabelsForAllUserBinSources())

    @classmethod
    def _getUserBinRegistrySubCls(cls, prevChoices):
        """
        May be overridden by the subclass. A tool should then either:
          - subclass one of the existing UserBinMixin variants:

              UserBinMixinForDescriptiveStats
              UserBinMixinForHypothesisTests
              UserBinMixinForExtraction

            Each of these specify a default ordering of the user bin choice selection
            box.

          - override the _getUserBinRegistrySubCls method in the tool:

            If none of the subclasses above fits (if e.g. the tool supports both descriptive
            statistics and hypothesis tests), one needs to override the _getUserBinRegistrySubCls
            method and either:

                - return one of the subclasses above
                - create and return a new subclass of UserBinSourceRegistry

            In both cases, one can make use of prevChoices, if needed.
        """
        # Default user bin choice selection is for descriptive and
        # other analyses without position randomization
        from quick.application.UserBinManager import UserBinSourceRegistryForDescriptiveStats
        return UserBinSourceRegistryForDescriptiveStats

    @classmethod
    def getInputBoxNamesForUserBinSelection(cls):
        """
        Should be added at the end of the list in the getUserBinInputBoxNames()
        method in the subclass. E.g.:

        @classmethod
        def getUserBinInputBoxNames(cls):
            return [('First choice', 'first') + \
                    ('Second choice', 'second')] + \
                    cls.getInputBoxNamesForUserBinSelection()
        """
        cls.setupExtraBoxMethods()

        inputBoxNames = [('Compare in:', 'compareIn')]

        for i, label in enumerate(cls.REG_SPEC_LABELS):
            inputBoxNames += [(label, 'regSpec%s' % i)]
            inputBoxNames += [('', 'regSpecHelpText%s' % i)]

        for i, label in enumerate(cls.BIN_SPEC_LABELS):
            inputBoxNames += [(label, 'binSpec%s' % i)]
            inputBoxNames += [('', 'binSpecHelpText%s' % i)]

        inputBoxNames += [('', 'sourceHelpText')]

        return inputBoxNames

    @classmethod
    def getInputBoxGroups(cls, choices=None):
        prevBoxGroups = None
        if hasattr(super(UserBinMixin, cls), 'getInputBoxGroups'):
            prevBoxGroups = super(UserBinMixin, cls).getInputBoxGroups(choices)

        if choices.compareIn:
            if not prevBoxGroups:
                prevBoxGroups = []
            return prevBoxGroups + \
                   [BoxGroup(label='Region and scale', first='compareIn', last='sourceHelpText')]
        else:
            return prevBoxGroups

    @classmethod
    def _getUserBinSourceRegistry(cls, prevChoices):
        ubSourceRegistryCls = cls._getUserBinRegistrySubCls(prevChoices)

        genome = cls._getGenome(prevChoices)
        if not genome:
            return None

        trackNameList = cls._getTrackNameList(prevChoices)
        return ubSourceRegistryCls(genome, trackNameList)

    @classmethod
    def _getNamesOfAllUserBinSources(cls, prevChoices):
        ubSourceRegistry = cls._getUserBinSourceRegistry(prevChoices)
        if not ubSourceRegistry:
            return []

        return ubSourceRegistry.getNamesOfAllUserBinSourcesForSelection()

    @classmethod
    def _getUserBinSourceInfoFromSelection(cls, prevChoices):
        ubSourceRegistry = cls._getUserBinSourceRegistry(prevChoices)
        if not ubSourceRegistry:
            return None

        return ubSourceRegistry.getUserBinSourceInfoFromName(prevChoices.compareIn)

    @classmethod
    def _isBasicMode(cls, prevChoices):
        # This code checks if the tool is in basic mode, we don't want to
        # display user bin selection in basic mode.
        # For this to work you must name the optionBox isBasic in your tool.
        try:
            isBasicMode = prevChoices.isBasic
        except:
            pass
        else:
            if isBasicMode:
                return True
        return False

    @classmethod
    def getOptionsBoxCompareIn(cls, prevChoices):
        if cls._isBasicMode(prevChoices):
            return None

        allSources = cls._getNamesOfAllUserBinSources(prevChoices)
        if allSources:
            return allSources

    @classmethod
    def getInfoForOptionsBoxCompareIn(cls, prevChoices):
        core = HtmlCore()
        core.paragraph('Select the region(s) of the genome in which to analyze and '
                       'possibly how the analysis regions should be divided into bins. '
                       'First select the main category, and if needed, provide further '
                       'details in the subsequent fields.')
        return str(core)

    @classmethod
    def getOptionsBoxSourceHelpText(cls, prevChoices):
        if cls._isBasicMode(prevChoices) or not prevChoices.compareIn:
            return None

        ubSourceInfo = cls._getUserBinSourceInfoFromSelection(prevChoices)
        if ubSourceInfo:
            return '__rawStr__', ubSourceInfo.helpTextForUserBinSource()

    @classmethod
    def _getOptionBoxRegSpec(cls, prevChoices, index):
        if index < len(cls.REG_SPEC_LABELS):
            if prevChoices.compareIn == cls.REG_SPEC_NAMES[index]:
                ubSourceInfo = cls._getUserBinSourceInfoFromSelection(prevChoices)
                return ubSourceInfo.protoRegSpecOptionsBoxForUserBinSource()

    @classmethod
    def _getOptionBoxRegSpecHelpText(cls, prevChoices, index):
        if index < len(cls.REG_SPEC_LABELS):
            if prevChoices.compareIn == cls.REG_SPEC_NAMES[index]:
                ubSourceInfo = cls._getUserBinSourceInfoFromSelection(prevChoices)
                return '__rawStr__', ubSourceInfo.protoRegSpecHelpTextForUserBinSource()

    @classmethod
    def _getOptionBoxBinSpec(cls, prevChoices, index):
        if index < len(cls.BIN_SPEC_LABELS):
            if prevChoices.compareIn == cls.BIN_SPEC_NAMES[index]:
                ubSourceInfo = cls._getUserBinSourceInfoFromSelection(prevChoices)
                return ubSourceInfo.protoBinSpecOptionsBoxForUserBinSource()

    @classmethod
    def _getOptionBoxBinSpecHelpText(cls, prevChoices, index):
        if index < len(cls.BIN_SPEC_LABELS):
            if prevChoices.compareIn == cls.BIN_SPEC_NAMES[index]:
                ubSourceInfo = cls._getUserBinSourceInfoFromSelection(prevChoices)
                return '__rawStr__', ubSourceInfo.protoBinSpecHelpTextForUserBinSource()

    @classmethod
    def setupExtraBoxMethods(cls):
        from functools import partial

        for i in range(len(cls.REG_SPEC_LABELS)):
            setattr(cls, 'getOptionsBoxRegSpec%s' % i,
                    partial(cls._getOptionBoxRegSpec, index=i))
            setattr(cls, 'getOptionsBoxRegSpecHelpText%s' % i,
                    partial(cls._getOptionBoxRegSpecHelpText, index=i))

        for i in range(len(cls.BIN_SPEC_LABELS)):
            setattr(cls, 'getOptionsBoxBinSpec%s' % i,
                    partial(cls._getOptionBoxBinSpec, index=i))
            setattr(cls, 'getOptionsBoxBinSpecHelpText%s' % i,
                    partial(cls._getOptionBoxBinSpecHelpText, index=i))

    @classmethod
    def getRegsAndBinsSpec(cls, choices):
        """
        Returns the regSpec and binSpec for the choices made in the gui.
        """

        if cls._isBasicMode(choices):
            return "__chrs__", "*"

        regIndex = cls.REG_SPEC_NAMES.index(choices.compareIn)
        regSpec = getattr(choices, 'regSpec%s' % regIndex)

        try:
            binIndex = cls.BIN_SPEC_NAMES.index(choices.compareIn)
            binSpec = getattr(choices, 'binSpec%s' % binIndex)
        except:
            binSpec = ''

        try:
            from proto.CommonFunctions import extractFnFromDatasetInfo, \
                extractFileSuffixFromDatasetInfo
            binSpec, regSpec = extractFnFromDatasetInfo(binSpec), \
                               extractFileSuffixFromDatasetInfo(binSpec)
        except:
            pass

        return regSpec, binSpec

    @classmethod
    def validateUserBins(cls, choices):
        if cls._isBasicMode(choices):
            return None

        regSpec, binSpec = cls.getRegsAndBinsSpec(choices)
        return cls._getUserBinSourceRegistry(choices).validateRegAndBinSpec(regSpec, binSpec)

        errorString = GalaxyInterface._validateRegAndBinSpec(regSpec, binSpec, genome,
                                                             [trackName1, trackName2])
        if errorString:
            return errorString

    @classmethod
    def _getGenome(cls, choices):
        if hasattr(choices, 'genome'):
            return choices.genome
        else:
            genomes = set(getGSuiteFromGalaxyTN(getattr(choices, key)).genome for key in
                          cls.GSUITE_FILE_OPTIONS_BOX_KEYS if hasattr(choices, key))
            if len(genomes) == 1:
                genome = genomes.pop()
                if genome:
                    return genome

            raise ShouldNotOccurError(
                'Subclass of UserBinMixin needs to override the cls._getGenome method')

    @classmethod
    def _getTrackNameList(cls, choices):
        trackNameList = []
        gsuites = [getGSuiteFromGalaxyTN(getattr(choices, key)) for key in
                   cls.GSUITE_FILE_OPTIONS_BOX_KEYS if
                   hasattr(choices, key) and getattr(choices, key)]

        for gsuite in gsuites:
            trackNameList += [track.trackName for track in gsuite.allTracks()]

        return trackNameList


class UserBinMixinForDescriptiveStats(UserBinMixin):
    """
    To be used for descriptive and other analyses without position randomization
    """


class UserBinMixinForHypothesisTests(UserBinMixin):
    """
    To be used for hypothesis tests where positions are randomized on the genome line.
    """
    @classmethod
    def _getUserBinRegistrySubCls(cls, prevChoices):
        from quick.application.UserBinManager import UserBinSourceRegistryForHypothesisTests
        return UserBinSourceRegistryForHypothesisTests


class UserBinMixinForExtraction(UserBinMixin):
    """
    To be used for track extraction and other manipulation
    """
    @classmethod
    def _getUserBinRegistrySubCls(cls, prevChoices):
        from quick.application.UserBinManager import UserBinSourceRegistryForExtraction
        return UserBinSourceRegistryForExtraction


class UserBinMixinForSmallBins(UserBinMixin):
    """
    To be used for analyses that requires small bins
    """
    @classmethod
    def _getUserBinRegistrySubCls(cls, prevChoices):
        from quick.application.UserBinManager import UserBinSourceRegistry

        class UserBinSourceRegistryForSmallBins(UserBinSourceRegistry):
            def _getOrderOfUserBinKeysForSelection(self):
                return ['__custom__', '__genes__', '__history__']

        return UserBinSourceRegistryForSmallBins

    @classmethod
    def _getOptionBoxBinSpec(cls, prevChoices, index):
        if index < len(cls.BIN_SPEC_LABELS):
            if prevChoices.compareIn == cls.BIN_SPEC_NAMES[index]:
                if prevChoices.compareIn == 'Custom specification':
                    return '250k'
                else:
                    return UserBinMixin._getOptionBoxBinSpec(prevChoices, index)

