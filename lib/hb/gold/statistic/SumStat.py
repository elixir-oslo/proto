from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.SumOverCoveredBpsStat import SumOverCoveredBpsStatSplittable, SumOverCoveredBpsStatUnsplittable
from gold.track.TrackFormat import TrackFormatReq

class SumStat(MagicStatFactory):
    pass

class SumStatSplittable(SumOverCoveredBpsStatSplittable):    
    pass

class SumStatUnsplittable(SumOverCoveredBpsStatUnsplittable):
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='number', dense=True, interval=False)) )
