from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class SumOfSquaresInsideStat(MagicStatFactory):
    pass

class SumOfSquaresInsideStatSplittable(StatisticSumResSplittable):
    pass

class SumOfSquaresInsideStatUnsplittable(Statistic):    
    def _compute(self):
        numData = self._children[1].getResult().valsAsNumpyArray()
        sumInside = numData.dtype.type(0)
        for el in self._children[0].getResult():
            vec = numData[el.start():el.end()]
            sumInside += (vec*vec).sum(dtype='float64')
        return sumInside
        
    def _createChildren(self):
        rawSegDataStat = RawDataStat(self._region, self._track, TrackFormatReq(interval=True, dense=False))
        rawNumDataStat = RawDataStat(self._region, self._track2, TrackFormatReq(dense=True, val='number', interval=False))
        self._addChild(rawSegDataStat)
        self._addChild(rawNumDataStat)
