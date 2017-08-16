from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.RandomUtil import random

class MarksSortedByFunctionValueStat(MagicStatFactory):
    pass

class MarksSortedByFunctionValueStatUnsplittable(Statistic):
    def __init__(self, region, track, track2, markReq=None, **kwArgs):        
        self._markReq = markReq
        Statistic.__init__(self, region, track, track2, markReq=markReq, **kwArgs)

    def _compute(self):
        tvMarkSegs = self._children[0].getResult()
        tvFuncValues = self._children[1].getResult()
        
        funcValueAndMarkList = []
        #coverBorderList = []
        #for coverSeg in tvCoverSegs:
        #    coverBorderList.append( [coverSeg.start(), 0])
        #    coverBorderList.append( [coverSeg.end()-1, 1])
                
        for markSeg in tvMarkSegs:
            funcValueAndMarkList.append( [ tvFuncValues[markSeg.start() : markSeg.end()].valsAsNumpyArray().mean(dtype='float64'), random.random(), markSeg.val()]  )
        
        return [x[2] for x in reversed(sorted(funcValueAndMarkList))], [x[0] for x in reversed(sorted(funcValueAndMarkList))]
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(interval=True, val=self._markReq)) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=True, val='number')) )


