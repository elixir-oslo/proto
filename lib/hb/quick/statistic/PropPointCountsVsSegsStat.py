from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawOverlapStat import RawOverlapStat
from gold.statistic.ProportionCountStat import ProportionCountStat
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq
from collections import OrderedDict

class PropPointCountsVsSegsStat(MagicStatFactory):
    pass

class PropPointCountsVsSegsStatUnsplittable(Statistic):
    def _compute(self):
        overlap = self._rawOverlap.getResult()
        res = OrderedDict([('Both', overlap['Both']), ('Only1', overlap['Only1'])])
        
        totPointCount = sum( res.values() )
        res['BothProp'] = res['Both']*1.0/totPointCount if totPointCount != 0 else None
        res['Only1Prop'] = res['Only1']*1.0/totPointCount if totPointCount != 0 else None
        res['SegCoverage'] = self._segmentCoverProportion.getResult()
        
        return res
        
    def _createChildren(self):
        self._rawOverlap = self._addChild( RawOverlapStat(self._region, self._track, self._track2) )
        self._segmentCoverProportion = self._addChild( ProportionCountStat(self._region, self._track2) )
        self._addChild( FormatSpecStat(self._region, self._track, TrackFormatReq(dense=False, interval=False)) )
        self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True)) )
