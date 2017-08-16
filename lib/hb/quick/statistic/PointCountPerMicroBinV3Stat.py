from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
#from gold.statistic.CountStat import CountStatSplittable, CountStatUnsplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.statistic.Statistic import StatisticConcatResSplittable
from gold.origdata.GenomeElement import GenomeElement
import numpy as np
import math

class PointCountPerMicroBinV3Stat(MagicStatFactory):
    "Gives PointCountPerMicroBin, as a mapping from Genome Region object to count"
    pass

class PointCountPerMicroBinV3StatSplittable(StatisticConcatResSplittable):
    pass
            
class PointCountPerMicroBinV3StatUnsplittable(Statistic):
    def _init(self, microBin=10000, **kwArgs):
        self.microBin = int(microBin)
            
    def _compute(self):
        tv = self._children[0].getResult()
        starts = tv.startsAsNumpyArray()
        binArray = starts/self.microBin
        binCounts = np.bincount(binArray)
        numMicroBins = int( math.ceil( float(len(self._region)) / self.microBin) )
        binCounts = np.concatenate([binCounts, np.zeros(numMicroBins-len(binCounts), dtype='int')])
        return [GenomeElement(self._region.genome, self._region.chr, 
                self._region.start+i*self.microBin, min(self._region.start+(i+1)*self.microBin, self._region.end), 
                binCounts[i])
                for i in xrange(len(binCounts))]            
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False, allowOverlaps=True)) )
