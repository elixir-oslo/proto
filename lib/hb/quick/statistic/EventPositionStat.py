from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import numpy as np

class EventPositionStat(MagicStatFactory):
    pass

#class EventPositionStatSplittable(StatisticSumResSplittable):
#    pass
            
class EventPositionStatUnsplittable(Statistic):
    
    def _compute(self):
        tv1 = self._children[0].getResult()
        tv2 = self._children[1].getResult()
        tv1Events = np.concatenate((tv1.startsAsNumpyArray(), tv1.endsAsNumpyArray()))
        tv2Events = np.concatenate((tv2.startsAsNumpyArray(), tv2.endsAsNumpyArray()))
        return np.unique(np.concatenate((tv1Events, tv2Events)))
        
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq()) )
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq()) )
