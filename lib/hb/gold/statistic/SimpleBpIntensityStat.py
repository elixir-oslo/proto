from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.DiscreteMarksStat import DiscreteMarksStat
from gold.statistic.SimpleDiscreteMarksIntensityStat import SimpleDiscreteMarksIntensityStat
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq

class SimpleBpIntensityStat(MagicStatFactory):
    pass

#class SimpleBpIntensityStatSplittable(StatisticSumResSplittable):
#    IS_MEMOIZABLE = False
            
class SimpleBpIntensityStatUnsplittable(Statistic):    
    IS_MEMOIZABLE = False

    def __init__(self, region, track, track2, numDiscreteVals=None, **kwArgs):
        self._numDiscreteVals = numDiscreteVals
        Statistic.__init__(self, region, track, track2, numDiscreteVals=numDiscreteVals, **kwArgs)

    def _compute(self):
        discreteMarks = self._children[0].getResult()
        discreteMarksIntensities = self._children[1].getResult()
        return discreteMarksIntensities[discreteMarks]
    
    def _createChildren(self):
        self._addChild( DiscreteMarksStat(self._region, self._track, self._track2, numDiscreteVals=self._numDiscreteVals, printIntervals=True) )
        self._addChild( SimpleDiscreteMarksIntensityStat(self._region, self._track, self._track2, numDiscreteVals=self._numDiscreteVals) )
        self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(dense=False, interval=False)) )
