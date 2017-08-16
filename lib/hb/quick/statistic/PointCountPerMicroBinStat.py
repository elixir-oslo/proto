from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
#from gold.statistic.CountStat import CountStatSplittable, CountStatUnsplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import numpy as np
import math

class PointCountPerMicroBinStat(MagicStatFactory):
    "Gives PointCountPerMicroBin, as a mapping from bin index to count"
    pass

#class PointCountPerMicroBinStatSplittable(StatisticSumResSplittable):
#    pass
            
class PointCountPerMicroBinStatUnsplittable(Statistic):
    def _init(self, microBin=10000, **kwArgs):
        self.microBin = int(microBin)
            
    def _compute(self):
        tv = self._children[0].getResult()
        starts = tv.startsAsNumpyArray()
        binArray = starts/self.microBin
        binCounts = np.bincount(binArray)
        numMicroBins = int( math.ceil( float(len(self._region)) / self.microBin) )
        binCounts = np.concatenate([binCounts, np.zeros(numMicroBins-len(binCounts), dtype='int')])
        
        return dict( [ (str(index), binCounts[index]) for index in xrange(len(binCounts)) ] )
    
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False)) )
