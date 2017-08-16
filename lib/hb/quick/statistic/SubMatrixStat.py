from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.GraphMatrixStat import GraphMatrixStat
from gold.graph.GraphMatrix import GraphMatrix
from quick.statistic.PositionToGraphNodeIdStat import PositionToGraphNodeIdStat

class SubMatrixStat(MagicStatFactory):
    pass

class SubMatrixStatUnsplittable(Statistic):
    def _compute(self):
        #import pdb; pdb.set_trace()
        graphMatrix = self.matrix.getResult()
        ids = self.ids.getResult()
        #translate indices from IDs (such as 'chr1*100') to indices in array (such as '29')
        translated_indices = graphMatrix._translate(ids)
        subMatrix = graphMatrix.weights.take(translated_indices, axis=0)
        if subMatrix != []:
            subMatrix = subMatrix.take(translated_indices, axis=1)
        #wrap the new subMatrix in a GraphMatrix
        #TODO: is this a valid way to generate id -> position mapping?
        #assumes that the order in 'ids' is correct
        id2position = {id_name: row_num for row_num, id_name in enumerate(ids)}
        return GraphMatrix(weights=subMatrix, ids=id2position)

    def _createChildren(self):
        self.matrix = self._addChild(GraphMatrixStat(self._region, self._track))
        self.ids = self._addChild(PositionToGraphNodeIdStat(self._region, self._track, self._track2))
