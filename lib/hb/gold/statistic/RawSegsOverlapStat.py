from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.BinSizeStat import BinSizeStat
from gold.statistic.RawOverlapStat import RawOverlapStatSplittable, RawOverlapStatUnsplittable

class RawSegsOverlapStat(MagicStatFactory):
    pass

class RawSegsOverlapStatSplittable(RawOverlapStatSplittable):
    pass

class RawSegsOverlapStatUnsplittable(RawOverlapStatUnsplittable):
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=True)) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True)) )
        self._binSizeStat = self._addChild( BinSizeStat(self._region, self._track2))
