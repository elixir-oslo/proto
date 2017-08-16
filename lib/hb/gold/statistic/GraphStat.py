from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.ProtoGraphStat import ProtoGraphStat

class GraphStat(MagicStatFactory):
    pass
        
class GraphStatUnsplittable(Statistic):        
    def _compute(self):
        return self._children[0].getResult().getClosedGraphVersion()
        
                
    def _createChildren(self):
        self._addChild( ProtoGraphStat(self._region, self._track, **self._kwArgs))
