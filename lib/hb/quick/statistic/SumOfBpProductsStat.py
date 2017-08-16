from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import numpy

class SumOfBpProductsStat(MagicStatFactory):
    pass

#class SumOfBpProductsStatSplittable(StatisticSumResSplittable):
#    pass
            
class SumOfBpProductsStatUnsplittable(Statistic):    
    def _compute(self):
        a1 = self._children[0].getResult().valsAsNumpyArray()
        a2 = self._children[1].getResult().valsAsNumpyArray()
        #return (a1*a2).sum(dtype='float64')
        return numpy.inner(a1,a2)
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='number', dense=True)) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(val='number', dense=True)) )
