from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.GraphStat import GraphStat

class EdgeDistributionStat(MagicStatFactory):
    pass

class EdgeDistributionStatUnsplittable(Statistic): 
    IS_MEMOIZABLE = False

    def _compute(self):
        fullGraph = self._graphStat.getResult()
        return [e.weight for e in fullGraph.getEdgeIter()]
            
    def _createChildren(self):
        #self._track: 3D data
        self._graphStat = self._addChild(GraphStat(self._region, self._track) )
