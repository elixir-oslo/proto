from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.track.TrackView import TrackView
import numpy

class ForEachSegmentDistToNearestInSameTrackStat(MagicStatFactory):
    pass

#class ForEachSegmentDistToNearestInSameTrackSplittable(Statistic):
#    IS_MEMOIZABLE = False

class ForEachSegmentDistToNearestInSameTrackStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    def _init(self, withOverlaps='no',threshold='1000', **kwArgs):
        self.threshold = int(threshold)
    
    def _compute(self):
        tv = self._children[0].getResult()
        
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        
        vals = []
        dists = starts[1:]-ends[:-1]
        if len(dists)==0:
            return TrackView(genomeAnchor=tv.genomeAnchor, startList=starts, endList=ends, valList=numpy.array(vals, dtype='int32'), \
                strandList=None, idList=None, edgesList=None, weightsList=None, borderHandling=tv.borderHandling, allowOverlaps=tv.allowOverlaps)
        dists[dists<0] = 0
        selector = [False]*len(ends)
        
        if dists[0]<=self.threshold:
            selector[0] = True
            vals.append(dists[0])
            
        for index in xrange(1,len(starts)-1):
            nearestDist = min(dists[index-1], dists[index])
            if nearestDist <= self.threshold:
                vals.append(nearestDist)
                selector[index]=True
        selector = numpy.array(selector)
        return TrackView(genomeAnchor=tv.genomeAnchor, startList=starts[selector], endList=ends[selector], valList=numpy.array(vals, dtype='int32'), \
                strandList=None, idList=None, edgesList=None, weightsList=None, borderHandling=tv.borderHandling, allowOverlaps=tv.allowOverlaps)
        
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=True, allowOverlaps = False ) ))
