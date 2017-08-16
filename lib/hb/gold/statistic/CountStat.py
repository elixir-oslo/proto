from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class CountStat(MagicStatFactory):
    "Counts bps covered by track. If specified with intra-track overlaps, it will for each bp count the number of times the bp is covered by a track element."
    pass

class CountStatSplittable(StatisticSumResSplittable):
    pass

class CountStatUnsplittable(Statistic):
    def _compute(self):
        rawData = self._children[0].getResult()
        if rawData.trackFormat.reprIsDense():
            return len(rawData.valsAsNumpyArray())
        else:
            #return sum(el.end()-el.start() for el in rawData)
            return int(rawData.endsAsNumpyArray().sum() - rawData.startsAsNumpyArray().sum())

    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=self._configuredToAllowOverlaps(strict=False))) )
