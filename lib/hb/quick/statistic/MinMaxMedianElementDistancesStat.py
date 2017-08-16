from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.ElementDistancesStat import ElementDistancesStat
from quick.statistic.MinMaxMedianSegmentDistancesStat import MinMaxMedianSegmentDistancesStatUnsplittable


class MinMaxMedianElementDistancesStat(MagicStatFactory):
    pass

class MinMaxMedianElementDistancesStatUnsplittable(MinMaxMedianSegmentDistancesStatUnsplittable):
            
    def _createChildren(self):
        self._addChild( ElementDistancesStat(self._region, self._track) )
