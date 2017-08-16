from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import RatioDictSingleDenomStatUnsplittable
from quick.statistic.BinSizeStat import BinSizeStat

class GenericProportionalToBinSizeStat(MagicStatFactory):
    pass

#class ThreeWayProportionalBpOverlapStatSplittable(StatisticSumResSplittable):
#    pass
            
class GenericProportionalToBinSizeStatUnsplittable(RatioDictSingleDenomStatUnsplittable):        
    #def _compute(self):
    #    pass
    
    def _createChildren(self):
        rawStat = self.getRawStatisticClass( self._kwArgs['rawStatistic'] )
        self._addChild( rawStat(self._region, self._track, self._track2 if hasattr(self, '_track2') else None, **self._kwArgs) )
        self._addChild( BinSizeStat(self._region, self._track) )
        
