from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawOverlapStat import RawOverlapStat
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq

class ProportionOverlapStat(MagicStatFactory):
    pass

class ProportionOverlapStatUnsplittable(Statistic):
    def _compute(self):
        res = self._children[0].getResult()

        n = sum( res[key] for key in ['Neither','Only1','Only2','Both'] )

        res['NeitherProp'] = res['Neither']*1.0/n
        res['Only1Prop'] = res['Only1']*1.0/n
        res['Only2Prop'] = res['Only2']*1.0/n
        res['BothProp'] = res['Both']*1.0/n
        
        return res

    def _createChildren(self):
        self._addChild( RawOverlapStat(self._region, self._track, self._track2) )
        self._addChild( FormatSpecStat(self._region, self._track, TrackFormatReq(dense=False, interval=True)) )
        self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True)) )

        

