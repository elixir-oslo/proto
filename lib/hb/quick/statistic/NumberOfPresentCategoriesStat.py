from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, OnlyGloballySplittable, StatisticConcatResSplittable
#from gold.statistic.RawDataStat import RawDataStat
#from gold.track.TrackFormat import TrackFormatReq
#from gold.util.CustomExceptions import NotSupportedError
#from quick.statistic.CategoryPointCountNoOverlapsStat import CategoryPointCountNoOverlapsStat
from gold.statistic.BpCoverageByCatStat import BpCoverageByCatStat

class NumberOfPresentCategoriesStat(MagicStatFactory):
    pass

class NumberOfPresentCategoriesStatSplittable(StatisticConcatResSplittable, OnlyGloballySplittable):
    pass
#    IS_MEMOIZABLE = False

class NumberOfPresentCategoriesStatUnsplittable(Statistic):
    #IS_MEMOIZABLE = False

    def _compute(self):
        countsPerCategory = self._children[0].getResult()
        numCategories = len(countsPerCategory)
        return [numCategories]
            
    def _createChildren(self):
        self._addChild( BpCoverageByCatStat(self._region, self._track ) )
        
