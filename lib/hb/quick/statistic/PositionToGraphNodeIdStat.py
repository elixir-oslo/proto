'''
Returns a mapping from Points to Graph ids. The graph ids are the segments in which the points can be found.
'''
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticConcatResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from bisect import bisect

class PositionToGraphNodeIdStat(MagicStatFactory):
    pass

class PositionToGraphNodeIdStatSplittable(StatisticConcatResSplittable):

    def _combineResults(self):
        #self._result = reduce(lambda l1,l2:l1+l2, [childResult for childResult in self._childResults])
        self._result = reduce(lambda l1, l2:l1+l2, self._childResults)
            
class PositionToGraphNodeIdStatUnsplittable(Statistic):
    def _compute(self):
        ids = set()
        points = self._segmentsStat.getResult()
        graphNodeId = self._graphNodeIdStat.getResult()
        pointsStarts = points.startsAsNumpyArray()
        graphTrackIds = graphNodeId.idsAsNumpyArray()
        graphTrackStarts = graphNodeId.startsAsNumpyArray()
        if len(graphTrackStarts) > 0:
            for point in pointsStarts:
                #bisect finds the position where all elements on the left are smaller, and all elements on the right are bigger.
                #TODO: what if bisect returns 0?
                index = bisect(graphTrackStarts, point)-1
                pointBelongsInNodeWithId = graphTrackIds[index]
                #TODO: do a check here that point is between start and end of this node?
                ids.add(pointBelongsInNodeWithId)
        return list(ids)

    def _createChildren(self):
        self._graphNodeIdStat = self._addChild(RawDataStat(self._region, self._track, TrackFormatReq(interval=True, id=True, dense=True)))
        #self._segmentsStat = self._addChild(RawDataStat(self._region, self._track2, TrackFormatReq(interval=False, dense=False)))
        self._segmentsStat = self._addChild(RawDataStat(self._region, self._track2, TrackFormatReq(interval=False, dense=False, allowOverlaps=None)))

        
