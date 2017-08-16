from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.NearestPointDistsStat import NearestPointDistsStatUnsplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class NearestPointMarkDiffStat(MagicStatFactory):
    pass

#class NearestPointMarkDiffStatSplittable(StatisticSumResSplittable):
#    pass
            
class NearestPointMarkDiffStatUnsplittable(NearestPointDistsStatUnsplittable):    
    def _compute(self):
        return sum(NearestPointDistsStatUnsplittable._compute(self))
        
    @staticmethod
    def _getObservator(p1, p2):
        return (p2.val() - p1.val())**2 if p2 != None else 0
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False, val='number')) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, interval=False, val='number')) )
