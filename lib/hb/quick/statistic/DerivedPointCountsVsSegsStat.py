from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.PointCountsVsSegsStat import PointCountsVsSegsStat
from gold.statistic.DerivedOverlapStat import DerivedOverlapStatUnsplittable

class DerivedPointCountsVsSegsStat(MagicStatFactory):
    pass

class DerivedPointCountsVsSegsStatUnsplittable(DerivedOverlapStatUnsplittable):
    def _createChildren(self):
        self._addChild( PointCountsVsSegsStat(self._region, self._track, self._track2) )
