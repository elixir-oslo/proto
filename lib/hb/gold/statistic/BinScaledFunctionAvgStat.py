from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.BinsScaledDistributionStat import *
from quick.statistic.BinSizeStat import BinSizeStat
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import numpy

class BinScaledFunctionAvgStat(MagicStatFactory):
    pass

class BinScaledFunctionAvgStatSplittable(BinsScaledDistributionStatSplittable):
    pass
            
class BinScaledFunctionAvgStatUnsplittable(BinsScaledDistributionStatUnsplittable):    
    def _compute(self):
        tv1 = self._children[1].getResult()        
        vals = tv1.valsAsNumpyArray()
        if len(vals) < self._numSubBins:
            return None
        
        splitPoints = self._getSplitPoints()
        #subBinMeans = [vals[bpStart:bpEnd].mean(dtype='float64') for bpStart,bpEnd in self._getSubBins()]
        #return numpy.array(subBinMeans)
        subBinSums = numpy.add.reduceat(vals, splitPoints[:-1])
        subBinCounts = splitPoints[1:] - splitPoints[:-1]

        res = 1.0 * subBinSums / subBinCounts
        if self._region.strand == False:
            res = res[::-1]
        return res    
    
    def _createChildren(self):
        self._addChild( BinSizeStat(self._region, self._track))
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='number', dense=True)) )
