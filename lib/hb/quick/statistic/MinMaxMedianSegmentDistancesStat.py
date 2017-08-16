from collections import OrderedDict
from numpy import median

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.SegmentDistancesStat import SegmentDistancesStat


class MinMaxMedianSegmentDistancesStat(MagicStatFactory):
    pass

class MinMaxMedianSegmentDistancesStatUnsplittable(Statistic):

    def _init(self, withOverlaps='no', **kwArgs):
        assert( withOverlaps in ['no','yes'] )
        self._withOverlaps = withOverlaps
    
    def _compute(self):
        dists = self._children[0].getResult()['Result']
        if len(dists) == 0:
                return OrderedDict([('MinDist', 0),('MaxDist', 0), ('MedianDist', 0.0)])

        return OrderedDict([('MinDist', min(dists)),('MaxDist', max(dists)), ('MedianDist', median(dists))])

            
    def _createChildren(self):
        self._addChild( SegmentDistancesStat(self._region, self._track) )
