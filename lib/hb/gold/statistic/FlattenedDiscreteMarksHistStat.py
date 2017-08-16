from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.AbstractHistStat import AbstractHistStatUnsplittable
from gold.statistic.MultiDiscreteMarkFlattenerStat import MultiDiscreteMarkFlattenerStat

class FlattenedDiscreteMarksHistStat(MagicStatFactory):
    pass

#class FlattenedDiscreteMarksHistStatSplittable(StatisticSumResSplittable):
#    IS_MEMOIZABLE = False

class FlattenedDiscreteMarksHistStatUnsplittable(AbstractHistStatUnsplittable):
    def __init__(self, region, track, track2=None, numDiscreteVals=None, reducedNumDiscreteVals=None, \
                 marksStat='MarksListStat', controlTrackNameList=None, **kwArgs):

        self._numDiscreteVals = numDiscreteVals
        self._reducedNumDiscreteVals = reducedNumDiscreteVals
        self._marksStat = marksStat

        assert controlTrackNameList is not None
        self._controlTrackNameList = controlTrackNameList
        
        numControlTracks = len([x.split('^') for x in controlTrackNameList.split('^^')] \
            if isinstance(controlTrackNameList, basestring) else controlTrackNameList)
        assert numControlTracks > 0

        self._numHistBins = int(reducedNumDiscreteVals)**numControlTracks

        Statistic.__init__(self, region, track, track2, numDiscreteVals=numDiscreteVals, \
                           reducedNumDiscreteVals=reducedNumDiscreteVals, marksStat=marksStat, \
                           controlTrackNameList=controlTrackNameList, **kwArgs)

    def _createChildren(self):
        self._addChild( MultiDiscreteMarkFlattenerStat(self._region, self._track,\
                                                       numDiscreteVals=self._numDiscreteVals, reducedNumDiscreteVals=self._reducedNumDiscreteVals,\
                                                       marksStat=self._marksStat, controlTrackNameList=self._controlTrackNameList) )
