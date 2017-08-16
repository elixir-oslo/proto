from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import StatisticAvgResSplittable,\
    RatioStatUnsplittable
from quick.statistic.BinSizeStat import BinSizeStat

class TpProportionOverlapPerBinAvgStat(MagicStatFactory):
    """For an individual bin, it gives the proportion of the bin covered by segments of both tracks.
    Globally, it takes the average of the above proportion values achieved per bin, weighting each bin equally regardless of its length.
    """
    pass

class TpProportionOverlapPerBinAvgStatSplittable(StatisticAvgResSplittable):    
    pass

class TpProportionOverlapPerBinAvgStatUnsplittable(RatioStatUnsplittable):    
    def _createChildren(self):
        from quick.statistic.StatFacades import TpRawOverlapStat
        self._addChild( TpRawOverlapStat(self._region, self._track, self._track2) )
        self._addChild( BinSizeStat(self._region, self._track) )
