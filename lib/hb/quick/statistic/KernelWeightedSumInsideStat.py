from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import NotSupportedError
from gold.application.LogSetup import logLackOfSupport

class KernelWeightedSumInsideStat(MagicStatFactory):
    pass

class KernelWeightedSumInsideStatSplittable(StatisticSumResSplittable):
    pass
            
class KernelWeightedSumInsideStatUnsplittable(Statistic):
    def _init(self, method='sum_of_sum', kernelType=None, spreadParam=None, **kwArgs):
        self._method = method
        if method != 'sum_of_sum':
            errorMsg = 'KernelWeightedSumInsideStat only supports "sum_of_sum".'
            logLackOfSupport(errorMsg)
            raise NotSupportedError(errorMsg)
        self._kernelType = kernelType
        self._spreadParam = int(spreadParam)
        
    def _compute(self):
        valsTv = self._children[0].getResult()
        segsTv = self._children[1].getResult()
        #print valsTv.startsAsNumpyArray()
        
        if valsTv.trackFormat.reprIsDense():            
            numData = valsTv.valsAsNumpyArray()
            #for el in self._children[0].getResult():
            #    aggregateInside += numData[el.start():el.end()].sum()
            #return aggregateInside
            #
        else:
            numData = valsTv.getValueBpLevelArray(0)
            
        aggregateInside = numData.dtype.type(0)
        
        #for el,i in enumerate(self._children[1].getResult()):
        for i,el in enumerate(segsTv):
            slicedData = numData[el.start():el.end()]
            elementLen = el.end()-el.start()
            from quick.statistic.KernelUtilStat import KernelUtilStatUnsplittable
            kernel = KernelUtilStatUnsplittable.getKernel(elementLen, self._kernelType, self._spreadParam)
            weightedSlice = slicedData*kernel
            #if self._method == 'sum_of_sum':
            #print 'TEMP6: ',self._track.trackName, len(el), el.start(), el.end(), sum(slicedData), sum(weightedSlice)
            aggregateInside += weightedSlice.sum(dtype='float64')
            #elif self._method in ['sum_of_mean', 'mean_of_mean']:
            #    aggregateInside += slicedData.mean(dtype='float64')
                
        #if self._method == 'mean_of_mean' and len(segsTv):
        #    aggregateInside /= 1.0 * i
        
        return aggregateInside
    
            
            
            
        #starts, ends = tv1.startsAsNumpyArray(), tv1.endsAsNumpyArray()
        #regionVals = np.zeros(startRegion.size)
        #tv2 = self._children[1].getResult()
        #startSF, endSF, valSF = tv2.startsAsNumpyArray(), tv2.endsAsNumpyArray(), tv2.valsAsNumpyArray()
        ##eventPostions = self._children[2].getResult()
        #regionPos, index = 0, 0
        #regionSize=startRegion.size
        #sfSize = startSF.size
        #
        
        #if regionSize > 0:
        #    while index<startSF.size:
        #        # region ligger foran sfReg
        #        if startRegion[regionPos]>=endSF[index]:
        #            index+=1
        #            while index<sfSize and startRegion[regionPos]>=endSF[index]:
        #                index+=1
        #            if index == sfSize:
        #                break
        #            regionVals[regionPos] += valSF[index]*(min(endRegion[regionPos], endSF[index])-startRegion[regionPos])
        #            
        #        # region ligger etter sfReg   
        #        elif endRegion[regionPos]<=startSF[index]:
        #            regionPos+=1
        #            while regionPos< regionSize and endRegion[pos]<=startSF[index]:
        #                regionPos+=1
        #            if regionPos == regionSize:
        #                break
        #            regionVals[regionPos] +=  valSF[index]*(min(endRegion[regionPos], endSF[index])-startRegion[regionPos])                
        #        #sfReg ligger i region
        #        elif endRegion[regionPos]>startSF[index]>=startRegion[regionPos]:
        #            if index>0 and startSF[index]>startRegion[regionPos] > startSF[index-1]:
        #                regionVals[regionPos] += valSF[index-1]*( startSF[index]-startRegion[regionPos])
        #            regionVals[regionPos] +=  valSF[index]*(min(endRegion[regionPos], endSF[index])-startSF[index])
        #        index+=1
        #else:
        #    newVals = ['']
        #segBorders = np.array(uniquePoints) + tv.genomeAnchor.start
        #return TrackView(genomeAnchor = tv1.genomeAnchor, startList=startRegion, endList=endRegion, valList=regionVals, \
        #                 strandList=None, borderHandling=tv1.borderHandling, allowOverlaps=tv1.allowOverlaps)
        
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=False, val='number')) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(allowOverlaps=False, dense=False)) )
        
        

