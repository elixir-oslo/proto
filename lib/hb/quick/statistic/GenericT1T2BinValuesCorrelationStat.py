from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSplittable


class GenericT1T2BinValuesCorrelationStat(MagicStatFactory):
    "takes as parameter another statistic class, gets results for this per bin, then at the global level returns the max of values per bin"
    pass

class GenericT1T2BinValuesCorrelationStatSplittable(StatisticSplittable):
    def _init(self, corrMethod, **kwArgs):
        assert corrMethod in ['pearson','spearman','kendall']
        self._corrMethod = corrMethod
        
    def _combineResults(self):
        from proto.RSetup import robjects, r
        rVec1 = robjects.FloatVector([x[0] for x in self._childResults])
        rVec2 = robjects.FloatVector([x[1] for x in self._childResults])
        return r.cor(rVec1, rVec2, method=self._corrMethod)
        
        
    
class GenericT1T2BinValuesCorrelationStatUnsplittable(Statistic):
    def _init(self, perBinStatistic, **kwArgs):
        self._perBinStatistic = self.getRawStatisticClass(perBinStatistic)
    
    def _compute(self):
        return [self._children[0].getResult(), self._children[1].getResult()]
    
    def _createChildren(self):
        self._addChild( self._perBinStatistic(self._region, self._track, **self._kwArgs) )
        self._addChild( self._perBinStatistic(self._region, self._track2, **self._kwArgs) )
