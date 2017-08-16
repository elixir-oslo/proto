from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from quick.statistic.BinSizeStat import BinSizeStat
from gold.track.TrackFormat import TrackFormatReq

class RelPositionsInBinStat(MagicStatFactory):
    pass

class RelPositionsInBinStatSplittable(StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable):
    IS_MEMOIZABLE = False

class RelPositionsInBinStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    
    def _compute(self):
        bpSize = self._children[1].getResult()
        rawRelPositions = self._children[0].getResult().startsAsNumpyArray()/float(bpSize)
        if self._region.strand == False:
            return 1.0-rawRelPositions
        else:
            return rawRelPositions

            
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(interval=False, dense=False) ) )
        self._addChild(BinSizeStat(self._region, self._track))
