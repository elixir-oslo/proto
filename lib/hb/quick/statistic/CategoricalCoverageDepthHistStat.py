from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class CategoricalCoverageDepthHistStat(MagicStatFactory):
    pass

#class CategoricalCoverageDepthHistStatSplittable(StatisticSumResSplittable):
#    pass

class CategoricalCoverageDepthHistStatUnsplittable(Statistic):
    def _compute(self):
        tv = self._children[0].getResult()
        coverage = tv.getCoverageBpLevelArray()

        import numpy as np
        return np.bincount(coverage)

    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(interval=True, val='category', allowOverlaps=True)) )
