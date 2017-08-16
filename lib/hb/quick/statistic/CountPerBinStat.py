from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.CountElementStat import CountElementStat

class CountPerBinStat(MagicStatFactory):
    "Returns at global level a list of the count of elements (using CountElementStat) for each bin"
    pass

class CountPerBinStatUnsplittable(Statistic):
    def _compute(self):
        return [ self._children[0].getResult() ]
    
    def _createChildren(self):
        self._addChild( CountElementStat(self._region, self._track))

from gold.statistic.Statistic import StatisticConcatResSplittable
class CountPerBinStatSplittable(StatisticConcatResSplittable):
    pass
