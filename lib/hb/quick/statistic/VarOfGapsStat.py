from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
#from gold.statistic.RawDataStat import RawDataStat
#from quick.statistic.BinSizeStat import BinSizeStat
#from quick.statistic.SegmentDistancesStat import SegmentDistancesStat
from quick.statistic.PointGapsStat import PointGapsStat
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq

class VarOfGapsStat(MagicStatFactory):
    pass

#class VarOfGapsStatSplittable(StatisticSumResSplittable, OnlyGloballySplittable):
#    IS_MEMOIZABLE = False

class VarOfGapsStatUnsplittable(Statistic):
    #IS_MEMOIZABLE = False

    #def _init(self, bpWindow='100', **kwArgs):
    #    self._bpWindow = int(bpWindow)
    
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)    
    def _compute(self):
        gaps = self._children[0].getResult()['Result']
        return gaps.var()
        #if len(points)==0:
        #    return 1.0
        #else:
                    
    def _createChildren(self):
        self._addChild(PointGapsStat(self._region, self._track) )
        self._addChild(FormatSpecStat(self._region, self._track, TrackFormatReq(dense=False, interval=False) ) )
        #self._addChild( BinSizeStat(self._region, self._track) )
