from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSplittable
from gold.track.TrackFormat import TrackFormatReq

class FormatSpecStat(MagicStatFactory):
    def __new__(cls, region, track, trackFormatReq, **kwArgs):
        assert isinstance(trackFormatReq, TrackFormatReq)
        track.addFormatReq(trackFormatReq)
        return MagicStatFactory.__new__(cls, region, track, trackFormatReq=trackFormatReq, **kwArgs)

class FormatSpecStatSplittable(StatisticSplittable):
    def _combineResults(self):
        self._result = None
            
class FormatSpecStatUnsplittable(Statistic):    
    IS_MEMOIZABLE = False

    def _compute(self):
        return None
    
    def _createChildren(self):
        self._children = []
