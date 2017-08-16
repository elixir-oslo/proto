from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class BinSizeStat(MagicStatFactory):
    pass

class BinSizeStatSplittable(StatisticSumResSplittable):
    IS_MEMOIZABLE = False
    
    pass
            
class BinSizeStatUnsplittable(Statistic):    
    IS_MEMOIZABLE = False
    
    def _compute(self):
        #if isIter(self._region):
            #return sum( len(reg) for reg in self._region)
        #else:
        return len(self._region)
        
    def _createChildren(self):
        #pass
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=None)) )
