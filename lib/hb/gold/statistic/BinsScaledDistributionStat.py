from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSplittable, OnlyGloballySplittable
from collections import OrderedDict
import numpy

class BinsScaledDistributionStat(MagicStatFactory):
    pass

class BinsScaledDistributionStatSplittable(StatisticSplittable, OnlyGloballySplittable):
    def __init__(self, region, track, track2=None, numSubBins=10, **kwArgs):
        #track2 is ignored..
        self._numSubBins = int(numSubBins)
        StatisticSplittable.__init__(self, region, track, track2, numSubBins=numSubBins, **kwArgs)
        
    def _combineResults(self):
        relevantResults = [x for x in self._childResults if x is not None and not any(numpy.isnan(x))]
        if len(relevantResults)==0:
            self._result = None
        else:
            resultsAsNumpy = numpy.concatenate(relevantResults)
            resultsAsNumpy = resultsAsNumpy.reshape((-1,self._numSubBins))
            mean = resultsAsNumpy.mean(axis=0)
            sdOfMean = resultsAsNumpy.std(axis=0) / resultsAsNumpy.shape[0]**0.5
            self._result = {'Result':OrderedDict([('mean', mean), ('sdOfMean', sdOfMean)])}
            
class BinsScaledDistributionStatUnsplittable(Statistic):    
    def __init__(self, region, track, track2=None, numSubBins=10, **kwArgs):
        #track2 is ignored..
        self._numSubBins = int(numSubBins)
        Statistic.__init__(self, region, track, track2, numSubBins=numSubBins, **kwArgs)

    def _compute(self):
        raise
    
    def _calcSplitPoints(self):
        pass
    
    def _createChildren(self):
        raise

    def _getSplitPoints(self):
        bpSize = self._children[0].getResult()
        #splitPoints = [ bpSize*i/self._numSubBins for i in xrange(self._numSubBins+1)]
        return numpy.arange(self._numSubBins+1) * bpSize / self._numSubBins
    
    def _getSubBins(self):
        splitPoints = self._getSplitPoints()
        return zip(splitPoints[:-1], splitPoints[1:])

