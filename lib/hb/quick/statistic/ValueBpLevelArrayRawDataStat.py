from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class ValueBpLevelArrayRawDataStat(MagicStatFactory):
    pass

#class ValueBpLevelArrayRawDataStatSplittable(StatisticSumResSplittable):
#    pass

class ValueBpLevelArrayRawDataStatUnsplittable(Statistic):
    def _init(self, voidValue=0):
        self._voidValue = voidValue

    def _compute(self):
        tv = self._children[0].getResult()
        return tv.getValueBpLevelArray(self._voidValue)

    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=False, val='number')) )

    def _afterComputeCleanup(self):
        if self.hasResult():
            del self._result
