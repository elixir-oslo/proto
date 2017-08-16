from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.DiscreteMarksStat import DiscreteMarksStat
from gold.statistic.AbstractHistStat import AbstractHistStatUnsplittable

class DiscreteMarksHistStat(MagicStatFactory):
    pass

#class DiscreteMarksHistStatSplittable(StatisticSumResSplittable):
#    IS_MEMOIZABLE = False
            

class DiscreteMarksHistStatUnsplittable(AbstractHistStatUnsplittable):    
    def __init__(self, region, track, track2=None, numDiscreteVals=None, marksStat='MarksListStat', **kwArgs):
        self._numDiscreteVals = numDiscreteVals
        self._marksStat = marksStat

        self._numHistBins = int(self._numDiscreteVals)

        Statistic.__init__(self, region, track, track2, numDiscreteVals=numDiscreteVals, marksStat=marksStat, **kwArgs)
    
    def _createChildren(self):
        self._addChild( DiscreteMarksStat(self._region, self._track, (self._track2 if hasattr(self,'_track2') else None),\
                                          numDiscreteVals=self._numDiscreteVals, marksStat=self._marksStat) )

