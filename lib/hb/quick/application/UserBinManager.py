import os
from collections import OrderedDict
from itertools import islice

from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.util.GenomeInfo import GenomeInfo
from gold.util.CustomExceptions import AbstractClassError, InvalidFormatError, \
    BoundingRegionsNotAvailableError, ShouldNotOccurError

# UserBinSourceInfo class and subclasses

class UserBinSourceInfo(object):
    KEY = None
    NAME = None

    def __init__(self, genome, trackNameList=[], **kwArgs):
        self._genome = genome
        self._trackNameList = trackNameList
        self._kwArgs = kwArgs

    def isAvailable(self, registry):
        raise AbstractClassError()

    def generateUserBinSource(self, regSpec, binSpec):
        raise AbstractClassError()

    def helpTextForUserBinSource(self):
        return ''

    def describeUserBinSource(self, regSpec, binSpec):
        raise AbstractClassError()

    def validateRegAndBinSpec(self, regSpec, binSpec):
        raise AbstractClassError()

    def getZeroBinsValidationMessage(self, regSpec, binSpec):
        raise AbstractClassError()

    @classmethod
    def protoRegSpecLabelForUserBinSource(cls):
        return ''

    @classmethod
    def protoRegSpecOptionsBoxForUserBinSource(cls):
        if cls.KEYS is not None:
            return '__hidden__', cls.KEYS[0]

    @classmethod
    def protoRegSpecHelpTextForUserBinSource(cls):
        return ''

    @classmethod
    def protoBinSpecLabelForUserBinSource(cls):
        return None

    @classmethod
    def protoBinSpecOptionsBoxForUserBinSource(cls):
        return None

    @classmethod
    def protoBinSpecHelpTextForUserBinSource(cls):
        return ''


class ChrArmNoteMixin(object):
    def _appendChrArmNoteIfNeeded(self, core):
        if self._kwArgs.get('forHypothesisTest'):
            core2 = HtmlCore()
            core2.styleInfoBegin(styleClass='infomessagesmall')
            core2.descriptionLine('Note', 'For hypothesis tests where the positions of elements '
                                         'are randomized, the centromeres and other regions '
                                         'where the elements are never found should be removed '
                                         'from the analysis regions. In this case, use the '
                                         'chromosome arms as analysis regions, define specific '
                                         'bounding regions for the tracks, or use custom '
                                         'analysis regions. If this is not done, the resulting '
                                         'p-values are generally better than what they should '
                                         'have been.')
            core2.styleInfoEnd()
            core.paragraph(str(core2))


class BoundingRegionUserBinSourceInfo(UserBinSourceInfo, ChrArmNoteMixin):
    KEYS = ['__brs__']
    NAME = 'Bounding regions'

    def __init__(self, genome, trackNameList=[], **kwArgs):
        UserBinSourceInfo.__init__(self, genome, trackNameList, **kwArgs)
        self._trackName1 = trackNameList[0] if len(trackNameList) >= 1 else None
        self._trackName2 = trackNameList[1] if len(trackNameList) >= 2 else None

    def isAvailable(self):
        if self._trackName1 is None: #or sum(1 for _ in self._trackNameList if _) > 2:
            return False
        return self.generateUserBinSource(None, None) is not None

    def generateUserBinSource(self, regSpec, binSpec):
        try:
            from quick.application.BoundingRegionUserBinSource import BoundingRegionUserBinSource
            return BoundingRegionUserBinSource(self._genome, self._trackName1, self._trackName2)
        except BoundingRegionsNotAvailableError:
            return None

    def helpTextForUserBinSource(self):
        core = HtmlCore()
        core.paragraph(str(HtmlCore().emphasize('Use the bounding regions of the selected '
                                                'track(s), if defined. If more than one track '
                                                'is selected, the intersection of the bounding '
                                                'regions is used, i.e. where the bounding '
                                                'regions are overlapping.')))

        core2 = HtmlCore()
        core2.divBegin(divId='help_bounding_regions', divClass='infomessagesmall help',
                      style='display: block;')
        core2.paragraph('Bounding regions are the regions where a track is defined, e.g. where '
                       'there theoretically may be data. This means that if there is no data in '
                       'a bounding region, the absence of data is informative, i.e. that the lack '
                       'of data is not just caused by not looking at the particular region. '
                       'Hence, the bounding region for most tracks should be defined without '
                       'for instance the centromeres. For tracks with no explicitly defined '
                       'bounding regions, the bounding regions are implicitly defined as all '
                       '(complete) chromosomes containing at least one track element.')
        core2.divEnd()
        core2.toggle('More information about bounding regions', styleId='help_bounding_regions')
        core.paragraph(str(core2))

        core3 = HtmlCore()
        core3.styleInfoBegin(styleClass='infomessagesmall')
        core3.descriptionLine('Note', 'Intersecting bounding regions currently only supported for '
                                      'two tracks. If using a third track or an intensity track, '
                                      'only the bounding regions of the two first tracks are '
                                      'considered.')
        core3.styleInfoEnd()
        core.paragraph(str(core3))

        self._appendChrArmNoteIfNeeded(core)

        core.hideToggle(styleId='help_bounding_regions')
        return str(core)

    def describeUserBinSource(self, regSpec, binSpec):
        if self._trackName2 is not None:
            return 'Using the intersection of the bounding regions of the tracks as bins.'
        else:
            return 'Using the bounding regions of the track as bins.'

    def validateRegAndBinSpec(self, regSpec, binSpec):
        pass

    def getZeroBinsValidationMessage(self, regSpec, binSpec):
        return 'Zero analysis bins specified. This may happen if there is no overlap between ' +\
               'the bounding regions of the selected tracks.'


class FnBasedUserBinSourceInfo(UserBinSourceInfo):
    def isAvailable(self):
        return self._getUserBinSourceFn() is not None

    def generateUserBinSource(self, regSpec, binSpec, forValidation=False):
        categoryFilterList = self._getCategoryFilterListFromBinSpec(binSpec)
        return self._getUserBinSource(categoryFilterList, forValidation)

    def describeUserBinSource(self, regSpec, binSpec):
        categoryFilterList = self._getCategoryFilterListFromBinSpec(binSpec)
        if categoryFilterList is None:
            return 'Using all ' + self.NAME + ' of genome build "' + self._genome + '" as bins'
        else:
            return 'Using the following ' + self.NAME + ' of genome build "' + self._genome + \
                '" as bins: ' + ', '.join(categoryFilterList)

    def validateRegAndBinSpec(self, regSpec, binSpec):
        pass

    def getZeroBinsValidationMessage(self, regSpec, binSpec):
        ubSource = self.generateUserBinSource(regSpec, '*', forValidation=True)

        errorStr = 'Zero analysis bins specified. '

        exampleRegs = [reg.val for reg in islice(ubSource, 3) if reg.val is not None]
        if len(exampleRegs) > 0:
            errorStr += 'This is probably caused by entering an incorrect ' +\
                        'filtering condition. Example of supported input categories: ' +\
                        ', '.join(exampleRegs)
        else:
            errorStr += 'The underlying "%s" track in the current ' % self.NAME +\
                        'genome ("%s") does not contain categorical values, ' % self._genome +\
                        'which is necessary for supporting filtering conditions. '

        return errorStr

    def _getCategoryFilterListFromBinSpec(self, binSpec):
        return None if binSpec=='*' else binSpec.replace(' ','').split(',')

    def _getUserBinSourceFn(self):
        raise AbstractClassError()

    def _getUserBinSource(self, categoryFilterList):
        raise AbstractClassError()

    @classmethod
    def protoBinSpecLabelForUserBinSource(cls):
        return 'Which:'

    @classmethod
    def protoBinSpecOptionsBoxForUserBinSource(cls):
        return '*'


class ChrUserBinSourceInfo(FnBasedUserBinSourceInfo, ChrArmNoteMixin):
    KEYS = ['__chrs__']
    NAME = 'Chromosomes'

    def _getUserBinSourceFn(self):
        return GenomeInfo.getChrRegsFn(self._genome)

    def _getUserBinSource(self, categoryFilterList, forValidation):
        stripValues = False if forValidation else True
        return GenomeInfo.getChrRegs(self._genome, categoryFilterList, stripValues=stripValues)

    def helpTextForUserBinSource(self):
        core = HtmlCore()
        self._appendChrArmNoteIfNeeded(core)
        return str(core)

    @classmethod
    def protoBinSpecHelpTextForUserBinSource(cls):
        core = HtmlCore()
        core.emphasize('Allowed values: comma separated list of chromosomes. '
                       '"*" means all chromosomes. Example: "chr1,chr3"')
        return str(core)


class ChrArmUserBinSourceInfo(FnBasedUserBinSourceInfo):
    KEYS = ['__chrArms__']
    NAME = 'Chromosome arms'

    def _getUserBinSourceFn(self):
        return GenomeInfo.getChrArmRegsFn(self._genome)

    def _getUserBinSource(self, categoryFilterList, forValidation):
        return GenomeInfo.getChrArmRegs(self._genome, categoryFilterList)

    @classmethod
    def protoBinSpecHelpTextForUserBinSource(cls):
        core = HtmlCore()
        core.emphasize('Allowed values: comma separated list of chromosome arms. '
                       '"*" means all chromosome arms. Example: "chr1p,chr1q,chr2p"')
        return str(core)


class ChrBandUserBinSourceInfo(FnBasedUserBinSourceInfo, ChrArmNoteMixin):
    KEYS = ['__chrBands__']
    NAME = 'Cytobands'

    def _getUserBinSourceFn(self):
        return GenomeInfo.getChrBandRegsFn(self._genome)

    def _getUserBinSource(self, categoryFilterList, forValidation):
        return GenomeInfo.getChrBandRegs(self._genome, categoryFilterList)

    def helpTextForUserBinSource(self):
        core = HtmlCore()
        self._appendChrArmNoteIfNeeded(core)
        return str(core)

    @classmethod
    def protoBinSpecHelpTextForUserBinSource(cls):
        core = HtmlCore()
        core.emphasize('Allowed values: comma separated list of cytobands (chromosome bands). '
                       '"*" means all cytobands. Example: "1p36.33,1p36.23"')
        return str(core)


class GeneUserBinSourceInfo(FnBasedUserBinSourceInfo):
    KEYS = ['__genes__']
    NAME = 'Ensembl genes (merged)'

    def _getUserBinSourceFn(self):
        return GenomeInfo.getStdGeneRegsFn(self._genome)

    def _getUserBinSource(self, categoryFilterList, forValidation):
        return GenomeInfo.getStdGeneRegs(self._genome, categoryFilterList)

    @classmethod
    def protoBinSpecHelpTextForUserBinSource(cls):
        core = HtmlCore()
        core.emphasize('Allowed values: comma separated list of Ensembl gene ids. '
                       '"*" means all genes. Example: "ENSG00000208234, ENSG00000199674"')
        core.styleInfoBegin(styleClass='infomessagesmall')
        core.descriptionLine('Note', 'all overlapping gene isoforms have been merged to form '
                                      '"supergenes" with positions from the start of the gene '
                                      'located most upstream, to the end of the gene located '
                                      'most downstream.')
        core.styleInfoEnd()
        return str(core)


class StdUserBinSourceInfo(UserBinSourceInfo):
    ALLOW_OVERLAPPING_USER_BINS = False

    def generateUserBinSource(self, regSpec, binSpec):
        if self.ALLOW_OVERLAPPING_USER_BINS:
            from quick.application.UserBinSource import BoundedUnMergedUserBinSource
            ubSource = BoundedUnMergedUserBinSource(regSpec, binSpec, genome=self._genome)
            #altUbSource = UserBinSource(regSpec,binSpec,genome)
            from gold.application.LogSetup import logMessage
            logMessage('NB! Using unmerged local bins - meaning that global results are not necessarily valid.')# +\
                   #'%i non-overlapping vs %i if clustered' % (len(list(ubSource )), len(list(altUbSource )) )
        else:
            from quick.application.UserBinSource import UserBinSource
            ubSource = UserBinSource(regSpec, binSpec, genome=self._genome)

        return ubSource


class BinsFromHistoryUserBinSourceInfo(StdUserBinSourceInfo):
    from gold.application.DataTypes import getSupportedFileSuffixesForBinning
    KEYS = ['file', '__history__'] + getSupportedFileSuffixesForBinning()
    NAME = 'Bins from history'

    def isAvailable(self):
        return True

    def describeUserBinSource(self, regSpec, binSpec):
        return 'Using regions from file of type "' + regSpec + \
            '" of genome build "' + self._genome + '" as bins'

    def validateRegAndBinSpec(self, regSpec, binSpec):
        if binSpec in [None, '']:
            return 'Please select a history element containing regions.'
            
        try:
            from proto.CommonFunctions import getGalaxyFnFromEncodedDatasetId
            binFn = getGalaxyFnFromEncodedDatasetId(binSpec)
        except:
            binFn = binSpec

        if not os.path.exists(binFn):
            return 'The specified file to be used for analysis regions does not exist: "%s"' % binFn

    def getZeroBinsValidationMessage(self, regSpec, binSpec):
        raise ShouldNotOccurError('The GenomeElementSource should already have raised ' \
                                  'an error about the file being empty.')

    @classmethod
    def protoBinSpecLabelForUserBinSource(cls):
        return 'Choose from history:'

    @classmethod
    def protoBinSpecOptionsBoxForUserBinSource(cls):
        from gold.application.DataTypes import getSupportedFileSuffixesForBinning
        return tuple(['__history__'] + getSupportedFileSuffixesForBinning())

    @classmethod
    def protoBinSpecHelpTextForUserBinSource(cls):
        return ''


class BinsFromTrackUserBinSourceInfo(StdUserBinSourceInfo):
    KEYS = ['track', '__track__']
    NAME = 'Bins from track'

    def isAvailable(self):
        return True

    def describeUserBinSource(self, regSpec, binSpec):
        return 'Using regions from track "' + regSpec + \
            '" of genome build "' + self._genome + '" as bins'

    def validateRegAndBinSpec(self, regSpec, binSpec):
        from quick.util.CommonFunctions import convertTNstrToTNListFormat
        from gold.description.TrackInfo import TrackInfo
        from gold.track.TrackFormat import TrackFormatReq

        trackName = convertTNstrToTNListFormat(binSpec)
        ti = TrackInfo(self._genome, trackName)

        if not ti.isValid():
            return 'The specified track is not valid: "%s"' % ':'.join(trackName)

        if not (ti.trackFormatName and TrackFormatReq(name=ti.trackFormatName).isInterval()):
            return 'The specified track does not contain regions: "%s"' % ':'.join(trackName)

    def getZeroBinsValidationMessage(self, regSpec, binSpec):
        raise ShouldNotOccurError('The specified track does not contain any regions')


class CustomSpecUserBinSourceInfo(StdUserBinSourceInfo, ChrArmNoteMixin):
    KEYS = ['__custom__']
    NAME = 'Custom specification'

    def isAvailable(self):
        return True

    def helpTextForUserBinSource(self):
        core = HtmlCore()
        self._appendChrArmNoteIfNeeded(core)
        return str(core)

    def describeUserBinSource(self, regSpec, binSpec):
        from quick.application.UserBinSource import parseRegSpec
        from quick.util.CommonFunctions import strWithStdFormatting, \
            generateStandardizedBpSizeText, parseShortenedSizeSpec
        from quick.util.GenomeInfo import GenomeInfo

        regions = parseRegSpec(regSpec, self._genome)
        if len(regions) == 1:
            region = regions[0]
            regStr = ' chromosome ' + region.chr +\
                     ' of genome build "' + self._genome + '"' +\
                     ((' from position ' + strWithStdFormatting(region.start+1) + ' to ' + \
                        strWithStdFormatting(region.end)) if not region.isWholeChr() else '')
        else:
            if all(region.chr is None or region.isWholeChr() for region in regions):
                regionChrs = set([region.chr for region in regions])
                allChrs = set(GenomeInfo.getChrList(self._genome))
                if len(regions) == len(allChrs) and regionChrs == allChrs:
                    regStr = ' all chromosomes'
                else:
                    regStr = ' chromosomes ' + ', '.join(region.chr for region in regions)
            else:
                regStr = ' %s regions' % len(regions)
            regStr += ' of genome build "%s"' % self._genome

        return 'Using' + regStr +\
                ((', divided into intervals of size ' +\
                generateStandardizedBpSizeText( parseShortenedSizeSpec( binSpec ) ) + ',') if binSpec != '*' else '') +\
                ' as bins'

    def validateRegAndBinSpec(self, regSpec, binSpec):
        from quick.util.CommonFunctions import parseShortenedSizeSpec
        from quick.application.UserBinSource import parseRegSpec

        try:
            parseRegSpec(regSpec, self._genome)
            if binSpec != '*':
                parseShortenedSizeSpec(binSpec)
        except Exception, e:
            return str(e)

        return ''

    def getZeroBinsValidationMessage(self, regSpec, binSpec):
        raise ShouldNotOccurError('The region specification "%s" does not ' % regSpec +
                                  ' describe any real regions')

    @classmethod
    def protoRegSpecLabelForUserBinSource(cls):
        return 'Regions of the genome:'

    @classmethod
    def protoRegSpecOptionsBoxForUserBinSource(cls):
        return '*'

    @classmethod
    def protoRegSpecHelpTextForUserBinSource(cls):
        core = HtmlCore()
        core.emphasize('Allowed values: region specification as in UCSC Genome browser '
                       '(with 1 as the first position). "*" means the '
                       'whole genome, and "k" and "m" denotes thousand and million bps, '
                       'respectively. Several regions may be specified if separated by comma. '
                       'If the end position is omitted, it is set equal to the end of the '
                       'chromosome. Example: "chr1:1-20m, chr2:10m-"')
        return str(core)

    @classmethod
    def protoBinSpecLabelForUserBinSource(cls):
        return 'Bin size:'

    @classmethod
    def protoBinSpecOptionsBoxForUserBinSource(cls):
        return '*'

    @classmethod
    def protoBinSpecHelpTextForUserBinSource(cls):
        core = HtmlCore()
        core.emphasize('Allowed values: any number (integer). The selected regions are divided '
                       'into bins of this size. "k" and "m" denotes thousand and million bps, '
                       'respectively. "*" means the whole region / chromosome. '
                       'Example: "100k"')
        return str(core)


# UserBinSourceRegistry

ALL_UB_SOURCE_INFO_CLS = [BoundingRegionUserBinSourceInfo,
                          ChrUserBinSourceInfo,
                          ChrArmUserBinSourceInfo,
                          ChrBandUserBinSourceInfo,
                          GeneUserBinSourceInfo,
                          BinsFromHistoryUserBinSourceInfo,
                          BinsFromTrackUserBinSourceInfo,
                          CustomSpecUserBinSourceInfo]


class UserBinSourceRegistry(object):
    _ALL_UB_SOURCE_INFO_CLS_DICT = {}
    for ubInfoCls in ALL_UB_SOURCE_INFO_CLS:
        for key in ubInfoCls.KEYS:
            _ALL_UB_SOURCE_INFO_CLS_DICT[key] = ubInfoCls

    _DEFAULT_KEY_WHEN_NO_MATCH = '__custom__'

    def __init__(self, genome, trackNameList, **kwArgs):
        self._ubSourceInfoDict = OrderedDict()
        self._ubSourceInfoDictFromName = OrderedDict()

        assert genome is not None

        from quick.util.GenomeInfo import GenomeInfo
        if not GenomeInfo(genome).isInstalled():
            raise InvalidFormatError('The specified genome "%s" is not installed.' % genome)
        
        for key in self._ALL_UB_SOURCE_INFO_CLS_DICT:
            ubSourceInfo = self._ALL_UB_SOURCE_INFO_CLS_DICT[key](genome, trackNameList, **kwArgs)
            if ubSourceInfo.isAvailable():
                self._ubSourceInfoDictFromName[ubSourceInfo.NAME] = ubSourceInfo
                self._ubSourceInfoDict[key] = ubSourceInfo

    def _getOrderOfUserBinKeysForSelection(self):
        return ['__chrs__', '__chrArms__', '__chrBands__', '__genes__', '__brs__', '__custom__', '__history__']

    def getNamesOfAllUserBinSourcesForSelection(self):
        return [self._ubSourceInfoDict[key].NAME for key in self._getOrderOfUserBinKeysForSelection() \
                if key in self._ubSourceInfoDict]

    def getNameAndKeyTuplesOfAllUserBinSources(self):
        return [(self._ubSourceInfoDict[key].NAME, key) for key in self._getOrderOfUserBinKeysForSelection() \
                if key in self._ubSourceInfoDict]

    def getUserBinSourceInfoFromName(self, name):
        # raise Exception(name, repr(self._ubSourceInfoDictFromName))
        return self._ubSourceInfoDictFromName.get(name)

    def _getUserBinSourceInfo(self, regSpec):
        ubSourceInfo = self._ubSourceInfoDict.get(regSpec)
        if ubSourceInfo is None:
            if regSpec in self._ALL_UB_SOURCE_INFO_CLS_DICT.keys():
                name = self._ALL_UB_SOURCE_INFO_CLS_DICT[regSpec].NAME
                raise InvalidFormatError('Cannot create user bins of type: "%s", as it is not ' % name +\
                                         'available for the selected genome and tracks (if any).')
            else:
                ubSourceInfo = self._ubSourceInfoDict[self._DEFAULT_KEY_WHEN_NO_MATCH]

        return ubSourceInfo

    def getUserBinSource(self, regSpec, binSpec):
        ubSourceInfo = self._getUserBinSourceInfo(regSpec)
        
        try:
            ubSource = ubSourceInfo.generateUserBinSource(regSpec, binSpec)
            ubSource.description = ubSourceInfo.describeUserBinSource(regSpec, binSpec)
            return ubSource
        except Exception, e:
            raise InvalidFormatError('Unable to parse region specification. Error message: "%s"' % e)

    def validateRegAndBinSpec(self, regSpec, binSpec):
        ubSourceInfo = self._getUserBinSourceInfo(regSpec)
        errorString = ubSourceInfo.validateRegAndBinSpec(regSpec, binSpec)
        
        if errorString:
            return "Error in specification of analysis regions: " + errorString

        try:
            ubSource = self.getUserBinSource(regSpec, binSpec)
            hasBins = any(bin for bin in ubSource)

            if not hasBins:
                errorString = ubSourceInfo.getZeroBinsValidationMessage(regSpec, binSpec)
        
        except Exception as e:
            from gold.application.LogSetup import logException
            logException(e)
            errorString = "Error fetching genome region using the specification of analysis regions: %s" % e

        return errorString


class UserBinSourceRegistryForDescriptiveStats(UserBinSourceRegistry):
    pass


class UserBinSourceRegistryForHypothesisTests(UserBinSourceRegistry):
    def __init__(self, genome, trackNameList=[], **kwArgs):
        super(UserBinSourceRegistryForHypothesisTests, self). \
            __init__(genome, trackNameList, forHypothesisTest=True, **kwArgs)

    def _getOrderOfUserBinKeysForSelection(self):
        return ['__chrArms__', '__chrs__', '__chrBands__', '__genes__', '__brs__', '__custom__', '__history__']


class UserBinSourceRegistryForExtraction(UserBinSourceRegistry):
    def _getOrderOfUserBinKeysForSelection(self):
        return ['__brs__', '__chrs__', '__chrArms__', '__chrBands__', '__genes__', '__custom__', '__history__']


def getNameAndProtoRegSpecLabelsForAllUserBinSources():
    return [(ubiCls.NAME, ubiCls.protoRegSpecLabelForUserBinSource())
            for ubiCls in ALL_UB_SOURCE_INFO_CLS
            if ubiCls.protoRegSpecLabelForUserBinSource() is not None]


def getNameAndProtoBinSpecLabelsForAllUserBinSources():
    return [(ubiCls.NAME, ubiCls.protoBinSpecLabelForUserBinSource())
            for ubiCls in ALL_UB_SOURCE_INFO_CLS
            if ubiCls.protoBinSpecLabelForUserBinSource() is not None]
