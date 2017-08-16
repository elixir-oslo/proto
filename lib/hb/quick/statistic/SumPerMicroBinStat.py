from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
#from gold.statistic.CountStat import CountStatSplittable, CountStatUnsplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import numpy as np
import math
from gold.track.TrackView import TrackView

class SumPerMicroBinStat(MagicStatFactory):
    "Not yet functioning.."
    pass

#class SumPerMicroBinStatSplittable(StatisticConcatResSplittable):
#    pass
            
class SumPerMicroBinStatUnsplittable(Statistic):
    def _init(self, microBin=10000, **kwArgs):
        self.microBin = int(microBin)
            
    def _compute(self):
        raise #not finished implementing..

        tv = self._children[0].getResult()
        vals = tv.valsAsNumpyArray()
        numMicroBins = int( math.ceil( float(len(self._region)) / self.microBin) )
        miBinBorders = range(0, len(self._region), self.microBin) + [len(self._region)]
        miBins = []
        #go from borders 0,10,20 to paired bin intervals 0,10, 10,20, 20,30 ...
        for i,b in enumerate(miBinBorders):
            miBins.append(b)
            if i!=0 and i!=len(miBinBorders)-1:
                miBins.append(b)
        accVals = vals.add.reduceat(vals, miBins)[::2]
        binCounts = accVals
        #print 'temp1: ', len(binCounts)
        #Fix asserts here..
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
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=True, interval=False, allowOverlaps=False)) )
