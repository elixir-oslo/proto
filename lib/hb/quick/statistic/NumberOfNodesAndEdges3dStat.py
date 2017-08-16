from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.GraphStat import GraphStat

class NumberOfNodesAndEdges3dStat(MagicStatFactory):
    pass
            
class NumberOfNodesAndEdges3dStatUnsplittable(Statistic):    
    def _compute(self):
        graph = self._graphStat.getResult()
        #assert not graph.isDirected()
        numNeighbors = []
        i = 0

        numNodes = sum(1 for node in graph.getNodeIter())
        numEdges = sum(1 for edge in graph.getEdgeIter())
        #for node in graph.getNodeIter():
            #numNeighbors.append( sum(1 for neighbor in node.getNeighborIter() if graph.isDirected() or node.id() <= neighbor.node.id()) )#len(list(node.getNeighborIter()))
        #    i = i+1
        #res = {"totNeig" : sum(numNeighbors), "totNodes":i}
        res = {"totNodes" : numNodes, 'totEdges':numEdges}
        return res
    
    def _createChildren(self):
        self._graphStat = self._addChild(GraphStat(self._region, self._track) )
        
