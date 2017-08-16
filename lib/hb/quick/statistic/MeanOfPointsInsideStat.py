from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.MeanInsideStat import MeanInsideStatUnsplittable
from gold.statistic.SumInsideStat import SumInsideStat
from gold.statistic.CountStat import CountStat
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq

class MeanOfPointsInsideStat(MagicStatFactory):
    pass

class MeanOfPointsInsideStatUnsplittable(MeanInsideStatUnsplittable):    
    def _createChildren(self):
        self._addChild( SumInsideStat(self._region, self._track, self._track2) )
        self._addChild( CountStat(self._region, self._track) )
        self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(interval=False, dense=False)))
