from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import RatioStatUnsplittable
from gold.statistic.SumInsideStat import SumInsideStat
from gold.statistic.CountStat import CountStat

class MeanInsideStat(MagicStatFactory):
    pass

class MeanInsideStatUnsplittable(RatioStatUnsplittable):    
    def _createChildren(self):
        self._addChild( SumInsideStat(self._region, self._track, self._track2) )
        self._addChild( CountStat(self._region, self._track) )
