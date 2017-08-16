from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import RatioStatUnsplittable
from gold.statistic.CountPointStat import CountPointStat
from gold.statistic.SumAtPointsStat import SumAtPointsStat

class MeanValAtPointsStat(MagicStatFactory):
    pass

#class MeanValAtPointsSplittable(StatisticSumResSplittable):
#    pass
            
class MeanValAtPointsStatUnsplittable(RatioStatUnsplittable):    
    def _createChildren(self):
        self._addChild(SumAtPointsStat(self._region, self._track, self._track2))
        self._addChild(CountPointStat(self._region, self._track))
