from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.statistic.BpCoverageByCatStat import BpCoverageByCatStatSplittable, BpCoverageByCatStatUnsplittable

class FreqByCatStat(MagicStatFactory):
    pass

class FreqByCatStatSplittable(BpCoverageByCatStatSplittable):
    pass

class FreqByCatStatUnsplittable(BpCoverageByCatStatUnsplittable):
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False, val='category', allowOverlaps=True)) )
