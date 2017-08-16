from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import RatioStatUnsplittable
from gold.statistic.CountStat import CountStat
from gold.statistic.SumStat import SumStat

class MeanStat(MagicStatFactory):
    '''Calculates the mean of the values associated with each element.
    '''
    pass

class MeanStatUnsplittable(RatioStatUnsplittable):
    def _createChildren(self):
        self._addChild( SumStat(self._region, self._track) )
        self._addChild( CountStat(self._region, self._track) )

