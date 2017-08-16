from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from quick.statistic.RawCaseVsControlOverlapDifferenceStat import RawCaseVsControlOverlapDifferenceStat

class CaseVsControlOverlapDifferenceStat(MagicStatFactory):
    pass

class CaseVsControlOverlapDifferenceStatSplittable(StatisticSumResSplittable):
    pass

class CaseVsControlOverlapDifferenceStatUnsplittable(Statistic):

    def _compute(self):
        rawCaseControlOverlap = self._children[0].getResult()        
        caseOverlap = rawCaseControlOverlap['tpCase']
        controlOverlap = rawCaseControlOverlap['tpControl']

        return caseOverlap - controlOverlap
        
    def _createChildren(self):
        self._addChild(RawCaseVsControlOverlapDifferenceStat(self._region, self._track, self._track2 ))
