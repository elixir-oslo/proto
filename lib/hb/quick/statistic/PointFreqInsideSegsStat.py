from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import RatioStatUnsplittable
from quick.statistic.PointCountInsideSegsStat import PointCountInsideSegsStat
from gold.statistic.CountStat import CountStat
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq

class PointFreqInsideSegsStat(MagicStatFactory):
    pass

class PointFreqInsideSegsStatUnsplittable(RatioStatUnsplittable):    
    def _createChildren(self):
        self._addChild( PointCountInsideSegsStat(self._region, self._track, self._track2) )
        self._addChild( CountStat(self._region, self._track2) )
        self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True) ) )
