from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.SegmentDistancesStat import SegmentDistancesStat

class AvgSegDistStat(MagicStatFactory):
    pass
            
class AvgSegDistStatUnsplittable(Statistic):
    def _compute(self):
        return self._children[0].getResult()['Result'].mean()
        
    def _createChildren(self):
        self._addChild( SegmentDistancesStat(self._region, self._track) )
