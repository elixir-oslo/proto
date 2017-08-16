from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleRawDataStatistic
from gold.track.TrackFormat import TrackFormatReq
#from gold.statistic.RawOverlapStat import RawOverlapStat
from quick.statistic.TpRawOverlapAllowSingleTrackOverlapsStat import TpRawOverlapAllowSingleTrackOverlapsStat
from gold.statistic.FormatSpecStat import FormatSpecStat
import numpy

class ThreeTrackT2inT1vsT3inT1Stat(MagicStatFactory):
    pass

#class ThreeTrackT2inT1vsT3inT1PvalStatSplittable(StatisticDictSumResSplittable):
#    pass
            
class ThreeTrackT2inT1vsT3inT1StatUnsplittable(MultipleRawDataStatistic):
    def _compute(self):
        t2vst1 = self._t2vst1.getResult()
        t3vst1 = self._t3vst1.getResult()
        #t2t3RatioInsideT1 = float(t2vst1['Both']) / t3vst1['Both'] if t3vst1['Both']>0 else None        
        #t2t3RatioInsideT1 = float(t2vst1) / t3vst1 if t3vst1>0 else numpy.nan
        t2t3RatioInsideT1 = float(t2vst1) / t3vst1 if t3vst1>0 else numpy.nan
        if self._kwArgs.get('useNormalizedTestStatistic')=='yes' and not numpy.isnan(t2t3RatioInsideT1):
            globalT2t3Ratio = self._globalT2CoverageStat.getResult() / self._globalT3CoverageStat.getResult()
            return t2t3RatioInsideT1 / globalT2t3Ratio
        else:
            return t2t3RatioInsideT1        
        
    def _createChildren(self):
        from quick.statistic.StatFacades import TpRawOverlapStat
        t1,t2,t3 = self._tracks
        if self._configuredToAllowOverlaps(strict=False):
            self._t2vst1 = self._addChild( TpRawOverlapAllowSingleTrackOverlapsStat(self._region, t2,t1))
            self._t3vst1 = self._addChild( TpRawOverlapAllowSingleTrackOverlapsStat(self._region, t3,t1))
            self._addChild( FormatSpecStat(self._region, t1, TrackFormatReq(allowOverlaps=True)) )
            self._addChild( FormatSpecStat(self._region, t2, TrackFormatReq(allowOverlaps=True)) )
            self._addChild( FormatSpecStat(self._region, t3, TrackFormatReq(allowOverlaps=True)) )
        elif self._kwArgs.get('onlyT3WithOverlap') == 'yes':
            #self._t2vst1 = self._addChild( TpRawOverlapAllowSingleTrackOverlapsStat(self._region, t2,t1, **self._kwArgs))
            self._t2vst1 = self._addChild( TpRawOverlapStat(self._region, t2,t1, **self._kwArgs))
            self._t3vst1 = self._addChild( TpRawOverlapAllowSingleTrackOverlapsStat(self._region, t3,t1, **self._kwArgs))
            self._addChild( FormatSpecStat(self._region, t1, TrackFormatReq(allowOverlaps=False)) )
            self._addChild( FormatSpecStat(self._region, t2, TrackFormatReq(allowOverlaps=False)) )
            self._addChild( FormatSpecStat(self._region, t3, TrackFormatReq(allowOverlaps=True)) )
        else:
            self._t2vst1 = self._addChild( TpRawOverlapStat(self._region, t2,t1))
            self._t3vst1 = self._addChild( TpRawOverlapStat(self._region, t3,t1))
