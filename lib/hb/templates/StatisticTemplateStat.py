from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic  # , StatisticSumResSplittable


class XyzStat(MagicStatFactory):
    """
    Statistic description
    """
    pass


# class XyzStatSplittable(StatisticSumResSplittable):
#    pass


class XyzStatUnsplittable(Statistic):
    def _compute(self):
        pass
    
    def _createChildren(self):
        pass
