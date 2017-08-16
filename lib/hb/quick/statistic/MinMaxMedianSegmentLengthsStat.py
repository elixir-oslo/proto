from collections import OrderedDict

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from numpy import median
from gold.statistic.SegmentLengthsStat import SegmentLengthsStat


class MinMaxMedianSegmentLengthsStat(MagicStatFactory):
    pass

class MinMaxMedianSegmentLengthsStatUnsplittable(Statistic):
    def _init(self, withOverlaps='no', **kwArgs):
        assert( withOverlaps in ['no','yes'] )
        self._withOverlaps = withOverlaps

    def _compute(self):
        lengths = self._children[0].getResult()['Result']
        if len(lengths) == 0:
            return OrderedDict([('MinLen', 0),('MaxLen', 0), ('MedianLen', 0.0)])
        return OrderedDict([('MinLen', min(lengths)),('MaxLen', max(lengths)), ('MedianLen', median(lengths))])
                    
    def _createChildren(self):
        self._addChild( SegmentLengthsStat(self._region, self._track, withOverlaps=self._withOverlaps) )
