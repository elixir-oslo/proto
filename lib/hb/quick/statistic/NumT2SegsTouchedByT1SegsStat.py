from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.BpCoveragePerT2SegStat import BpCoveragePerT2SegStat

class NumT2SegsTouchedByT1SegsStat(MagicStatFactory):
    pass
            
class NumT2SegsTouchedByT1SegsStatUnsplittable(Statistic):    
    IS_MEMOIZABLE = False

    def _compute(self):
        bpCovPerSeg = self._children[0].getResult()
        return (bpCovPerSeg >0).sum()
    
    def _createChildren(self):
        self._addChild( BpCoveragePerT2SegStat(self._region, self._track, self._track2))
