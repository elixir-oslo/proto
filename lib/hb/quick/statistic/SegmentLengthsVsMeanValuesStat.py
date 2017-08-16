from collections import defaultdict

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.MarksListStat import MarksListStat
from gold.statistic.SegmentLengthsStat import SegmentLengthsStat
from gold.statistic.Statistic import Statistic, StatisticConcatDictResSplittable, OnlyGloballySplittable
from gold.util.CommonFunctions import mean
from quick.result.model.ResultTypes import LinePlotResultType


class SegmentLengthsVsMeanValuesStat(MagicStatFactory):
    pass

class SegmentLengthsVsMeanValuesStatSplittable(StatisticConcatDictResSplittable, OnlyGloballySplittable):
    IS_MEMOIZABLE = False
    
    def _combineResults(self):
        StatisticConcatDictResSplittable._combineResults(self)
        self._result = LinePlotResultType(self._result)
        self._result.setXLabel('Segment lengths')
        self._result.setYLabel('Mean values')
            
class SegmentLengthsVsMeanValuesStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    
    def _init(self, withOverlaps='no', **kwArgs):
        assert( withOverlaps in ['no','yes'] )
        self._withOverlaps = withOverlaps
    
    def _compute(self):
        lenghts = self._segmentLengthsStat.getResult()['Result']
        vals = self._marksListStat.getResult()

        assert len(lenghts) == len(vals)
        allValsDict = defaultdict(list)
        for i in xrange(len(lenghts)):
            allValsDict[lenghts[i]].append(vals[i])
        
        return LinePlotResultType([(length, mean(valList)) for length, valList in allValsDict.iteritems()])
    
    def _createChildren(self):
        self._segmentLengthsStat = SegmentLengthsStat(self._region, self._track, withOverlaps=self._withOverlaps)
        self._marksListStat = MarksListStat(self._region, self._track, withOverlaps=self._withOverlaps, enforcePoints=False)
        
        self._addChild(self._segmentLengthsStat)
        self._addChild(self._marksListStat)
