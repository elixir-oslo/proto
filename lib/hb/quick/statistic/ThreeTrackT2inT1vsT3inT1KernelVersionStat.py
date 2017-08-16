from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.track.TrackFormat import TrackFormatReq
#from gold.statistic.RawOverlapStat import RawOverlapStat
from quick.statistic.KernelWeightedSumInsideStat import KernelWeightedSumInsideStat
from quick.statistic.KernelWeightedT1SegsInTpRawOverlapVersion2Stat import KernelWeightedT1SegsInTpRawOverlapVersion2Stat
#from quick.statistic.TpRawOverlapAllowSingleTrackOverlapsStat import TpRawOverlapAllowSingleTrackOverlapsStat
from gold.statistic.FormatSpecStat import FormatSpecStat
from quick.statistic.ThreeTrackT2inT1vsT3inT1Stat import ThreeTrackT2inT1vsT3inT1StatUnsplittable
from gold.statistic.SumInsideStat import SumInsideStat

class ThreeTrackT2inT1vsT3inT1KernelVersionStat(MagicStatFactory):
    pass

#class ThreeTrackT2inT1vsT3inT1PvalStatSplittable(StatisticDictSumResSplittable):
#    pass
            
class ThreeTrackT2inT1vsT3inT1KernelVersionStatUnsplittable(ThreeTrackT2inT1vsT3inT1StatUnsplittable):
    #def _compute(self):
    #    t2vst1 = self._t2vst1.getResult()
    #    t3vst1 = self._t3vst1.getResult()
    #    #t2t3RatioInsideT1 = float(t2vst1['Both']) / t3vst1['Both'] if t3vst1['Both']>0 else None
    #    t2t3RatioInsideT1 = float(t2vst1) / t3vst1 if t3vst1>0 else None
    #    
    #    return t2t3RatioInsideT1        

    def _init(self, kernelType='uniform', globalSource='', minimal=False, **kwArgs):
        self._kernelType = kernelType
        from quick.statistic.GenericRelativeToGlobalStat import GenericRelativeToGlobalStatUnsplittable
        self._globalSource = GenericRelativeToGlobalStatUnsplittable.getGlobalSource(globalSource, self.getGenome(), minimal)

    def _createChildren(self):
        "Takes three tracks: "
        t1,t2,t3 = self._tracks
        
        #print 'TEMP4: ',self._kernelType
        if self._kernelType == 'uniform':
            from quick.statistic.StatFacades import TpRawOverlapStat
            self._t2vst1 = self._addChild( TpRawOverlapStat(self._region, t2,t1, **self._kwArgs))
            self._t3vst1 = self._addChild( SumInsideStat(self._region, t1,t3, **self._kwArgs))
        elif self._kernelType == 'binSizeNormalizedV3':
            #from quick.statistic.TpProportionOverlapPerBinAvgStat import TpProportionOverlapPerBinAvgStat
            #from quick.statistic.MeanInsidePerBinAvgStat import MeanInsidePerBinAvgStat
            from quick.statistic.AggregateOfCoveredBpsInSegmentsStat import AggregateOfCoveredBpsInSegmentsStat
            from quick.statistic.AggregateOfCoverageInSegmentsStat import AggregateOfCoverageInSegmentsStat
            #self._t2vst1 = self._addChild( TpProportionOverlapPerBinAvgStat(self._region, t2,t1, **self._kwArgs))
            self._t2vst1 = self._addChild( AggregateOfCoverageInSegmentsStat(self._region, t2,t1, method='sum_of_mean', **self._kwArgs))
            #self._t3vst1 = self._addChild( MeanInsidePerBinAvgStat(self._region, t1,t3, **self._kwArgs))
            self._t3vst1 = self._addChild( AggregateOfCoveredBpsInSegmentsStat(self._region, t3,t1, method='sum_of_mean', **self._kwArgs))
            if self._kwArgs.get('useNormalizedTestStatistic')=='yes':
                from gold.statistic.CountSegmentStat import CountSegmentStat
                from gold.statistic.SumStat import SumStat
                self._globalT2CoverageStat = self._addChild(CountSegmentStat(self._region, t2, **self._kwArgs))
                self._globalT3CoverageStat = self._addChild(SumStat(self._region, t3, **self._kwArgs))            
        else:
            #self._t2vst1 = self._addChild( KernelWeightedT1SegsInTpRawOverlapStat(self._region, t1,t2, **self._kwArgs))
            self._t2vst1 = self._addChild( KernelWeightedT1SegsInTpRawOverlapVersion2Stat(self._globalSource, t1,t2, **self._kwArgs))
            self._t3vst1 = self._addChild( KernelWeightedSumInsideStat(self._globalSource, t3,t1, **self._kwArgs))

        self._addChild( FormatSpecStat(self._region, t1, TrackFormatReq(allowOverlaps=False)) )
        self._addChild( FormatSpecStat(self._region, t2, TrackFormatReq(allowOverlaps=False)) )
        #self._addChild( FormatSpecStat(self._region, t3, TrackFormatReq(allowOverlaps=True)) )
