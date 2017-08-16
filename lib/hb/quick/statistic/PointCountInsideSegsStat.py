from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.PointCountsVsSegsStat import PointCountsVsSegsStat

class PointCountInsideSegsStat(MagicStatFactory):
    pass

#class PointCountInsideSegsStatSplittable(StatisticSumResSplittable):
#    pass
            
#The current implementation simply passes on values from PointCountsVsSegsStat. If the class here is used much, it could compute its result more quickly by only computing the necessary result..
class PointCountInsideSegsStatUnsplittable(Statistic):
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)
    #def computeStep(self):
    #    return Statistic.computeStep(self)
    
    def _compute(self):
        #from gold.application.LogSetup import logMessage
        #logMessage('HERE: '+str(self._children[0].getResult()))
        res = self._children[0].getResult()
        #print 'RESSSS: ', res
        return res['Both']
        #codedPoints = tv1.startsAsNumpyArray()  * 4 +2
        #codedStarts = tv2.startsAsNumpyArray()  * 4 +3
        #codedEnds= tv2.endsAsNumpyArray()  * 4 +1
        #
        #allSortedCodedEvents = numpy.concatenate( (codedPoints, codedStarts, codedEnds) )
        #allSortedCodedEvents.sort()
        #
        #allEventCodes = (allSortedCodedEvents % 4) -2
        #allSortedDecodedEvents = allSortedCodedEvents / 4
        #
        #allIndexesOfPoints = (allEventCodes == 0)
        #
        #cumulativeCoverStatus = numpy.add.accumulate(allEventCodes)
        #return cumulativeCoverStatus[allIndexesOfPoints].sum() 

    def _createChildren(self):
        self._addChild( PointCountsVsSegsStat(self._region, self._track, self._track2))
        #self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False)) )
        #self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True)) )
