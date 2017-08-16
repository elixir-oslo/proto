from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import RatioDictSingleDenomStatUnsplittable
from quick.statistic.BinSizeStat import BinSizeStat
from quick.statistic.MultitrackBpOverlapStat import MultitrackBpOverlapStat

class ThreeWayProportionalBpOverlapStat(MagicStatFactory):
    pass

#class ThreeWayProportionalBpOverlapStatSplittable(StatisticSumResSplittable):
#    pass
            
class ThreeWayProportionalBpOverlapStatUnsplittable(RatioDictSingleDenomStatUnsplittable):        
    #def _compute(self):
    #    pass
    
    def _createChildren(self):
#         self._addChild( ThreeWayBpOverlapStat(self._region, self._track, self._track2, **self._kwArgs) )
        self._addChild( MultitrackBpOverlapStat(self._region, self._track, self._track2, **self._kwArgs) )
        self._addChild( BinSizeStat(self._region, self._track) )
        
