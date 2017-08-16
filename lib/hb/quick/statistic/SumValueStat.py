from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class SumValueStat(MagicStatFactory):
    pass

class SumValueStatSplittable(Statistic):    
    pass

class SumValueStatUnsplittable(Statistic):
    
    def _compute(self):
        tv = self._children[0].getResult()
        return sum(tv.valsAsNumpyArray())
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='number')) )
