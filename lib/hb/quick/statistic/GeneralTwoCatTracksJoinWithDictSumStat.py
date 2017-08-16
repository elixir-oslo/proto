from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import StatisticDynamicDictSumResSplittable
from quick.statistic.GeneralTwoCatTracksStat import GeneralTwoCatTracksStatUnsplittable

class GeneralTwoCatTracksJoinWithDictSumStat(MagicStatFactory):
    pass

class GeneralTwoCatTracksJoinWithDictSumStatSplittable(StatisticDynamicDictSumResSplittable):
    pass

class GeneralTwoCatTracksJoinWithDictSumStatUnsplittable(GeneralTwoCatTracksStatUnsplittable):
    STORE_CHILDREN = False
