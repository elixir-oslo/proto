from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.CountPerBinStat import CountPerBinStat
from quick.statistic.GenericRelativeToGlobalStat import GenericRelativeToGlobalStatUnsplittable

class RankOfCountPerBinStat(MagicStatFactory):
    "Statistic description"
    pass

class RankOfCountPerBinStatUnsplittable(Statistic):
    def __init__(self, region, track, track2=None, minimal=False, **kwArgs):
        self._globalSource = GenericRelativeToGlobalStatUnsplittable.getGlobalSource('userbins', region.genome, minimal)
        super(self.__class__, self).__init__(region, track, track2, minimal=minimal, **kwArgs)
        
    def _compute(self):
        localVal = self._localCount.getResult()[0]
        globalVals = self._allGlobalCounts.getResult()
        
        return [sum(x>localVal for x in globalVals) + 1]
    
    def _createChildren(self):
        self._localCount = self._addChild( CountPerBinStat(self._region, self._track))
        self._allGlobalCounts = self._addChild( CountPerBinStat(self._globalSource, self._track))

from gold.statistic.Statistic import StatisticConcatResSplittable
class RankOfCountPerBinStatSplittable(StatisticConcatResSplittable):
    pass
# 
