from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import RatioDictSingleDenomStatUnsplittable
from gold.statistic.BpCoverageByCatStat import BpCoverageByCatStat
from quick.statistic.BinSizeStat import BinSizeStat

class PropCoverageByCatStat(MagicStatFactory):
    pass

#class PropCoverageByCatStatSplittable(StatisticSumResSplittable):
#    pass

class PropCoverageByCatStatUnsplittable(RatioDictSingleDenomStatUnsplittable):    
    def _createChildren(self):
        self._addChild( BpCoverageByCatStat(self._region, self._track) )
        self._addChild( BinSizeStat(self._region, self._track) )
