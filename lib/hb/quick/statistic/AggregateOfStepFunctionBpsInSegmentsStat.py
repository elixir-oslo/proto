from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from quick.statistic.AggregateOfCoveredBpsInSegmentsStat import AggregateOfCoveredBpsInSegmentsStatSplittable, AggregateOfCoveredBpsInSegmentsStatUnsplittable
from gold.track.TrackFormat import TrackFormatReq

class AggregateOfStepFunctionBpsInSegmentsStat(MagicStatFactory):
    pass

class AggregateOfStepFunctionBpsInSegmentsStatSplittable(AggregateOfCoveredBpsInSegmentsStatSplittable):
    pass

class AggregateOfStepFunctionBpsInSegmentsStatUnsplittable(AggregateOfCoveredBpsInSegmentsStatUnsplittable):
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=False, val='number', interval=True, dense=True)) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(allowOverlaps=False, dense=False, interval=True)) )
