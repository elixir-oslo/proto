from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import  RatioStatUnsplittable
from gold.statistic.SumOverCoveredBpsStat import SumOverCoveredBpsStat
from quick.statistic.BinSizeStat import BinSizeStat

class MeanOverCoveredBpsStat(MagicStatFactory):
    pass

class MeanOverCoveredBpsStatUnsplittable(RatioStatUnsplittable):    
    def _createChildren(self):
        self._addChild(SumOverCoveredBpsStat(self._region, self._track))
        self._addChild(BinSizeStat(self._region, self._track))
