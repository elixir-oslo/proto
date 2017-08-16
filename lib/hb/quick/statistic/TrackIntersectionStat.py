from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawOverlapStat import RawOverlapStatUnsplittable
from gold.track.TrackView import TrackView
import numpy

class TrackIntersectionStat(MagicStatFactory):
    pass

#class TrackIntersectionStatSplittable(StatisticSumResSplittable):
#    pass

class TrackIntersectionStatUnsplittable(RawOverlapStatUnsplittable):
    #def _init(self, operation="intersect"):
    #    assert operation in ['intersect', 'union', 'subtract1from2', 'subtract2from1', 'notcovered']

    def _compute(self):
        tv1, tv2 = self._children[0].getResult(), self._children[1].getResult()

        t1s = tv1.startsAsNumpyArray()
        t1e = tv1.endsAsNumpyArray()
        t2s = tv2.startsAsNumpyArray()
        t2e = tv2.endsAsNumpyArray()

        allSortedDecodedEvents, allEventLengths, cumulativeCoverStatus = \
            self._findAllStartAndEndEvents(t1s, t1e, t2s, t2e)

        allResultStarts = allSortedDecodedEvents[cumulativeCoverStatus == 3]
        allResultLengths = allEventLengths[cumulativeCoverStatus[:-1] == 3]
        allResultEnds = allResultStarts + allResultLengths

        return TrackView(genomeAnchor=tv1.genomeAnchor, startList=allResultStarts,
                         endList=allResultEnds, valList=None, strandList=None,
                         idList=None, edgesList=None, weightsList=None,
                         borderHandling=tv1.borderHandling, allowOverlaps=False)
