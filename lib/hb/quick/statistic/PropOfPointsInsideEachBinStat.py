from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.CountPointStat import CountPointStat
from quick.statistic.PropOfSegmentsInsideEachBinStat import PropOfSegmentsInsideEachBinStatUnsplittable

class PropOfPointsInsideEachBinStat(MagicStatFactory):
    "For each bin, return the proportion of all points that falls within that specific bin. "
    "This means that if the bins cover the whole genome, the results across all bins will sum to one"
    
class PropOfPointsInsideEachBinStatUnsplittable(PropOfSegmentsInsideEachBinStatUnsplittable):    
    def _createChildren(self):
        globCount1 = CountPointStat(self._globalSource , self._track)
        binCount1 = CountPointStat(self._region, self._track)

        self._addChild(globCount1)
        self._addChild(binCount1)            
