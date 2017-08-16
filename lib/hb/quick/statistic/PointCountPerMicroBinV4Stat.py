from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
#from gold.statistic.CountStat import CountStatSplittable, CountStatUnsplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import numpy as np
import math
from gold.track.TrackView import TrackView

class PointCountPerMicroBinV4Stat(MagicStatFactory):
    "Gives PointCountPerMicroBin, as a mapping from Genome Region object to count"
    pass

#class PointCountPerMicroBinV4StatSplittable(StatisticConcatResSplittable):
#    pass
            
class PointCountPerMicroBinV4StatUnsplittable(Statistic):
    def _init(self, microBin=10000, **kwArgs):
        self.microBin = int(microBin)
            
    def _compute(self):
        tv = self._children[0].getResult()
        starts = tv.startsAsNumpyArray()
        binArray = starts/self.microBin
        binCounts = np.bincount(binArray)
        numMicroBins = int( math.ceil( float(len(self._region)) / self.microBin) )
        binCounts = np.concatenate([binCounts, np.zeros(numMicroBins-len(binCounts), dtype='int')])
        #print 'temp1: ', len(binCounts)
        assert [i*self.microBin for i in xrange(len(binCounts))] == range(0, len(self._region), self.microBin), ([i*self.microBin for i in xrange(len(binCounts))], range(0, len(self._region), self.microBin) )
        startList = [i*self.microBin for i in xrange(len(binCounts))]
        assert [min( (i+1)*self.microBin, len(self._region)) for i in xrange(len(binCounts))] == startList[1:] + [len(self._region)]
        endList = [min( (i+1)*self.microBin, len(self._region)) for i in xrange(len(binCounts))]
        #print ','.join([str(x) for x in binCounts])
        return TrackView(genomeAnchor=tv.genomeAnchor, startList=np.array(startList), endList=np.array(endList), valList=binCounts, \
                          strandList=None, idList=None, edgesList=None, weightsList=None, borderHandling=tv.borderHandling, allowOverlaps=False)
        #return [GenomeElement(self._region.genome, self._region.chr, 
        #        self._region.start+i*self.microBin, min(self._region.start+(i+1)*self.microBin, self._region.end), 
        #        binCounts[i])
        #        for i in xrange(len(binCounts))]            
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False, allowOverlaps=True)) )
