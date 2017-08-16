from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.CommonStatisticalTests import pearsonCC
from gold.description.StatDescriptionList import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class LongitudinalCorrStat(MagicStatFactory):
    pass

#class LongitudinalCorrStatSplittable(StatisticSumResSplittable):
#    pass
            
class LongitudinalCorrStatUnsplittable(Statistic):    
    def _compute(self):
        tv = self._children[0].getResult()
        vals = tv.valsAsNumpyArray()
        valsFirsts = vals[:-1]
        valsLasts = vals[1:]
        return pearsonCC(valsFirsts, valsLasts)
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='number')) )
