from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import StatisticAvgResSplittable
from gold.statistic.ProportionCountStat import ProportionCountStatUnsplittable

class ProportionCountPerBinAvgStat(MagicStatFactory):
    """For an individual bin, it gives the proportion covered by segments.
    Globally, it takes the average of the proportion values achieved per bin, weighting each bin equally regardless of its length.
    """
    pass

class ProportionCountPerBinAvgStatSplittable(StatisticAvgResSplittable):    
    pass

class ProportionCountPerBinAvgStatUnsplittable(ProportionCountStatUnsplittable):    
    pass
