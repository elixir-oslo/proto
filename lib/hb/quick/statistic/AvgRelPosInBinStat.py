from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
#from gold.statistic.RawDataStat import RawDataStat
#from quick.statistic.BinSizeStat import BinSizeStat
from quick.statistic.RelPositionsInBinStat import RelPositionsInBinStat

class AvgRelPosInBinStat(MagicStatFactory):
    pass

#class MostCommonCategoryStatSplittable(StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable):
#    IS_MEMOIZABLE = False

class AvgRelPosInBinStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    def _compute(self):
        tvArray = self._children[0].getResult()
        
        #rawRelPos = tvArray.mean()
        #if self._region.strand == False:
        #    return 1.0-rawRelPos
        #else:
        #    return rawRelPos
        return tvArray.mean(dtype='float64')
        
    #def _compute(self):
    #    bpSize = self._children[1].getResult()
    #    tvArray = self._children[0].getResult().startsAsNumpyArray()/float(bpSize)
    #    
    #    rawRelPos = tvArray.mean(dtype='float64')
    #    if self._region.strand == False:
    #        return 1.0-rawRelPos
    #    else:
    #        return rawRelPos
        
            
    #def _createChildren(self):
    #    self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(interval=False, dense=False) ) )
    #    self._addChild(BinSizeStat(self._region, self._track))
    def _createChildren(self):
        self._addChild(RelPositionsInBinStat(self._region, self._track))
