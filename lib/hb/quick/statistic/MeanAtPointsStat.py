from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.CountStat import CountStat
from gold.statistic.SumAtPointsStat import SumAtPointsStat

class MeanAtPointsStat(MagicStatFactory):
    pass

class MeanAtPointsStatUnsplittable(Statistic):
    resultLabel = 'Mean at points'
    
    def _compute(self):               
        sumInside = self._children[0].getResult()
        cntInside = self._children[1].getResult()
        
        return 1.0*sumInside/cntInside

    def _createChildren(self):
        self._addChild(SumAtPointsStat(self._region, self._track, self._track2))
        self._addChild(CountStat(self._region, self._track))
        
