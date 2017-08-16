from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawOverlapStat import RawOverlapStatUnsplittable
from gold.track.TrackView import TrackView
from numpy import array

class TrackIntersectionWithValStat(MagicStatFactory):
    pass

#class TrackIntersectionWithValStatSplittable(StatisticSumResSplittable):
#    pass

class TrackIntersectionWithValStatUnsplittable(RawOverlapStatUnsplittable):
    #def _init(self, operation="intersect"):
    #    assert operation in ['intersect', 'union', 'subtract1from2', 'subtract2from1', 'notcovered']

    def _compute(self):
        tv1, tv2 = self._children[0].getResult(), self._children[1].getResult()

        t1s = tv1.startsAsNumpyArray()
        t1e = tv1.endsAsNumpyArray()
        t1vals = tv1.valsAsNumpyArray()
        t2s = tv2.startsAsNumpyArray()
        t2e = tv2.endsAsNumpyArray()

        allSortedDecodedEvents, allEventLengths, cumulativeCoverStatus = \
            self._findAllStartAndEndEvents(t1s, t1e, t2s, t2e)

        allResultStarts = allSortedDecodedEvents[cumulativeCoverStatus[:-1] == 3]
        allResultLengths = allEventLengths[cumulativeCoverStatus[:-1] == 3]
        allResultEnds = allResultStarts + allResultLengths
        
        valList = []
        cursor = 0
        for rs, re in zip(allResultStarts, allResultEnds):
            for i in xrange(cursor, len(t1s)):
                if rs >= t1s[i] and re <= t1e[i]:
                    valList.append(float(t1vals[i]))
                    cursor = i
                    break
        
        assert len(valList) == len(allResultStarts), valList
            
        return TrackView(genomeAnchor=tv1.genomeAnchor, startList=allResultStarts,
                         endList=allResultEnds, valList=array(valList), strandList=None,
                         idList=None, edgesList=None, weightsList=None,
                         borderHandling=tv1.borderHandling, allowOverlaps=False)
