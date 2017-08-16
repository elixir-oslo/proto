from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.CountPointStat import CountPointStatSplittable, CountPointStatUnsplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class CountPointAllowingOverlapStat(MagicStatFactory):
    pass

class CountPointAllowingOverlapStatSplittable(CountPointStatSplittable):
    pass
            
class CountPointAllowingOverlapStatUnsplittable(CountPointStatUnsplittable):
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False, \
                                                                              allowOverlaps=True)))#, borderHandling='include')) )
