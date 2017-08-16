from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class SumOfSquaresStat(MagicStatFactory):
    pass

class SumOfSquaresStatSplittable(StatisticSumResSplittable):    
    pass

class SumOfSquaresStatUnsplittable(Statistic):    
    def _compute(self):
        vec = self._children[0].getResult().valsAsNumpyArray()
        return (vec*vec).sum(dtype='float64')
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='number', dense=True, interval=False)) )
