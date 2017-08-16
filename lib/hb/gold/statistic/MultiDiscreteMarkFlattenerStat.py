from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.track.Track import PlainTrack
from gold.statistic.DiscreteMarkReducerStat import DiscreteMarkReducerStat
from numpy import zeros

class MultiDiscreteMarkFlattenerStat(MagicStatFactory):
    pass

#class MultiDiscreteMarkFlattenerStatSplittable(StatisticSumResSplittable):
#    IS_MEMOIZABLE = False
            
class MultiDiscreteMarkFlattenerStatUnsplittable(Statistic):    
    IS_MEMOIZABLE = False

    def __init__(self, region, track, track2=None, numDiscreteVals=None, reducedNumDiscreteVals=None, \
                 marksStat='MarksListStat', controlTrackNameList=None, **kwArgs):

        self._numDiscreteVals = int(numDiscreteVals)
        self._reducedNumDiscreteVals = int(reducedNumDiscreteVals)
        self._marksStat = marksStat

        assert controlTrackNameList is not None
        self._controlTrackNameList = [x.split('^') for x in controlTrackNameList.split('^^')] \
            if isinstance(controlTrackNameList, basestring) else controlTrackNameList
        assert len(controlTrackNameList) > 0

        Statistic.__init__(self, region, track, track2, numDiscreteVals=numDiscreteVals, \
                           reducedNumDiscreteVals=reducedNumDiscreteVals, marksStat=marksStat, **kwArgs)

    def _compute(self):
        flattenedMarks = zeros( len(self._children[0].getResult()), dtype='int32' )
        for i,reducedMarks in enumerate( [x.getResult() for x in self._children] ):
            flattenedMarks += reducedMarks * (self._reducedNumDiscreteVals ** i)
        return flattenedMarks    
    
    def _createChildren(self):
        for tn in self._controlTrackNameList:
            controlTrack = PlainTrack(tn)
            self._addChild( DiscreteMarkReducerStat(self._region, controlTrack, self._track, numDiscreteVals=self._numDiscreteVals, \
                                                    reducedNumDiscreteVals=self._reducedNumDiscreteVals, marksStat=self._marksStat) )
