from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.GraphStat import GraphStat

class MeasureGraphDensity3dStat(MagicStatFactory):
    pass

#class MeasureGraphDensity3dStatSplittable(StatisticSplittable):
#    def _combineResults(self):
#        res = {"WeightedEdges" : 0, 'totEdges':0, 'Ratio':0}
#        for child in self._childResults:
#            for key, value in child.items():
#                res[key] += value
#        res['Ratio'] = res['WeightedEdges']/res['totEdges']*1.0        
#        return res
    
    
class MeasureGraphDensity3dStatUnsplittable(Statistic):    
    def _compute(self):
        graph = self._graphStat.getResult()
        numNodes = sum(1 for node in graph.getNodeIter())
        numEdges = sum(1 for edge in graph.getEdgeIter())
        numWeightedEdges = sum(1 for edge in graph.getEdgeIter() if edge.weight>0)
        
        res = {"WeightedEdges": numWeightedEdges, 'totEdges': numEdges, 'totNodes': numNodes, 'Density': 1.0*numWeightedEdges/(numNodes*(numNodes-1))}
        return res
    
    def _createChildren(self):
        self._graphStat = self._addChild(GraphStat(self._region, self._track) )
        
