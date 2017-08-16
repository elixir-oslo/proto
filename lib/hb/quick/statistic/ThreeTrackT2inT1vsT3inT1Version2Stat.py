from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.track.TrackFormat import TrackFormatReq
#from gold.statistic.RawOverlapStat import RawOverlapStat
#from quick.statistic.TpRawOverlapAllowSingleTrackOverlapsStat import TpRawOverlapAllowSingleTrackOverlapsStat
from gold.statistic.FormatSpecStat import FormatSpecStat
from quick.statistic.ThreeTrackT2inT1vsT3inT1Stat import ThreeTrackT2inT1vsT3inT1StatUnsplittable

class ThreeTrackT2inT1vsT3inT1Version2Stat(MagicStatFactory):
    pass

#class ThreeTrackT2inT1vsT3inT1PvalStatSplittable(StatisticDictSumResSplittable):
#    pass
            
class ThreeTrackT2inT1vsT3inT1Version2StatUnsplittable(ThreeTrackT2inT1vsT3inT1StatUnsplittable):
    #def _compute(self):
    #    t2vst1 = self._t2vst1.getResult()
    #    t3vst1 = self._t3vst1.getResult()
    #    #t2t3RatioInsideT1 = float(t2vst1['Both']) / t3vst1['Both'] if t3vst1['Both']>0 else None
    #    t2t3RatioInsideT1 = float(t2vst1) / t3vst1 if t3vst1>0 else None
    #    
    #    return t2t3RatioInsideT1        
        
    def _createChildren(self):
        from quick.statistic.StatFacades import TpRawOverlapStat
        t1,t2,t3 = self._tracks
        from gold.statistic.MeanInsideStat import SumInsideStat
        self._t2vst1 = self._addChild( TpRawOverlapStat(self._region, t2,t1, **self._kwArgs))
        self._t3vst1 = self._addChild( SumInsideStat(self._region, t1,t3, **self._kwArgs))
        self._addChild( FormatSpecStat(self._region, t1, TrackFormatReq(allowOverlaps=False)) )
        self._addChild( FormatSpecStat(self._region, t2, TrackFormatReq(allowOverlaps=False)) )
        #self._addChild( FormatSpecStat(self._region, t3, TrackFormatReq(allowOverlaps=True)) )
