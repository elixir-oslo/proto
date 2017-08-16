from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from quick.statistic.BinSizeStat import BinSizeStat
from gold.statistic.CountPointStat import CountPointStat
from quick.statistic.GenericRelativeToGlobalStat import GenericRelativeToGlobalStatUnsplittable

#from quick.statistic.SegmentDistancesStat import SegmentDistancesStat
from gold.track.TrackFormat import TrackFormatReq

class RawRipleysKChrStat(MagicStatFactory):
    pass

class RawRipleysKChrStatSplittable(StatisticSumResSplittable, OnlyGloballySplittable):
    IS_MEMOIZABLE = False
    def _combineResults(self):
        res = StatisticSumResSplittable._combineResults(self)
        if res is None:
            import numpy
            return numpy.nan
        else:
            return res

class RawRipleysKChrStatUnsplittable(Statistic):
    #IS_MEMOIZABLE = False

    def _init(self, bpWindow='100', minimal=False, **kwArgs):
        self._bpWindow = int(bpWindow)
        self._globalSource = GenericRelativeToGlobalStatUnsplittable.getGlobalSource('userbins', self.getGenome(), minimal) 
    
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #
    #@repackageException(Exception, ShouldNotOccurError)    
    def _compute(self):
        tv = self._children[0].getResult() 
        # print tv.genomeAnchor.chr
        points = self._children[0].getResult().startsAsNumpyArray()
        binSize = self._children[1].getResult()
        globalPointCount = self._children[2].getResult()
        
        rCode = '''
k<-function(x,r,a,b,n) {
 if (min(x)<a || max(x)>b) stop("Points must be in interval [a,b]!")
 dmat<-as.matrix(dist(x)) ## calculate distanced between all pairs of points
 diag(dmat)<-Inf ## distance of point to itself (zero) should not be counted, so set this to infinite (i.e., never less than r)
 wmat<-outer(x,x,function(x,y) (pmin(b,pmax(x+abs(x-y),a))-pmin(b,pmax(x-abs(x-y),a)))/(2*abs(x-y))) ## calculate edge correction weights
 iwmat<-1/wmat ## inverse of edge correction weights
 diag(iwmat)<-0 ##  distance of point to itself (zero) should not be counted, so set this to zero (i.e., drops out of sum
 k<-sum(iwmat*(dmat<r))/n^2 ## final K-function: (sum of inverse weights iw_ij where d_ij<r)/n^2
 k/(2*r)
}
'''
        if len(points)==0:
            #import numpy
            #return numpy.nan
            return None
        else:
            from proto.RSetup import r, robjects
            return r(rCode)(robjects.FloatVector(points), self._bpWindow, 0, binSize, globalPointCount )
                    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False) ) )
        self._addChild( BinSizeStat(self._region, self._track) )
        self._addChild( CountPointStat(self._globalSource, self._track) )
        #self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=True, \
        #                                                                      allowOverlaps = (self._withOverlaps == 'yes') ) ) )
