from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.BinSizeStat import BinSizeStat
from quick.statistic.AggregateOfCoveredBpsInSegmentsStat import AggregateOfCoveredBpsInSegmentsStat
from gold.statistic.SumOverCoveredBpsStat import SumOverCoveredBpsStat
from gold.statistic.CountStat import CountStat
from gold.statistic.RawOverlapStat import RawOverlapStat
import numpy

class MeanInsideOutsideStat(MagicStatFactory):
    pass

#class MeanInsideOutsideStatSplittable(StatisticSumResSplittable):
#    pass

class MeanInsideOutsideStatUnsplittable(Statistic):
    def _init(self, missingVals='treatAsZero', **kwArgs):
        assert( missingVals in ['treatAsZero','exclude'])
        self._missingVals = missingVals
    
    def _compute(self):
        sumInside = self._children[0].getResult()
        sumTotal = self._children[1].getResult()
        res = self._children[4].getResult()
        lengthInside = self._children[2].getResult() if self._missingVals == 'treatAsZero' else  res['Both']
        lengthTotal = self._children[3].getResult() if self._missingVals == 'treatAsZero' else  res['Only2'] + res['Both']
        
        
        meanInside = sumInside / lengthInside if lengthInside>0 else numpy.nan
        meanOutside = (sumTotal-sumInside) / (lengthTotal-lengthInside) if lengthTotal!= lengthInside else numpy.nan
        
        return {'MeanInsideSegments':meanInside, 'MeanOutsideSegments':meanOutside}
        
    def _createChildren(self):
        #self._track: defines inside vs outside
        #self._track2: provides values
        self._addChild(AggregateOfCoveredBpsInSegmentsStat(self._region,  self._track2, self._track, method='sum_of_sum'))
        self._addChild(SumOverCoveredBpsStat(self._region, self._track2))
        self._addChild(CountStat(self._region, self._track))
        self._addChild(BinSizeStat(self._region, self._track))
        self._addChild( RawOverlapStat(self._region, self._track, self._track2) )
