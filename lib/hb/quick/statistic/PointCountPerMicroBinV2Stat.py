from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
#from gold.statistic.CountStat import CountStatSplittable, CountStatUnsplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.statistic.Statistic import StatisticConcatNumpyArrayResSplittable
import numpy as np
import math

class PointCountPerMicroBinV2Stat(MagicStatFactory):
    "Gives PointCountPerMicroBin, as a plain numpy array of values"
    pass

class PointCountPerMicroBinV2StatSplittable(StatisticConcatNumpyArrayResSplittable):
    pass
            
class PointCountPerMicroBinV2StatUnsplittable(Statistic):
    def _init(self, microBin=10000, **kwArgs):
        self.microBin = int(microBin)
            
    def _compute(self):
        tv = self._children[0].getResult()
        starts = tv.startsAsNumpyArray()
        binArray = starts/self.microBin
        binCounts = np.bincount(binArray)
        numMicroBins = int( math.ceil( float(len(self._region)) / self.microBin) )
        binCounts = np.concatenate([binCounts, np.zeros(numMicroBins-len(binCounts), dtype='int')])
        
        return binCounts
    
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False)) )
