from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.DiffOfMeanInsideOutsideStat import DiffOfMeanInsideOutsideStatUnsplittable
from gold.statistic.CountStat import CountStat
from gold.statistic.SumAtPointsStat import SumAtPointsStat
from gold.statistic.SumStat import SumStat

class DiffOfMeansAtPointsVsRemainingStat(MagicStatFactory):
    pass
            
class DiffOfMeansAtPointsVsRemainingStatUnsplittable(DiffOfMeanInsideOutsideStatUnsplittable):
    def _createChildren(self):
        self._addChild(SumAtPointsStat(self._region, self._track, self._track2))
        self._addChild(CountStat(self._region, self._track))
        self._addChild(SumStat(self._region, self._track2))
        self._addChild(CountStat(self._region, self._track2))
