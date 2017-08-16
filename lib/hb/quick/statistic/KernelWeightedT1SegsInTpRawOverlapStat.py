from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.BpLevelArrayRawDataStat import BpLevelArrayRawDataStat

class KernelWeightedT1SegsInTpRawOverlapStat(MagicStatFactory):
    pass

class KernelWeightedT1SegsInTpRawOverlapStatSplittable(StatisticSumResSplittable):
    pass
            
class KernelWeightedT1SegsInTpRawOverlapStatUnsplittable(Statistic):
    def _init(self, kernelType=None, spreadParam=None, **kwArgs):
        self._kernelType = kernelType
        self._spreadParam = int(spreadParam)
        
    def _compute(self):
        segsTv = self._children[0].getResult()
        numData= self._children[1].getResult()
        aggregateInside = numData.dtype.type(0)
        #for el,i in enumerate(self._children[1].getResult()):
        for i,el in enumerate(segsTv):
            slicedData = numData[el.start():el.end()]
            elementLen = el.end()-el.start()
            from quick.statistic.KernelUtilStat import KernelUtilStatUnsplittable
            kernel = KernelUtilStatUnsplittable.getKernel(elementLen, self._kernelType, self._spreadParam)
            weightedSlice = slicedData*kernel
            aggregateInside += weightedSlice.sum(dtype='float64')
        
        return aggregateInside
    
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=False, dense=False)) )
        self._addChild( BpLevelArrayRawDataStat(self._region, self._track2) )
        
        

