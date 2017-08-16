from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import numpy

class KernelWeightedT1SegsInTpRawOverlapVersion2Stat(MagicStatFactory):
    pass

class KernelWeightedT1SegsInTpRawOverlapVersion2StatSplittable(StatisticSumResSplittable):
    pass
            
class KernelWeightedT1SegsInTpRawOverlapVersion2StatUnsplittable(Statistic):
    def _init(self, kernelType=None, spreadParam=None, **kwArgs):
        self._kernelType = kernelType
        self._spreadParam = int(spreadParam)
        
    def _compute(self):
        segsTv = self._children[0].getResult()
        
        #segsTv2 = self._children[1].getResult()
        
        #numData= numpy.zeros(len(segsTv2))
        #for seg in segsTv2:
        #    numData[seg.start(): seg.end()] = 1
            
        #aggregateInside = numData.dtype.type(0)
        aggregateInside = 0.0
        #for el,i in enumerate(self._children[1].getResult()):
        for i,el in enumerate(segsTv):
            slicedData= numpy.zeros(len(el))
            from gold.track.GenomeRegion import GenomeRegion
            segsTv2 = self._track2.getTrackView(GenomeRegion(self._region.genome, self._region.chr, self._region.start+el.start(), self._region.start+el.end() ))
            slicedData = segsTv2.getCoverageBpLevelArray()
            
            elementLen = el.end()-el.start()
            from quick.statistic.KernelUtilStat import KernelUtilStatUnsplittable
            kernel = KernelUtilStatUnsplittable.getKernel(elementLen, self._kernelType, self._spreadParam)
            assert len(slicedData)==len(kernel)
            weightedSlice = slicedData*kernel
            aggregateInside += weightedSlice.sum(dtype='float64')
        
        return aggregateInside
    
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=False, dense=False)) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(allowOverlaps=False, dense=False)) )
        
        
        

