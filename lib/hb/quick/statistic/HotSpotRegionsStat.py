from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.RankOfCountPerBinStat import RankOfCountPerBinStat

class HotSpotRegionsStat(MagicStatFactory):
    "Statistic description"
    pass

class HotSpotRegionsStatUnsplittable(Statistic):
    def _init(self, numberOfTopHotSpots='', **kwArgs):
        if numberOfTopHotSpots!='':
            self._numberOfTopHotSpots = numberOfTopHotSpots
    
    def _compute(self):
        #numberOfBins = len(list(self._globalSource))   
        return [[str(self._region), self._localCount.getResult()[0]]]
        
#         if (self._localCount.getResult()[0] <= self._numberOfTopHotSpots):
#             return [self._region]
#             #return [self._localCount.getResult()[0], self._numberOfTopHotSpots]
#         else:
#             return []        
        
    
    def _createChildren(self):
        self._localCount = self._addChild( RankOfCountPerBinStat(self._region, self._track))
        #self._allGlobalCounts = self._addChild( RankOfCountPerBinStat(self._globalSource, self._track))

from gold.statistic.Statistic import StatisticConcatResSplittable
class HotSpotRegionsStatSplittable(StatisticConcatResSplittable):
    pass
