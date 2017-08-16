from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class MostCommonCategoryStat(MagicStatFactory):
    pass

#class MostCommonCategoryStatSplittable(StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable):
#    IS_MEMOIZABLE = False

class MostCommonCategoryStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    
    def _compute(self):
        
        tv1 = self._children[0].getResult()
        tv2 = self._children[1].getResult()
        finished = False
        #print "length: ",len(list(tv1)), len(list(tv2))
        it = iter(tv1)
        try:
            
            te1 = it.next() # in Python 2.x
        except StopIteration:
            #print 'No data for Track 1'
            return 'No data for Track 1'
        resultStr = ''
        for te2 in tv2:
            markDict = {}
            if te1.start() > te2.end():
                continue
            
            if te2.end()>te1.start() >= te2.start():
                while te1.start() < te2.end():
                    try:
                        if markDict.has_key(te1.val()):
                            markDict[te1.val()] +=1
                        else:
                            markDict[te1.val()] = 1
                        te1 = it.next() # in Python 2.x
                    except StopIteration:
                        finished = True
                        break
                
                
                max = 0
                tempresultStr =''
                for mark in markDict.keys():
                    if markDict[mark] > max:
                        tempresultStr = mark
                        max = markDict[mark]
                    elif markDict[mark] == max:
                        tempresultStr+=', '+mark
                
                resultStr+=' ('+ tempresultStr+') '
                if finished:
                    return resultStr
                
            else:
                while te1.start() < te2.start() :
                    try:
                        te1 = it.next() # in Python 2.x
                    except StopIteration:
                        return resultStr   
        return resultStr
            
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(interval=False, val='category') ) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(interval=True, val='category', allowOverlaps=True) ) )

