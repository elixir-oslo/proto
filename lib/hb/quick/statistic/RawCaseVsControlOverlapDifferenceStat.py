from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticDictSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.BinSizeStat import BinSizeStat
from gold.statistic.RawOverlapStat import RawOverlapStatUnsplittable

class RawCaseVsControlOverlapDifferenceStat(MagicStatFactory):
    '''
    Provides 8 numbers of overlap between case-control valued segments of T1 and segments of T2.
    Uses the functionality of RawOverlapStat to compute tp,fp,tn,fn separately for case segments and control segments,
    using the same terminology as RawOverlapStat to define true/false positives/negatives (so that T1 is considered prediction, and T2 answer).
    This means that for instance a base pair covered by a case segment, but not by a T2 segment, will be counted as fpCase.
    '''
    pass

class RawCaseVsControlOverlapDifferenceStatSplittable(StatisticDictSumResSplittable):
    pass

class RawCaseVsControlOverlapDifferenceStatUnsplittable(Statistic):
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)            
    def _compute(self): #Numpy Version..
        tv1, tv2 = self._children[0].getResult(), self._children[1].getResult()

        t1s = tv1.startsAsNumpyArray()
        
        t1e = tv1.endsAsNumpyArray()
        m = tv1.valsAsNumpyArray()
        t2s = tv2.startsAsNumpyArray()
        t2e = tv2.endsAsNumpyArray()

        #used to add bps before first and after last segment
        binSize = self._binSizeStat.getResult()
        

        tnCase,fpCase,fnCase,tpCase = RawOverlapStatUnsplittable._computeRawOverlap(t1s[m==True],t1e[m==True],t2s,t2e,binSize)
        
        tnControl,fpControl,fnControl,tpControl = RawOverlapStatUnsplittable._computeRawOverlap(t1s[m==False],t1e[m==False],t2s,t2e,binSize)
        
        return dict(zip('tnCase,fpCase,fnCase,tpCase,tnControl,fpControl,fnControl,tpControl'.split(','), \
                        [tnCase,fpCase,fnCase,tpCase,tnControl,fpControl,fnControl,tpControl]))

        
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)            
    def _createChildren(self):
        #print self, self.__class__, self.__dict__
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False,val='tc')) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False)) )
        self._binSizeStat = self._addChild( BinSizeStat(self._region, self._track2))
