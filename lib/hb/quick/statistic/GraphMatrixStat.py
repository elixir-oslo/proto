from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.GraphStat import GraphStat
from gold.graph.GraphMatrix import GraphMatrix
import numpy as np

class GraphMatrixStat(MagicStatFactory):
    pass

class GraphMatrixStatUnsplittable(Statistic):
    def _compute(self):
        #version 1: using the iterator based implementation for generating matrices
        #instance of GraphMatrix class:
        res = self._graphStat.getResult().getEdgeWeightMatrixRepresentation(completeMatrix=False, rowsAsFromNodes=True, missingEdgeWeight=np.nan)
        assert (res['Rows'] == res['Cols']).all() #rows and column IDs should be the same
        #TODO: the way ids are created is based on assumptions that may not hold:
        graphMatrix = GraphMatrix(weights=res['Matrix'], ids={i: n for n, i in enumerate(res['Rows'])})
        return graphMatrix

        #version 2: using optimized method that assumes complete graphs:
        #res = self._graphStat.getResult().getMatrixAndIdsFromCompleteGraph()
        #graphMatrix = GraphMatrix(weights=res["matrix"], ids=res["ids"])
        #return graphMatrix

    def _createChildren(self):
        self._graphStat = self._addChild(GraphStat(self._region, self._track))
