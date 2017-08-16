from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.HistReducerStat import HistReducerStat
from gold.statistic.DiscreteMarksStat import DiscreteMarksStat

class DiscreteMarkReducerStat(MagicStatFactory):
    pass

#class DiscreteMarkReducerStatSplittable(StatisticSumResSplittable):
#    IS_MEMOIZABLE = False
            
class DiscreteMarkReducerStatUnsplittable(Statistic):    
    IS_MEMOIZABLE = False

    def __init__(self, region, track, track2=None, numDiscreteVals=None, reducedNumDiscreteVals=None, marksStat='MarksListStat', **kwArgs):
        self._numDiscreteVals = numDiscreteVals
        self._reducedNumDiscreteVals = reducedNumDiscreteVals
        assert numDiscreteVals is not None and numDiscreteVals==reducedNumDiscreteVals
        self._marksStat = marksStat
        Statistic.__init__(self, region, track, track2, numDiscreteVals=numDiscreteVals, \
                           reducedNumDiscreteVals=reducedNumDiscreteVals, marksStat=marksStat, **kwArgs)

    def _compute(self):
        discreteMarkMapper = self._children[0].getResult()
        discreteMarks = self._children[1].getResult()
        return discreteMarkMapper[discreteMarks]
        #return self._children[1].getResult()
    
    def _createChildren(self):
        self._addChild( HistReducerStat(self._region, self._track, \
                                        numDiscreteVals=self._numDiscreteVals, reducedNumDiscreteVals=self._reducedNumDiscreteVals) )
        self._addChild( DiscreteMarksStat(self._region, self._track, (self._track2 if hasattr(self,'_track2') else None),\
                                          numDiscreteVals=self._numDiscreteVals, marksStat=self._marksStat) )
