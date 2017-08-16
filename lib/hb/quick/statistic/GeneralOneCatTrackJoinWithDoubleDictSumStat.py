from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import StatisticDynamicDoubleDictSumResSplittable
from quick.statistic.GeneralOneCatTrackStat import GeneralOneCatTrackStatUnsplittable

class GeneralOneCatTrackJoinWithDoubleDictSumStat(MagicStatFactory):
    pass

class GeneralOneCatTrackJoinWithDoubleDictSumStatSplittable(StatisticDynamicDoubleDictSumResSplittable):
    pass
            
class GeneralOneCatTrackJoinWithDoubleDictSumStatUnsplittable(GeneralOneCatTrackStatUnsplittable):
    STORE_CHILDREN = False
