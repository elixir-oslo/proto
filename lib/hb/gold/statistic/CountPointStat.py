from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
#from gold.statistic.CountStat import CountStatSplittable, CountStatUnsplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.statistic.Statistic import StatisticSumResSplittable

class CountPointStat(MagicStatFactory):
    pass

class CountPointStatSplittable(StatisticSumResSplittable):
    pass
            
class CountPointStatUnsplittable(Statistic):
    def _compute(self):
        rawData = self._children[0].getResult()
        return len( rawData.startsAsNumpyArray() )
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False)) )
