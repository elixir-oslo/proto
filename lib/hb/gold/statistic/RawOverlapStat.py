from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticDictSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.BinSizeStat import BinSizeStat
from collections import OrderedDict
import numpy

class RawOverlapStat(MagicStatFactory):
    '''
    Counts the number of base pairs covered by each of the 4 possible combinations of binary coverage by T1 and T2.
    These 4 numbers are denoted as tp,fp,tn,fn, using terminology as if T1 represented a binary prediction of individual base pairs,
    and T2 represented answer binary class for the base pairs.
    '''
    pass

class RawOverlapStatSplittable(StatisticDictSumResSplittable):
    pass

##TEMPORARY FOR CONSTRUCT FUNCTION DEF:
#from gold.statistic.Statistic import StatisticSplittable
#class RawOverlapStatSplittable(StatisticSplittable):
#    def _combineResults(self):
#        if len(self._childResults)>1:
#            #self._result = self._childResults[0] + self._childResults[1]
#            self._result = reduce(lambda x,y:x+y, self._childResults)
#        else:
#            self._result = 'Empty'


class RawOverlapStatUnsplittable(Statistic):
    VERSION = '1.1'

    #def __init__(self, region, track, track2, **kwArgs):
    #    Statistic.__init__(self, region, track, track2, **kwArgs)

    def _compute(self): #Numpy Version..
        tv1, tv2 = self._children[0].getResult(), self._children[1].getResult()

        t1s = tv1.startsAsNumpyArray()
        t1e = tv1.endsAsNumpyArray()
        t2s = tv2.startsAsNumpyArray()
        t2e = tv2.endsAsNumpyArray()

        #add bps before first and after last segment
        binSize = self._binSizeStat.getResult()
        #binSize = len(self._region)

        tn,fp,fn,tp = self._computeRawOverlap(t1s,t1e,t2s,t2e,binSize)


        return OrderedDict(zip(['Neither','Only1','Only2','Both'] , (tn,fp,fn,tp)))
        ##To construct code and tests for external development
        #from test.sandbox.div.constructFunctionDefs import constructFunctionDefWithTest
        #return constructFunctionDefWithTest('_computeRawOverlap', 't1s,t1e,t2s,t2e,binSize'.split(','), [list(x) for x in t1s,t1e,t2s,t2e]+[binSize], tp)
        ##return constructFunctionDefWithTest('_computeRawOverlap', 't1s,t1e,t2s,t2e,binSize'.split(','), [list(x) for x in t1s,t1e,t2s,t2e]+[binSize], dict(zip('tn,fp,fn,tp'.split(','), [tn,fp,fn,tp])))


    @staticmethod
    def _findAllStartAndEndEvents(t1s, t1e, t2s, t2e):
        #assert no overlaps..
        #create arrays multiplied by 8 to use last three bits to code event type,
        #Last three bits: relative to 4 (100): +/- 1 for start/end of track1, +/- 2 for track2..
        t1CodedStarts = t1s * 8 +5
        t1CodedEnds= t1e  * 8 +3
        t2CodedStarts = t2s * 8 +6
        t2CodedEnds= t2e * 8 +2

        allSortedCodedEvents = numpy.concatenate( (t1CodedStarts,t1CodedEnds,t2CodedStarts,t2CodedEnds) )
        allSortedCodedEvents.sort()

        allEventCodes = (allSortedCodedEvents % 8) -4

        allSortedDecodedEvents = allSortedCodedEvents / 8
        allEventLengths = allSortedDecodedEvents[1:] - allSortedDecodedEvents[:-1]

        #due to the coding, the last bit now has status of track1, and the second last bit status of track2
        #thus, 3 is cover by both, 2 is cover by only track2, 1 is cover by only track1, 0 is no cover
        #this works as there are no overlaps, and bits will thus not "spill over"..
        cumulativeCoverStatus = numpy.add.accumulate(allEventCodes)

        return allSortedDecodedEvents, allEventLengths, cumulativeCoverStatus

    @classmethod
    def _computeRawOverlap(cls, t1s, t1e, t2s, t2e, binSize):
        allSortedDecodedEvents, allEventLengths, cumulativeCoverStatus = cls._findAllStartAndEndEvents(t1s, t1e, t2s, t2e)

        tn,fp,fn,tp = [long((allEventLengths[ cumulativeCoverStatus[:-1] == status ]).sum()) for status in range(4)]

        if len(allSortedDecodedEvents)>0:
            tn += allSortedDecodedEvents[0] + (binSize - allSortedDecodedEvents[-1])
        else:
            tn+=binSize

        return tn,fp,fn,tp

    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False)) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False)) )
        self._binSizeStat = self._addChild( BinSizeStat(self._region, self._track2))
