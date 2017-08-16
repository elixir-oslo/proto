from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.PointCountPerSegStat import PointCountPerSegStat

class NumSegsContainingPointsStat(MagicStatFactory):
    pass
            
class NumSegsContainingPointsStatUnsplittable(Statistic):    
    IS_MEMOIZABLE = False

    def _compute(self):
        pointCountPerSeg = self._children[0].getResult()
        return (pointCountPerSeg>0).sum()
    
    def _createChildren(self):
        self._addChild( PointCountPerSegStat(self._region, self._track, self._track2))
