from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.DiffOfMeanInsideOutsideStat import DiffOfMeanInsideOutsideStat
from quick.statistic.AggregateOfStepFunctionBpsInSegmentsStat import AggregateOfStepFunctionBpsInSegmentsStat

class AggregateOfStepFunctionBpsVsSegmentsStat(MagicStatFactory):
    pass

class AggregateOfStepFunctionBpsVsSegmentsStatUnsplittable(Statistic):
    def _init(self, method='sum_of_sum', **kwArgs):
        self._method = method
            
    def _compute(self):
        return self._children[0].getResult()
    
    def _createChildren(self):
        if self._method == 'diff_of_mean':
            self._addChild( DiffOfMeanInsideOutsideStat(self._region, self._track2, self._track) )
        else:
            self._addChild( AggregateOfStepFunctionBpsInSegmentsStat(self._region, self._track, self._track2) )
