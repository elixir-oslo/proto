from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.GraphStat import GraphStat
from quick.statistic.PositionToGraphNodeIdStat import PositionToGraphNodeIdStat
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq
import numpy as np
#from quick.util.CommonFunctions import isNan

#class ColocalizationIn3dAssumingCompleteGraphStatSplittable(StatisticSumResSplittable):
#    pass

class ColocalizationIn3dAssumingCompleteGraphStat(MagicStatFactory):
    pass    

class ColocalizationIn3dAssumingCompleteGraphStatUnsplittable(Statistic):
    def _compute(self):
        graph = self._graphStat.getResult()
        subgraph_ids = self._position2NodeId.getResult()
        subgraph = graph.getNewSubGraphFromNodeIdSet(subgraph_ids)
        subgraph_as_matrix = subgraph.getMatrixFromCompleteGraph()
        if subgraph_as_matrix is None:
            return None

#        try:
        subgraph_as_matrix_without_nan = np.ma.masked_array(subgraph_as_matrix, np.isnan(subgraph_as_matrix))
#        except:
#            numNodes = sum(1 for x in graph.getNodeIter())
#            print "#nodes", numNodes, numNodes**2
#            print "#edges", sum(1 for x in graph.getEdgeIter())
#            print [len(x) for x in subgraph_as_matrix]
#            raise
#            print "Subgraph as matrix:", subgraph_as_matrix
        res = np.ma.mean(subgraph_as_matrix_without_nan)
        if type(res) == np.ma.core.MaskedConstant:
            res = None
        return res
        
    def _createChildren(self):
        self._graphStat = self._addChild(GraphStat(self._region, self._track))
        self._position2NodeId = self._addChild(PositionToGraphNodeIdStat(self._region, self._track, self._track2))
        dummyStat = self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(allowOverlaps=False)))
