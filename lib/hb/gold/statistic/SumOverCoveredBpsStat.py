from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class SumOverCoveredBpsStat(MagicStatFactory):
    pass

class SumOverCoveredBpsStatSplittable(StatisticSumResSplittable):    
    pass

class SumOverCoveredBpsStatUnsplittable(Statistic):    
    def _compute(self):
        rawData = self._children[0].getResult()
        
        vals = rawData.valsAsNumpyArray()
        assert vals.dtype in ["float32","float64","float128"]
        
        if rawData.trackFormat.reprIsDense():
            res = float(vals.sum(dtype="float64")) #accumulator must be 64-bit or rounding errors occur
        else:
            starts, ends = rawData.startsAsNumpyArray(), rawData.endsAsNumpyArray()
            res = float( ((ends - starts) * vals).sum(dtype="float64") )
        return res
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='number', allowOverlaps=False)) )
