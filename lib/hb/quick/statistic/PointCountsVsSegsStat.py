from gold.statistic.RawOverlapStat import RawOverlapStat, RawOverlapStatUnsplittable
from gold.statistic.Statistic import StatisticDictSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.BinSizeStat import BinSizeStat
from collections import OrderedDict

class PointCountsVsSegsStat(RawOverlapStat):
    pass

class PointCountsVsSegsStatSplittable(StatisticDictSumResSplittable):
    pass

class PointCountsVsSegsStatUnsplittable(RawOverlapStatUnsplittable):
    def _compute(self):
        res = RawOverlapStatUnsplittable._compute(self)
        return OrderedDict([('Both', res['Both']), ('Only1', res['Only1'])])

    def _createChildren(self):
        rawDataStat = RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False))
        self._addChild(rawDataStat)
        rawDataStat2 = RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True))
        self._addChild(rawDataStat2)
        self._binSizeStat = self._addChild( BinSizeStat(self._region, self._track2))
