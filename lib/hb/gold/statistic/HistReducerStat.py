from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.DiscreteMarksHistStat import DiscreteMarksHistStat
from numpy import arange

class HistReducerStat(MagicStatFactory):
    pass

#class HistReducerStatSplittable(StatisticSumResSplittable):
#    IS_MEMOIZABLE = False
            
class HistReducerStatUnsplittable(Statistic):    
    IS_MEMOIZABLE = False

    def __init__(self, region, track, track2=None, numDiscreteVals=None, reducedNumDiscreteVals=None, **kwArgs):
        self._numDiscreteVals = int(numDiscreteVals)
        self._reducedNumDiscreteVals = int(reducedNumDiscreteVals)
        assert numDiscreteVals is not None and numDiscreteVals==reducedNumDiscreteVals
        Statistic.__init__(self, region, track, track2, numDiscreteVals=numDiscreteVals, reducedNumDiscreteVals=reducedNumDiscreteVals, **kwArgs)

    def _compute(self):
        return arange(self._numDiscreteVals)
    
    def _createChildren(self):
        self._addChild( DiscreteMarksHistStat(self._region, self._track, numDiscreteVals=self._numDiscreteVals) )
        
