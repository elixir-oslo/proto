from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.ProportionCountStat import ProportionCountStat
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.PropPointCountsVsSegsStat import PropPointCountsVsSegsStatUnsplittable
from quick.statistic.RawOverlapAllowSingleTrackOverlapsStat import RawOverlapAllowSingleTrackOverlapsStat

class PropPointCountsAllowOverlapsVsSegsStat(MagicStatFactory):
    pass

class PropPointCountsAllowOverlapsVsSegsStatUnsplittable(PropPointCountsVsSegsStatUnsplittable):
    def _createChildren(self):
        self._rawOverlap = self._addChild( RawOverlapAllowSingleTrackOverlapsStat(self._region, self._track, self._track2) )
        self._segmentCoverProportion = self._addChild( ProportionCountStat(self._region, self._track2) )
        self._addChild( FormatSpecStat(self._region, self._track, TrackFormatReq(dense=False, interval=False, allowOverlaps=True)) )
        self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True, allowOverlaps=False)) )
