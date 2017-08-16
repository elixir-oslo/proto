from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import RatioDictSingleDenomStatUnsplittable
from quick.statistic.BinSizeStat import BinSizeStat
from quick.statistic.ThreeWayBpOverlapVegardAndKaiVersionWrapperStat \
import ThreeWayBpOverlapVegardAndKaiVersionWrapperStat

class ThreeWayProportionalBpOverlapKaiAndVegardStat(MagicStatFactory):
    pass

#class ThreeWayProportionalBpOverlapStatSplittable(StatisticSumResSplittable):
#    pass
            
class ThreeWayProportionalBpOverlapKaiAndVegardStatUnsplittable(RatioDictSingleDenomStatUnsplittable):        
    #def _compute(self):
    #    pass
    
    def _createChildren(self):
        self._addChild( ThreeWayBpOverlapVegardAndKaiVersionWrapperStat(self._region, self._track, self._track2, **self._kwArgs) )
        self._addChild( BinSizeStat(self._region, self._track) )
        
