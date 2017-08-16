from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, OnlyGloballySplittable, StatisticSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class NumBinsContainingElementsStat(MagicStatFactory):
    pass

class NumBinsContainingElementsStatSplittable(StatisticSumResSplittable, OnlyGloballySplittable):
    pass

class NumBinsContainingElementsStatUnsplittable(Statistic):    
    def _compute(self):
        tv = self._children[0].getResult()
        return 1 if len(tv.startsAsNumpyArray())>0 else 0
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False)) )
