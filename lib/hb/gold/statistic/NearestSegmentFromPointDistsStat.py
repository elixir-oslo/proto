from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import StatisticConcatDictOfListResSplittable, OnlyGloballySplittable
from gold.statistic.NearestSegmentDistsStat import NearestSegmentDistsStatUnsplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class NearestSegmentFromPointDistsStat(MagicStatFactory):
    pass

class NearestSegmentFromPointDistsStatSplittable(StatisticConcatDictOfListResSplittable, OnlyGloballySplittable):
    pass

class NearestSegmentFromPointDistsStatUnsplittable(NearestSegmentDistsStatUnsplittable):
    'For each point in track1, finds the distance to the closest segment of track2, overlap counting as zero distance..'
    
    def _init(self, **kwArgs):
        kwArgs['addSegmentLengths'] = 'False'
        NearestSegmentDistsStatUnsplittable._init(self, **kwArgs)
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False)) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True)) )
