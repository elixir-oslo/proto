from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class SumAtPointsStat(MagicStatFactory):
    pass

class SumAtPointsStatSplittable(StatisticSumResSplittable):
    pass
            
class SumAtPointsStatUnsplittable(Statistic):    
    def _compute(self):
        pointData = self._children[0].getResult().startsAsNumpyArray()
        if len(pointData)==0:
            return 0
        
        numData = self._children[1].getResult().valsAsNumpyArray()
        return numData[pointData].sum(dtype='float64')
    
    def _createChildren(self):
        rawPointsDataStat = RawDataStat(self._region, self._track, TrackFormatReq(interval=False, dense=False))
        rawNumDataStat = RawDataStat(self._region, self._track2, TrackFormatReq(dense=True, val='number', interval=False))
        self._addChild(rawPointsDataStat)
        self._addChild(rawNumDataStat)
