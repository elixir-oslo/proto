from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawOverlapStat import RawOverlapStat

class PropOverlapStat(MagicStatFactory):
    pass

#class PropOverlapStatSplittable(StatisticSumResSplittable):
#    pass
            
class PropOverlapStatUnsplittable(Statistic):    
    def _compute(self):
        res = self._children[0].getResult()
        return 1.0 * res['Both'] / max(res['Both'] + res['Only1'], 1)

    def _createChildren(self):
        self._addChild( RawOverlapStat(self._region, self._track, self._track2) )
