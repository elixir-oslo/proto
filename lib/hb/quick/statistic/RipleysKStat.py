from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.BinSizeStat import BinSizeStat
from quick.statistic.RawRipleysKStat import RawRipleysKStat

#from quick.statistic.SegmentDistancesStat import SegmentDistancesStat

class RipleysKStat(MagicStatFactory):
    pass

class RipleysKStatUnsplittable(Statistic):
    #IS_MEMOIZABLE = False
    
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #
    #@repackageException(Exception, ShouldNotOccurError)    
    def _compute(self):
        rawK = self._children[0].getResult()
        numBps = self._children[1].getResult()
        import numpy
        if numpy.isnan(rawK):
            return numpy.nan
        else:
            return numBps * rawK
    
    def _createChildren(self):
        self._addChild( RawRipleysKStat(self._region, self._track, **self._kwArgs) )
        self._addChild( BinSizeStat(self._region, self._track) )
        #self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=True, \
        #                                                                      allowOverlaps = (self._withOverlaps == 'yes') ) ) )
