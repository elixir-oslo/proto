from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import RatioStatUnsplittable
#from gold.statistic.RawDataStat import RawDataStat
#from quick.statistic.BinSizeStat import BinSizeStat
#from quick.statistic.SegmentDistancesStat import SegmentDistancesStat
from quick.statistic.VarOfGapsStat import VarOfGapsStat
from quick.statistic.MeanOfGapsStat import MeanOfGapsStat

class PoissonVarToExpOfGapsStat(MagicStatFactory):
    pass

#class PoissonVarToExpOfGapsStatSplittable(StatisticSumResSplittable, OnlyGloballySplittable):
#    IS_MEMOIZABLE = False

class PoissonVarToExpOfGapsStatUnsplittable(RatioStatUnsplittable):                    
    def _createChildren(self):
        self._addChild(VarOfGapsStat(self._region, self._track) )
        self._addChild(MeanOfGapsStat(self._region, self._track) )
