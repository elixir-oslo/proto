from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from quick.statistic.GenericRelativeToGlobalStat import GenericRelativeToGlobalStatUnsplittable
from quick.statistic.SizePerCatOfCategoricBinsStat import SizePerCatOfCategoricBinsStat
from gold.statistic.CountStat import CountStat
import numpy

class CatCoverageNormalizedCountStat(MagicStatFactory):
    '''
    For each bin, where bin is required to have an associated category value, it counts bps covered by track 1 and divides this by the total size of all bins having that same category.
    This means that for each category of the bin track, the sum across all bins having that category can be at most 1.
    This further means that the maximum value that can be achieved is equal to the number of different categories the different bins are having,
    where coverage is the average of across-bin coverage values per category.
    '''
    pass

class CatCoverageNormalizedCountStatSplittable(StatisticSumResSplittable):
    pass
            
class CatCoverageNormalizedCountStatUnsplittable(Statistic):
    def _init(self, minimal=False, **kwArgs):
        self._globalSource = GenericRelativeToGlobalStatUnsplittable.getGlobalSource('userbins', self.getGenome(), minimal) 
        
    
    def _compute(self):
        if self._kwArgs.get('minimal')==True:
            return numpy.nan
        category = self._region.val
        
        count = self._bpCount.getResult()
        catBinTotalSize = self._globalCatBinSizes.getResult()[category]
        if catBinTotalSize>0:
            return float(count) / catBinTotalSize
        else:
            return numpy.nan
        
    def _createChildren(self):
        self._bpCount = self._addChild( CountStat(self._region, self._track, **self._kwArgs))

        
        self._globalCatBinSizes = self._addChild( SizePerCatOfCategoricBinsStat(self._globalSource, self._track, **self._kwArgs))

        #self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=self._configuredToAllowOverlaps(strict=False))) )
        pass
