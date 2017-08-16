from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.SimpleExpectedBpOverlapStat import SimpleExpectedBpOverlapStat
from gold.statistic.Statistic import DivideByZeroAvoidingRatioStatUnsplittable

class SimpleObservedToExpectedBpOverlapStat(MagicStatFactory):
    pass
            
class SimpleObservedToExpectedBpOverlapStatUnsplittable(DivideByZeroAvoidingRatioStatUnsplittable):
    
    def _createChildren(self):
        from quick.statistic.StatFacades import TpRawOverlapStat
        self._addChild( TpRawOverlapStat(self._region, self._track, self._track2) )
        self._addChild( SimpleExpectedBpOverlapStat(self._region, self._track, self._track2) )

