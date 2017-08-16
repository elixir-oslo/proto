from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.GraphStat import GraphStat

class NumNeighborsDistribution3dStat(MagicStatFactory):
    pass
            
class NumNeighborsDistribution3dStatUnsplittable(Statistic):    
    def _compute(self):
        graph = self._graphStat.getResult()
        #assert not graph.isDirected()
        numNeighbors = []
        for node in graph.getNodeIter():
            numNeighbors.append( sum(1 for neighbor in node.getNeighborIter()) )#len(list(node.getNeighborIter()))
        return numNeighbors
    
    def _createChildren(self):
        self._graphStat = self._addChild(GraphStat(self._region, self._track) )
        
