from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.FormatSpecStat import FormatSpecStat
from quick.statistic.ValueBpLevelArrayRawDataStat import ValueBpLevelArrayRawDataStat
from quick.statistic.BpLevelArrayRawDataStat import BpLevelArrayRawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import NotSupportedError
from gold.application.LogSetup import logLackOfSupport

class AggregateOfCoveredBpsInSegmentsStat(MagicStatFactory):
    pass

class AggregateOfCoveredBpsInSegmentsStatSplittable(StatisticSumResSplittable):
    pass

class AggregateOfCoveredBpsInSegmentsStatUnsplittable(Statistic):
    def _init(self, method='sum_of_sum', **kwArgs):
        self._method = method
        if method == 'mean_of_mean':
            errorMsg = 'AggregateOfCoveredBpsInSegmentsStat does not support "mean_of_mean".'
            logLackOfSupport(errorMsg)
            raise NotSupportedError(errorMsg)

    def _compute(self):
        numData = self._valBpArrayStat.getResult()
        segData = self._segmentBpArrayStat.getResult()

        if self._method == 'sum_of_sum':
            overlappingVals = numData[segData]
            return overlappingVals.sum()
        else:
            #fixme: Can this be optimized further?

            segsTv = self._segStat.getResult()

            aggregateInside = numData.dtype.type(0)

            for i,el in enumerate(segsTv):
                slicedData = numData[el.start():el.end()]
                aggregateInside += slicedData.mean(dtype='float64')

            if self._method == 'mean_of_mean' and segsTv.getNumElements() > 0:
                aggregateInside /= 1.0 * (i+1)

            return aggregateInside


        #valsTv = self._children[0].getResult()
        #segsTv = self._children[1].getResult()
        ##print valsTv.startsAsNumpyArray()
        #
        #if valsTv.trackFormat.reprIsDense():
        #    numData = valsTv.valsAsNumpyArray()
        #    #for el in self._children[0].getResult():
        #    #    aggregateInside += numData[el.start():el.end()].sum(dtype='float64')
        #    #return aggregateInside
        #    #
        #else:
        #    numData = valsTv.getValueBpLevelArray(0)

        #aggregateInside = numData.dtype.type(0)
        #
        ##for el,i in enumerate(self._children[1].getResult()):
        #for i,el in enumerate(segsTv):
        #    slicedData = numData[el.start():el.end()]
        #    #print 'TEMP8: ',self._track.trackName, len(el), el.start(), el.end(), sum(slicedData)
        #    if self._method == 'sum_of_sum':
        #        aggregateInside += slicedData.sum(dtype='float64')
        #    elif self._method in ['sum_of_mean', 'mean_of_mean']:
        #        aggregateInside += slicedData.mean(dtype='float64')
        #
        #if self._method == 'mean_of_mean' and segsTv.getNumElements() > 0:
        #    aggregateInside /= 1.0 * (i+1)
        #
        #return aggregateInside

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
        self._valBpArrayStat = self._addChild( ValueBpLevelArrayRawDataStat(self._region, self._track, voidValue=0) )
        self._addChild( FormatSpecStat(self._region, self._track, TrackFormatReq(allowOverlaps=False, val='number')) )

        self._segmentBpArrayStat = self._addChild( BpLevelArrayRawDataStat(self._region, self._track2, bpDepthType='binary') )
        self._segStat = self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(allowOverlaps=False, dense=False, interval=True)) )
