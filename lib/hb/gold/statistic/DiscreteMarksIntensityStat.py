from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.FlattenedDiscreteMarksHistStat import FlattenedDiscreteMarksHistStat
from gold.statistic.SimpleDiscreteMarksIntensityStat import SimpleDiscreteMarksIntensityStatUnsplittable

class DiscreteMarksIntensityStat(MagicStatFactory):
    pass

#class DiscreteMarksIntensityStatSplittable(StatisticSumResSplittable):
#    IS_MEMOIZABLE = False
            
class DiscreteMarksIntensityStatUnsplittable(SimpleDiscreteMarksIntensityStatUnsplittable):
    IS_MEMOIZABLE = False

    def __init__(self, region, track, track2=None, numDiscreteVals=None, reducedNumDiscreteVals=None, \
                 controlTrackNameList=None, **kwArgs):
            assert controlTrackNameList is not None
            self._numDiscreteVals = numDiscreteVals
            self._reducedNumDiscreteVals = reducedNumDiscreteVals
            self._controlTrackNameList = controlTrackNameList
            Statistic.__init__(self, region, track, track2, numDiscreteVals=numDiscreteVals, \
                               reducedNumDiscreteVals=reducedNumDiscreteVals, controlTrackNameList=controlTrackNameList, **kwArgs)

    def _createChildren(self):
        self._addChild( FlattenedDiscreteMarksHistStat(self._region, self._track, numDiscreteVals=self._numDiscreteVals, \
                                                       reducedNumDiscreteVals=self._reducedNumDiscreteVals, controlTrackNameList=self._controlTrackNameList) )
        self._addChild( FlattenedDiscreteMarksHistStat(self._region, self._track, numDiscreteVals=self._numDiscreteVals, \
                                                       reducedNumDiscreteVals=self._reducedNumDiscreteVals, controlTrackNameList=self._controlTrackNameList, \
                                                       marksStat='ExtractMarksStat') )
