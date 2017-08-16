from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.MultiDiscreteMarkFlattenerStat import MultiDiscreteMarkFlattenerStat
from gold.statistic.SimpleBpIntensityStat import SimpleBpIntensityStatUnsplittable
from gold.statistic.DiscreteMarksIntensityStat import DiscreteMarksIntensityStat

class BpIntensityStat(MagicStatFactory):
    pass

#class BpIntensityStatSplittable(StatisticSumResSplittable):
#    IS_MEMOIZABLE = False
            
class BpIntensityStatUnsplittable(SimpleBpIntensityStatUnsplittable):    
    IS_MEMOIZABLE = False
    VERBOSE_INTENSITY_CREATION = True

    def __init__(self, region, track, track2=None, numDiscreteVals=None, reducedNumDiscreteVals=None, \
                 controlTrackNameList=None, **kwArgs):
            assert controlTrackNameList is not None
            self._numDiscreteVals = numDiscreteVals
            self._reducedNumDiscreteVals = reducedNumDiscreteVals
            self._controlTrackNameList = controlTrackNameList
            Statistic.__init__(self, region, track, track2, numDiscreteVals=numDiscreteVals, \
                               reducedNumDiscreteVals=reducedNumDiscreteVals, controlTrackNameList=controlTrackNameList, **kwArgs)

    def _createChildren(self):
        self._addChild( MultiDiscreteMarkFlattenerStat(self._region, self._track, numDiscreteVals=self._numDiscreteVals, \
                                                       reducedNumDiscreteVals=self._reducedNumDiscreteVals, controlTrackNameList=self._controlTrackNameList) )
        self._addChild( DiscreteMarksIntensityStat(self._region, self._track, numDiscreteVals=self._numDiscreteVals, \
                                                   reducedNumDiscreteVals=self._reducedNumDiscreteVals, controlTrackNameList=self._controlTrackNameList) )
