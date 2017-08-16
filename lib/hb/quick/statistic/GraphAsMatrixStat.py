import ast

import numpy as np

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.statistic.GraphStat import GraphStat
from gold.track.TrackFormat import TrackFormatReq
#from proto.RSetup import robjects, r

class GraphAsMatrixStat(MagicStatFactory):
    pass

#class GraphAsMatrixStatSplittable(StatisticNumpyMatrixSplittable):
#    pass
            
class GraphAsMatrixStatUnsplittable(Statistic):
    def _init(self, normalizationMethod='none', minimal=False, complete='False', rowsAsFromNodes='True', **kwArgs):
        assert normalizationMethod in ['none', 'log', 'log+1', 'p_inverse', 'p_to_normal_onesided', 'p_to_normal_twosided']
        self._normalizationMethod = normalizationMethod
        self._minimal = minimal
        assert complete in ['False', 'True']
        self._complete = ast.literal_eval(complete)
        assert rowsAsFromNodes in ['False', 'True']
        self._rowsAsFromNodes = ast.literal_eval(rowsAsFromNodes)

    def _numpyRemoveInfs(self, a):
        a = np.array(a)
        a[np.logical_and(np.isinf(a), a>0)] = np.finfo(a.dtype).max
        a[np.logical_and(np.isinf(a), a<0)] = np.finfo(a.dtype).min
        return a
        
    def _compute(self):
        from proto.RSetup import robjects, r
        #if self._minimal:
        #    return {'Result': OrderedDict([('Matrix', np.array([], dtype='float64')), \
        #                                   ('Rows', np.array([], dtype='S1')), \
        #                                   ('Cols', np.array([], dtype='S1'))])}
        #
        #rawData = self._children[0].getResult()
        #edges = rawData.edgesAsNumpyArray()
        #weights = rawData.weightsAsNumpyArray()
        #ids = rawData.idsAsNumpyArray()
        #
        #if len(edges) > 0:
        #    assert all((x==edges[0]).all() for x in edges), 'Edge arrays are not equal for all elements'
        #
        #x,y = weights.shape
        #assert x == y, 'Weight matrix is not square, %s != %s' % (x,y)
        
        graph = self._graphStat.getResult()
        res = graph.getEdgeWeightMatrixRepresentation(completeMatrix=self._complete, \
                                                      rowsAsFromNodes=self._rowsAsFromNodes, \
                                                      missingEdgeWeight=np.nan)
        
        if self._normalizationMethod != 'none':
            if self._normalizationMethod == 'log':
                res['Matrix'] = np.log(res['Matrix'])
            if self._normalizationMethod == 'log+1':
                res['Matrix'] = np.log(res['Matrix']+1)
            elif self._normalizationMethod == 'p_inverse':
                res['Matrix'] = 1 - res['Matrix']
            else:
                origShape = res['Matrix'].shape
                if self._normalizationMethod == 'p_to_normal_onesided':
                    intermed = 1-res['Matrix']
                else: #p_to_normal_twosided
                    intermed = 1-res['Matrix']/2
                vec = robjects.FloatVector(intermed.flatten())
                # To remove -Inf anf Inf values
                vec = r('f <- function(vec){vec[vec==0] = .Machine$double.eps; vec[vec==1] = 1-.Machine$double.eps;vec}')(vec)
                res['Matrix'] = np.array(list(r.qnorm(vec)))
                res['Matrix'].shape = origShape
                
        return {'Result': res}
                
        #return {'Result': OrderedDict([('Matrix', weights), \
        #                               ('Rows', edges[0] if len(edges) > 0 else np.array([], dtype='S1')), \
        #                               ('Cols', ids)])}
    
    def _createChildren(self):
        self._graphStat = self._addChild( GraphStat(self._region, self._track, isDirected='True') )
        self._addChild( FormatSpecStat(self._region, self._track, TrackFormatReq(weights='number')) )
