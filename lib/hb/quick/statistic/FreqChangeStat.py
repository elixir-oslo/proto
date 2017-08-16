from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from gold.statistic.BinScaledPointCoverageStat import BinScaledPointCoverageStat
from numpy import array
#from gold.application.LogSetup import logMessage
class FreqChangeStat(MagicStatFactory):
    pass

class FreqChangeStatSplittable(StatisticSumResSplittable):
    def _combineResults(self):
        #logMessage(str(self._childResults))
        relevantMins = [x[0] for x in self._childResults]# if x is not None and not any(numpy.isnan(x))]
        relevantMaxs = [x[1] for x in self._childResults]
        if len(relevantMins)==0:
            return []
        else:
            avgMin = array(relevantMins).mean(dtype='float64')
            avgMax = array(relevantMaxs).mean(dtype='float64')
            return [avgMin, avgMax ]
                        
class FreqChangeStatUnsplittable(Statistic):    
    def _compute(self):
        freqs = self._children[0].getResult()
        return [min(freqs), max(freqs)]
    
    def _createChildren(self):
        self._addChild( BinScaledPointCoverageStat(self._region, self._track, numSubBins=2))
