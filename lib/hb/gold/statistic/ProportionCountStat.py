from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import RatioStatUnsplittable
from gold.statistic.CountSegmentStat import CountSegmentStat
from quick.statistic.BinSizeStat import BinSizeStat

class ProportionCountStat(MagicStatFactory):
    '''
    Computes the proportion of base pairs in a bin (or global region) covered by a track.
    '''
    pass

class ProportionCountStatUnsplittable(RatioStatUnsplittable):    
    def _createChildren(self):
        self._addChild( CountSegmentStat(self._region, self._track, **self._kwArgs) )
        self._addChild( BinSizeStat(self._region, self._track) )
