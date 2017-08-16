from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.SubMatrixStat import SubMatrixStat
import numpy as np
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq

class ColocalizationIn3dUsingMatrixGraphStat(MagicStatFactory):
    pass

class ColocalizationIn3dUsingMatrixGraphStatUnsplittable(Statistic):

    def _compute(self):
        subgraph_as_matrix = self._subgraph.getResult()
        # filter out nan-values:
        #subgraph_as_matrix_masked = np.ma.masked_invalid(subgraph_as_matrix.weights) #tar lang tid!
        subgraph_as_matrix_masked = np.ma.masked_array(subgraph_as_matrix.weights, np.isnan(subgraph_as_matrix.weights))
        res = subgraph_as_matrix_masked.mean(dtype='float64') #tar enda lenger tid!
        #to play well with hyperbrowser:
        if type(res) == np.ma.core.MaskedConstant:
            res = None
        return res

    def _createChildren(self):
        self._subgraph = self._addChild(SubMatrixStat(self._region, self._track, self._track2))
        requirement = self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(allowOverlaps=False)))
