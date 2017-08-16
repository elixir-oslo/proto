from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.RandomUtil import random

class MarksSortedBySegmentOverlapStat(MagicStatFactory):
    pass

class MarksSortedBySegmentOverlapStatUnsplittable(Statistic):
    def __init__(self, region, track, track2, markReq=None, **kwArgs):        
        self._markReq = markReq
        Statistic.__init__(self, region, track, track2, markReq=markReq, **kwArgs)

    def _compute(self):
        tvMarkSegs = self._children[0].getResult()
        tvCoverSegs = self._children[1].getResult()
        
        relCoverAndMarkList = []
        coverBorderList = [[0,0]]
        for coverSeg in tvCoverSegs:
            coverBorderList.append( [coverSeg.start(), 0])
            coverBorderList.append( [coverSeg.end(), 1])
                
        coverIndex = 1 #since we are operating on ranges from previous, and have added a dummy element at positions 0..
        for markSeg in tvMarkSegs:
            cover = 0
            curPos = markSeg.start()
            while coverIndex < len(coverBorderList) and coverBorderList[coverIndex-1][0] < markSeg.end(): #coverIndex-1 to go one passed, since we are adding ranges from previous to current pos..
                cover += max(0, min(coverBorderList[coverIndex][0], markSeg.end()) - curPos) * coverBorderList[coverIndex][1]
                curPos = coverBorderList[coverIndex][0]
                coverIndex += 1
            coverIndex -= 1 #since we went two passed..
            relCoverAndMarkList.append( [1.0*cover/len(markSeg), random.random(), markSeg.val()] )
            
        return [x[2] for x in reversed(sorted(relCoverAndMarkList))], [x[0] for x in reversed(sorted(relCoverAndMarkList))]
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(interval=True, val=self._markReq)) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True)) )


