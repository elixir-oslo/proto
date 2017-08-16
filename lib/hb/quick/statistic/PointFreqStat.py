from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import RatioStatUnsplittable
from gold.statistic.CountPointStat import CountPointStat
from quick.statistic.BinSizeStat import BinSizeStat

class PointFreqStat(MagicStatFactory):
    pass

class PointFreqStatUnsplittable(RatioStatUnsplittable):
    def _createChildren(self):
        self._addChild( CountPointStat(self._region, self._track) )
        self._addChild( BinSizeStat(self._region, self._track) )
