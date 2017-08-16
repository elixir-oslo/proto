#import gold
from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.SegmentDistancesStat import SegmentDistancesStatUnsplittable, SegmentDistancesStatSplittable

class PointGapsStat(MagicStatFactory):
    pass

class PointGapsStatSplittable(SegmentDistancesStatSplittable):
    pass

class PointGapsStatUnsplittable(SegmentDistancesStatUnsplittable):
    INTERVALS = False
