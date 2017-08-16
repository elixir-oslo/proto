from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CommonFunctions import pairwise
import numpy

class PointCountPerSegStat(MagicStatFactory):
    pass

class PointCountPerSegStatSplittable(StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable):
    IS_MEMOIZABLE = False
    
    def _combineResults(self):
        for x,y in pairwise(self._region):
            if y.genome == x.genome and y.start == x.end:
                # Simple check for consequtive bins.
                # In this case, the result may not be correct since segments may cross
                # borders between bins, and be counted twice. This check does not
                # check every possibility for error, only the most basic.
                return None
        res = StatisticConcatNumpyArrayResSplittable._combineResults(self)
        
        
class PointCountPerSegStatUnsplittable(Statistic):    
    IS_MEMOIZABLE = False

    def _compute(self):
        tv1, tv2 = self._children[0].getResult(), self._children[1].getResult()

        codedPoints = tv1.startsAsNumpyArray()  * 8 +6 #+2 +4, with +4 to get correct sorting..
        codedStarts = tv2.startsAsNumpyArray()  * 8 +3
        codedEnds= tv2.endsAsNumpyArray()  * 8 +1
        
        if len(codedStarts)==0:
            return numpy.array([])

        allSortedCodedEvents = numpy.concatenate( (codedPoints, codedStarts, codedEnds) )
        allSortedCodedEvents.sort()

        allEventCodes = (allSortedCodedEvents % 4) -2 #Note %4, as this will remove the +4 for points
        allSortedDecodedEvents = allSortedCodedEvents / 8
        
        allIndexesOfSegEnds = numpy.nonzero(allEventCodes == -1)[0]
        
        cumulativeCoverStatus = numpy.add.accumulate(allEventCodes)
        
        pointInsidePerIndex = ( (cumulativeCoverStatus==1) & (allEventCodes==0) ).astype('int64')

        return numpy.add.reduceat(pointInsidePerIndex, numpy.concatenate(([0],allIndexesOfSegEnds)))[0:-1]
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False)) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True)) )
        #fixme: Track 2 should have borderhandling='include', but this is not supported yet. This to support correct splitting'
