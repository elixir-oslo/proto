import math
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.VarianceStat import VarianceStat

class StdDevStat(MagicStatFactory):
    pass

class StdDevStatUnsplittable(Statistic):
    def _compute(self):
        variance = float(self._children[0].getResult())
        return 1.0 * math.sqrt( variance )
        
    def _createChildren(self):
        self._addChild( VarianceStat(self._region, self._track) )
