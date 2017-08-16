from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
#from gold.statistic.CountStat import CountStatSplittable, CountStatUnsplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.statistic.Statistic import StatisticSumResSplittable

#Similar to CountPointStat, except it doesn't require interval=False
class OverlapAgnosticCountElementStat(MagicStatFactory):
    pass

class OverlapAgnosticCountElementStatSplittable(StatisticSumResSplittable):
    pass
            
class OverlapAgnosticCountElementStatUnsplittable(Statistic):
    ALLOW_OVERLAPS = None
    
    def _compute(self):
        rawData = self._children[0].getResult()
        if rawData.trackFormat.reprIsDense():
            return len(rawData.valsAsNumpyArray())
        else:
            return len( rawData.startsAsNumpyArray() )
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=self.ALLOW_OVERLAPS) ) )
