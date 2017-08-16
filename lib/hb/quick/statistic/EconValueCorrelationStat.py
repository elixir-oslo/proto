from gold.application.LogSetup import logMessage
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSplittable
#from proto.RSetup import r
from quick.statistic.GenericPerTrackStat import GenericPerTrackStat
from itertools import imap

class EconValueCorrelationStat(MagicStatFactory):
    pass

class EconValueCorrelationStatSplittable(StatisticSplittable):
    
    #def _pearsonr(self, x, y):
    #    logMessage('x:   '+ repr(x))
    #    logMessage('y:   '+ repr(y))
    #    # Assume len(x) == len(y)
    #    print 'x: ', x
    #    print 'y:', y
    #    n = len(x)
    #    sum_x = float(sum(x))
    #    sum_y = float(sum(y))
    #    sum_x_sq = sum([pow(v,2) for v in x])
    #    sum_y_sq = sum([pow(v,2) for v in y])
    #    psum = 0
    #    for i in x:
    #        for v in y:
    #            psum+=i*v
    #    #psum = sum(imap(lambda x, y: x * y, x, y))
    #    num = psum - (sum_x * sum_y/n)
    #    den = pow((sum_x_sq - pow(sum_x, 2) / n) * (sum_y_sq - pow(sum_y, 2) / n), 0.5)
    #    if den == 0:
    #        return 0
    #    return num / den
    
    def _pearsonr(self, x, y):
        # Assume len(x) == len(y)
        n = len(x)
        sum_x = float(sum(x))
        sum_y = float(sum(y))
        sum_x_sq = sum(map(lambda x: pow(x, 2), x))
        sum_y_sq = sum(map(lambda x: pow(x, 2), y))
        psum = sum(imap(lambda x, y: x * y, x, y))
        num = psum - (sum_x * sum_y/n)
        den = pow((sum_x_sq - pow(sum_x, 2) / n) * (sum_y_sq - pow(sum_y, 2) / n), 0.5)
        if den == 0: return 0
        return num / den
    
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)
    def _combineResults(self):
        if len(self._childResults)>0:
            logMessage(repr(self._childResults))
            x,y = zip(*self._childResults)
            return self._pearsonr(x,y)
        else:
            return 2.5
            
class EconValueCorrelationStatUnsplittable(Statistic):
    def _compute(self):
        return self._children[0].getResult()
    #def _compute(self):
    #    tv1 = self._children[0].getResult()
    #    tv2 = self._children[1].getResult()
    #    start1 = tv1.startsAsNumpyArray()
    #    start2 = tv2.startsAsNumpyArray()
    #    val1 = tv1.valsAsNumpyArray()
    #    val2 = list(tv2.valsAsNumpyArray())
    #    indx1, indx2 = 0, 0
    #    res1, res2 = [],[]
    #    
    #
    #    #
    #    count = 0
    #    while indx2<len(start2) and indx1<len(start1):
    #        count+=1
    #        if start1[indx1]<start2[indx2]:
    #            indx1+=1
    #        elif start1[indx1]>start2[indx2]:
    #            indx2+=1
    #        else:
    #            res1.append(val1[indx1])
    #            res2.append(val2[indx2])
    #            
    #            indx1+=1
    #            indx2+=1
    #
    #    if len(res1)<2 or len(res2)<2:
    #        return -2.0
    #    else:
    #        
    #        return self._pearsonr(res1, res2)
    
    
    def _createChildren(self):
        self._addChild( GenericPerTrackStat(self._region, self._track, self._track2, rawStatistic='MeanOverCoveredBpsStat') )#, TrackFormatReq(val='number')
        #self._addChild( GenericPerTrackStat(self._region, self._track2, rawStatistic='MeanStat')  )#TrackFormatReq(val='number'))
