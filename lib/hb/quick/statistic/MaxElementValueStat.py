from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable, StatisticSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class MaxElementValueStat(MagicStatFactory):
    "The maximum value of elements inside each bin"
    pass

class MaxElementValueStatSplittable(StatisticSplittable):
    def _combineResults(self):
        self._result = max(self._childResults)


class MaxElementValueStatUnsplittable(Statistic):
    def _compute(self):
        rawData = self._children[0].getResult()
        vals = rawData.valsAsNumpyArray()

        assert vals is not None

        if len(vals) > 0:
            return vals.max()

    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='number', allowOverlaps=self._configuredToAllowOverlaps(strict=False))) )
