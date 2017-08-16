import ast

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import StatisticConcatNumpyArrayResSplittable, Statistic, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class MarksListStat(MagicStatFactory):
    pass

class MarksListStatSplittable(StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable):
    IS_MEMOIZABLE = False
           
class MarksListStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    def __init__(self, region, track, track2=None, withOverlaps='no', markType='number', enforcePoints=True, **kwArgs):
        assert( withOverlaps in ['no','yes'] )
        self._withOverlaps = withOverlaps
        self._markType = markType
        if isinstance(enforcePoints, basestring):
            enforcePoints = ast.literal_eval(enforcePoints)
        self._enforcePoints = enforcePoints
        Statistic.__init__(self, region, track, track2, withOverlaps=withOverlaps, markType=markType, enforcePoints=enforcePoints, **kwArgs)
    
    def _compute(self):
        marks = self._children[0].getResult().valsAsNumpyArray()
        assert marks is not None
        #print marks
        #res = [float(x) for x in self._children[0].getResult().valsAsNumpyArray() ]
        return marks
    
    def _createChildren(self):
        interval = False if self._enforcePoints else None
        self._addChild( RawDataStat(self._region, self._track, \
                                    TrackFormatReq(interval=interval, val=self._markType, allowOverlaps=(self._withOverlaps=='yes'))) )
