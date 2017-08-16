from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.CountStat import CountStatSplittable, CountStatUnsplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class CountSegmentStat(MagicStatFactory):
    'Counts bp coverage of a single segment track'
    pass

class CountSegmentStatSplittable(CountStatSplittable):
    pass
            
class CountSegmentStatUnsplittable(CountStatUnsplittable):
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=True, allowOverlaps=self._configuredToAllowOverlaps(strict=False))) )
