from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.FreqByCatStat import FreqByCatStatUnsplittable
from gold.statistic.Statistic import StatisticDynamicDictSumOnlyValuesResSplittable, OnlyGloballySplittable

class FreqPerCatDistributionStat(MagicStatFactory):
    pass

class FreqPerCatDistributionStatSplittable(StatisticDynamicDictSumOnlyValuesResSplittable, OnlyGloballySplittable):
    pass

class FreqPerCatDistributionStatUnsplittable(FreqByCatStatUnsplittable):
    pass
