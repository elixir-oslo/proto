from config.Config import DebugConfig
from gold.track.GenomeRegion import GenomeRegion
from gold.track.RandomizedTrack import RandomizedTrack
from quick.util.GenomeInfo import GenomeInfo
from gold.util.CustomExceptions import CentromerError, TooLargeBinError
from gold.statistic.RawDataStat import RawDataStat
from gold.util.RandomUtil import random
from copy import copy
from gold.util.CommonFunctions import getClassName

class RandomGenomeLocationTrack(RandomizedTrack):
    MIN_SOURCE_TO_SAMPLE_SIZE_RATIO = 4#10
    WORKS_WITH_MINIMAL = False

    def _getTrackView(self, region):
        #if not hasattr(self, '_minimalRegion'):
        #    from quick.application.UserBinSource import MinimalBinSource
        #    minimalBinList = MinimalBinSource(region.genome)
        #    self._minimalRegion = minimalBinList[0] if minimalBinList is not None else None
        #
        #if  self._minimalRegion == region:
        #    return self._origTrack.getTrackView(region)

        allChrArmRegs = GenomeInfo.getContainingChrArms(region)
        if len(allChrArmRegs) != 1:
            raise CentromerError
        chrArm = allChrArmRegs[0]

        buffer = self._getIndependencyBufferSize(region)
        sourceRegs = chrArm.exclude( region.getCopy().extend(-buffer).extend(buffer) )
        assert len(sourceRegs) in [1,2], "Source region must be smaller than a tenth of a chromosome arm: %s" % region

        if not any(len(sourceReg) >= self.MIN_SOURCE_TO_SAMPLE_SIZE_RATIO * len(region) for sourceReg in sourceRegs):
            raise TooLargeBinError('Source region lengths of ' + str([len(x) for x in sourceRegs]) +
                                   ' are too small compared to region length of ' + str(len(region)) +
                                   ' according to MIN_SOURCE_TO_SAMPLE_SIZE_RATIO: ' + str(self.MIN_SOURCE_TO_SAMPLE_SIZE_RATIO))

        if len(sourceRegs) == 1:
            sourceReg = sourceRegs[0]
        else:
            firstSourceProportion = (len(sourceRegs[0])-len(region)) / sum(len(sourceRegs[i])-len(region) for i in range(2))
            sourceReg = sourceRegs[0] if random.random() < firstSourceProportion else sourceRegs[1]

        randOffset = random.randint( 0, len(sourceReg) - len(region) )
        start = sourceReg.start + randOffset
        end = start + len(region)
        randRegion = GenomeRegion(region.genome, region.chr, start, end)

        #rawData = RawDataStat(randRegion, self._origTrack, self._trackFormatReq)
        #tv = rawData.getResult()
        tv = self._origTrack.getTrackView(randRegion)
        assert tv.genomeAnchor != region, (region, tv.genomeAnchor, getClassName(region), getClassName(tv.genomeAnchor))
        return tv

    def _getIndependencyBufferSize(self, region):
        return 1 * len(region)
