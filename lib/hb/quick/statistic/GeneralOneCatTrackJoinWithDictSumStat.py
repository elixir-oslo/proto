from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import StatisticDynamicDictSumResSplittable
from quick.statistic.GeneralOneCatTrackStat import GeneralOneCatTrackStatUnsplittable

class GeneralOneCatTrackJoinWithDictSumStat(MagicStatFactory):
    pass

class GeneralOneCatTrackJoinWithDictSumStatSplittable(StatisticDynamicDictSumResSplittable):
    pass

class GeneralOneCatTrackJoinWithDictSumStatUnsplittable(GeneralOneCatTrackStatUnsplittable):
    STORE_CHILDREN = False
