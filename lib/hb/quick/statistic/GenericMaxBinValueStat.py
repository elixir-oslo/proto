from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.StatisticV2 import StatisticV2, StatisticV2Splittable

class GenericMaxBinValueStat(MagicStatFactory):
    "takes as parameter another statistic class, gets results for this per bin, then at the global level returns the max of values per bin"
    pass

class GenericMaxBinValueStatSplittable(StatisticV2Splittable):
    def _combineResults(self):
        self._result = max(self._childResults)

    
class GenericMaxBinValueStatUnsplittable(StatisticV2):
    def _init(self, perBinStatistic, **kwArgs):
        self._perBinStatistic = self.getRawStatisticClass(perBinStatistic)
    
    def _compute(self):
        return self._children[0].getResult()
    
    def _createChildren(self):
        self._addChild( self._perBinStatistic(self._region, self._trackStructure, **self._kwArgs) )

#from gold.statistic.Statistic import StatisticSumResSplittable
#class StatisticTemplateStatSplittable(StatisticSumResSplittable):
#   pass
