from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class MostCommonCategoryInBinStat(MagicStatFactory):
    pass

#class MostCommonCategoryStatSplittable(StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable):
#    IS_MEMOIZABLE = False

class MostCommonCategoryInBinStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    
    def _compute(self):
        markDict = {}
        tv = self._children[0].getResult()
        
        for te in tv:
            if markDict.has_key(te.val()):
                markDict[te.val()] +=1
            else:
                markDict[te.val()] = 1
                        
        max = 0
        resultStr =''
        for mark in markDict.keys():
            if markDict[mark] > max:
                resultStr = mark
                max = markDict[mark]
            elif markDict[mark] == max:
                resultStr+=', '+mark
               
        return resultStr
            
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(interval=False, val='category') ) )
        
