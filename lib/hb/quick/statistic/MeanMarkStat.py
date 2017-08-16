import ast

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import math

class MeanMarkStat(MagicStatFactory):
    pass

#class MeanMarkStatSplittable(StatisticSumResSplittable):
#    pass

class MeanMarkStatUnsplittable(Statistic):
    def _init(self, logScale='True', **kwArgs):
        assert logScale in ['False', 'True']
        self._logScale = ast.literal_eval(logScale)


    def _compute(self):
        #return float(self._children[0].getResult().valsAsNumpyArray().mean(dtype='float64'))
        vals = self._children[0].getResult().valsAsNumpyArray()
        if vals is None or len(vals) == 0:
            #print 'mean value is None'
            return None
        else:
            meanVal = float(vals.mean(dtype='float64'))
            #print 'mean value', meanVal
            if self._logScale:
                return math.log(meanVal, 2) if meanVal != 0 else 0
            else:
                return meanVal

    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='number', dense=False, interval=False)) )
