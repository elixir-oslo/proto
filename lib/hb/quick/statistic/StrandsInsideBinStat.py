from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import numpy

class StrandsInsideBinStat(MagicStatFactory):
    pass

#class MostCommonCategoryStatSplittable(StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable):
#    IS_MEMOIZABLE = False

class StrandsInsideBinStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)
    def _compute(self):
        tv1 = self._children[0].getResult()
        strands = tv1.strandsAsNumpyArray()
        if strands is None:
            return None
        strandsUnique = numpy.unique(strands)
        return ''.join(['+' if el == True else ('-' if el == False else '.') for el in strandsUnique])
        #return '+' if True in strandsUnique else '' + '-' if False in strandsUnique else ''
        
            
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=True) ) )
