from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import ShouldNotOccurError
import numpy

class MarksAggregationStat(MagicStatFactory):
    "Returns an aggregate operation performed on all marks in the bin, e.g. sum/max/min/mean of marks"
    pass

class MarksAggregationStatSplittable(StatisticSumResSplittable):    
    pass

class MarksAggregationStatUnsplittable(Statistic):    
    def __init__(self, region, track, track2, aggregateOperation=None, **kwArgs):
        self._aggregateOperation = aggregateOperation
        Statistic.__init__(self, region, track, track2, aggregateOperation=aggregateOperation, **kwArgs)
        
    def _compute(self):
        array = self._children[0].getResult().valsAsNumpyArray()
        if len(array)==0:
            return numpy.nan
        assert array.dtype == "float32" or array.dtype == "float64"
        if self._aggregateOperation == 'sum':
            return float(array.sum(dtype="float64")) #accumulator must be 64-bit or rounding errors occur
        elif self._aggregateOperation == 'min':
            return float(array.min())
        elif self._aggregateOperation == 'max':
            res = float(array.max())
            #assert not any([v.isnan() for v in ])
            return res
        else:
            raise ShouldNotOccurError()
    
    def _createChildren(self):        
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='number')) )
