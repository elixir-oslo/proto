from gold.util.CommonFunctions import parseShortenedSizeSpec
from gold.util.CustomExceptions import ShouldNotOccurError, InvalidFormatError
from config.Config import DEFAULT_GENOME
from gold.origdata.GenomeElementSorter import GenomeElementSorter
from gold.application.DataTypes import getSupportedFileSuffixesForBinning

## Helper methods

def parseRegSpec(regSpec, genome = None):
    from gold.track.GenomeRegion import GenomeRegion
    from quick.util.GenomeInfo import GenomeInfo

    class SimpleUserBinSource(list):
        pass

    regions = []
    allRegSpecs = regSpec.strip().split(',')
    for curRegSpec in allRegSpecs:
        regParts = curRegSpec.strip().split(':')
        if genome == None:
            genome = regParts[0]
            assert GenomeInfo(genome).isInstalled(), "Specified genome is not installed: %s" % genome

        if not (regParts[0]=='*' or regParts[0] in GenomeInfo.getExtendedChrList(genome)):
            assert regParts[0] == genome, \
                "Region specification does not start with one of '*' or correct chromosome or genome name. Region specification: %s. Genome: %s" % (curRegSpec, genome)
            #genome = regParts[0]
            regParts = regParts[1:]

        if regParts[0] == '*':
            assert len(regParts) == 1, \
                "Region specification starts with '*' but continues with ':'. Region specification: %s" % curRegSpec
            assert len(allRegSpecs) == 1, \
                "Region specification is '*', but is in a list with other region specifications: %s" % regSpec
            for chr in GenomeInfo.getChrList(genome):
                regions.append(GenomeRegion(genome, chr, 0, GenomeInfo.getChrLen(genome, chr)))
        else:
            assert regParts[0] in GenomeInfo.getExtendedChrList(genome), \
                "Region specification does not start with chromosome specification. Region specification: %s " % curRegSpec
            chr = regParts[0]
            try:
                chrLen = GenomeInfo.getChrLen(genome, chr)
            except Exception, e:
                raise InvalidFormatError("Chromosome '%s' does not exist for genome '%s'" % (chr, genome))

            if len(regParts)>1:
                posParts = regParts[1]
                assert '-' in posParts, \
                    "Position specification does not include character '-'. Region specification: %s " % curRegSpec
                rawStart, rawEnd = posParts.split('-')

                start = int(rawStart.replace('k','001').replace('m','000001'))
                end = int(rawEnd.replace('k','000').replace('m','000000')) if rawEnd != '' else chrLen
                assert start >= 1, \
                    "Start position is not positive. Region specification: %s " % curRegSpec
                assert end >= start, \
                    "End position is not larger than start position. Region specification: %s " % curRegSpec
                assert end <= chrLen, \
                    "End position is larger than chromosome size. Genome: %s. Chromosome size: %s. Region specification: %s" % (genome, chrLen, curRegSpec)
                #-1 for conversion from 1-indexing to 0-indexing end-exclusive
                start-=1

            else:
                start,end = 0, chrLen
            regions.append( GenomeRegion(genome, chr, start, end) )
    ubSource = SimpleUserBinSource(regions)
    ubSource.genome = genome
    return ubSource

## Classes

class BinSource(object):
    '''Root class of all bin sources.
    Subclasses are expected to offer iteration of GenomeRegion-objects, but this is not per now in any way enforced.
    Similarly, subclasses are expected to have an attribute genome of type str.
    '''
    pass

class UserBinSource(BinSource):
    '''Possible definitions of UserBinSource, based on (regSpec,binSpec)-tuple:
    ('file',fn) where instead of 'file', a more specific filetype such as 'bed' could be specified
    (chrReg,binSize) where chrReg is a Region specification as in UCSC Genome browser (string), 
    or '*' to denote whole genome, and where binSize is a number specifying length of each bin that the region should be split into.
    '''
    def __new__(cls, regSpec, binSpec, genome=None, categoryFilterList=None, strictMatch=True):
        if regSpec in ['file', 'track'] + getSupportedFileSuffixesForBinning():
            if genome is None:
                genome = DEFAULT_GENOME

            from gold.origdata.GenomeElementSource import GenomeElementSource
            if regSpec == 'track':
                from quick.util.CommonFunctions import convertTNstrToTNListFormat
                from gold.origdata.TrackGenomeElementSource import FullTrackGenomeElementSource
                trackName = convertTNstrToTNListFormat(binSpec)
                geSource = FullTrackGenomeElementSource(genome, trackName, allowOverlaps=False)
            else:
                from quick.application.ExternalTrackManager import ExternalTrackManager
                try:
                    fn = ExternalTrackManager.getGalaxyFnFromEncodedDatasetId(binSpec)
                except:
                    fn = binSpec
                geSource = GenomeElementSource(fn, genome=genome,
                                               suffix=regSpec if regSpec != 'file' else None)

            if categoryFilterList is not None:
                from gold.origdata.GECategoryFilter import GECategoryFilter
                geSource = GECategoryFilter(geSource, categoryFilterList, strict=strictMatch)
            return cls._applyEnvelope(geSource)
        else:
            if binSpec == '*':
                binSize = None
            else:
                binSize = parseShortenedSizeSpec(binSpec)

            from quick.application.AutoBinner import AutoBinner
            return AutoBinner(parseRegSpec(regSpec, genome), binSize)

    @staticmethod
    def _applyEnvelope(geSource):
        from quick.origdata.GERegionBoundaryFilter import GERegionBoundaryFilter
        from gold.origdata.GEOverlapClusterer import GEOverlapClusterer
        return GERegionBoundaryFilter(GEOverlapClusterer(GenomeElementSorter(geSource)), GlobalBinSource(geSource.genome))

class UnBoundedUserBinSource(UserBinSource):
    @staticmethod
    def _applyEnvelope(geSource):
        from gold.origdata.GEOverlapClusterer import GEOverlapClusterer
        return GEOverlapClusterer(GenomeElementSorter(geSource))

class UnBoundedUnClusteredUserBinSource(UserBinSource):
    @staticmethod
    def _applyEnvelope(geSource):
        return GenomeElementSorter(geSource)

class ValuesStrippedUserBinSource(UserBinSource):
    @staticmethod
    def _applyEnvelope(geSource):
        from gold.origdata.GEMarkRemover import GEMarkRemover
        return GenomeElementSorter(GEMarkRemover(geSource))

class BoundedUnMergedUserBinSource(UserBinSource):
    @staticmethod
    def _applyEnvelope(geSource):
        from quick.origdata.GERegionBoundaryFilter import GERegionBoundaryFilter
        return GERegionBoundaryFilter(GenomeElementSorter(geSource), GlobalBinSource(geSource.genome) )

class UnfilteredUserBinSource(UserBinSource):
    @staticmethod
    def _applyEnvelope(geSource):
        return geSource

class GlobalBinSource(BinSource):
    def __new__(cls, genome):
        return UserBinSource(genome+':*','*')

class MinimalBinSource(BinSource):
    def __new__(cls, genome):
        from gold.track.GenomeRegion import GenomeRegion
        from quick.util.GenomeInfo import GenomeInfo
        chrList = GenomeInfo.getChrList(genome)
        if len(chrList) > 0:
            return [GenomeRegion(genome, GenomeInfo.getChrList(genome)[0], 0, 1)]

class PairedGenomeRegion(BinSource):
    def __init__(self, firstRegion, secondRegion):
        assert firstRegion.genome == secondRegion.genome
        self.genome = firstRegion.genome
        self.first = firstRegion
        self.second = secondRegion

    def __eq__(self, other):
        return self.first == other.first and self.second == other.second

    def __hash__(self):
        return hash((self.first, self.second))

    def __str__(self):
        return '(%s, %s)' % (self.first, self.second)

    def strWithCentromerInfo(self):
        return '(%s, %s)' % (self.first.strWithCentromerInfo(), \
                             self.second.strWithCentromerInfo())

    def strShort(self):
        return '(%s, %s)' % (self.first.strShort(), \
                             self.second.strShort())


class AllCombinationsUserBinSource(BinSource):
    def __init__(self, userBinSource):
        self._userBinSource = userBinSource

    def __iter__(self):
        import itertools
        for binPair in itertools.combinations_with_replacement(self._userBinSource, 2):
            yield PairedGenomeRegion(binPair[0], binPair[1])

#A plain bin source, to be e.g. used when calling HB as an API
class RegionIter(BinSource):
    #@takes(list)
    def __init__(self, regs):
        assert len(regs)>0        
        self.genome = regs[0].genome
        list.__init__(self, regs)
