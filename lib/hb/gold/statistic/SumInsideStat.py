from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.AggregateOfCoveredBpsInSegmentsStat import AggregateOfCoveredBpsInSegmentsStatSplittable, AggregateOfCoveredBpsInSegmentsStatUnsplittable

class SumInsideStat(MagicStatFactory):
    pass

class SumInsideStatSplittable(AggregateOfCoveredBpsInSegmentsStatSplittable):
    pass

class SumInsideStatUnsplittable(AggregateOfCoveredBpsInSegmentsStatUnsplittable):
    def _init(self, **kwArgs):
        AggregateOfCoveredBpsInSegmentsStatUnsplittable._init(self, method='sum_of_sum', **kwArgs)

    #def _compute(self):
    #    numData = self._children[1].getResult().valsAsNumpyArray()
    #    sumInside = numData.dtype.type(0)
    #    for el in self._children[0].getResult():
    #        sumInside += numData[el.start():el.end()].sum(dtype='float64')
    #    return sumInside
    #
    #def _createChildren(self):
    #    rawSegDataStat = RawDataStat(self._region, self._track, TrackFormatReq(interval=True, dense=False))
    #    rawNumDataStat = RawDataStat(self._region, self._track2, TrackFormatReq(dense=True, val='number', interval=False))
    #    self._addChild(rawSegDataStat)
    #    self._addChild(rawNumDataStat)

    #Same as in AggregateOfCoveredBpsInSegmentsStatUnsplittable, just with the order of tracks reversed..
    def _createChildren(self):
        self._track, self._track2 = self._track2, self._track
        AggregateOfCoveredBpsInSegmentsStatUnsplittable._createChildren(self)
        #self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(allowOverlaps=False, val='number')) )
        #self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=False, dense=False)) )
