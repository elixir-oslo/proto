from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.GraphStat import GraphStat
from quick.statistic.GenericRelativeToGlobalStat import GenericRelativeToGlobalStatUnsplittable

class GlobalGraphStat(MagicStatFactory):
    pass
        
class GlobalGraphStatUnsplittable(Statistic):
    def _init(self, globalSource=None, minimal=False, **kwArgs):
        assert globalSource is not None
        self._globalSource = GenericRelativeToGlobalStatUnsplittable.getGlobalSource(globalSource, self._region.genome, minimal)        
    
    def _compute(self):
        return self._children[0].getResult()
        
                
    def _createChildren(self):
        self._addChild( GraphStat(self._globalSource, self._track))
