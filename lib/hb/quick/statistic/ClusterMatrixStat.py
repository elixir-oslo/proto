import ast
from collections import OrderedDict
from copy import copy

import numpy

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.util.CommonFunctions import isIter
from quick.util.CommonFunctions import silenceRWarnings


class ClusterMatrixStat(MagicStatFactory):
    pass

#class ClusterMatrixStatSplittable(StatisticSumResSplittable):
#    pass
            
class ClusterMatrixStatUnsplittable(Statistic):
    def _init(self, distMethod='euclidean', clustMethod='complete', \
              childStat=None, numClustersRows='1', numClustersCols='1', complete='False', \
              rowClustId='None', colClustId='None', **kwArgs):
        assert childStat is not None
        assert isinstance(childStat, basestring)
        from gold.statistic.AllStatistics import STAT_CLASS_DICT
        self._childStat = STAT_CLASS_DICT[childStat]
        self._distMethod = distMethod
        self._clustMethod = clustMethod
        self._numClustersRows = int(numClustersRows)
        self._numClustersCols = int(numClustersCols)
        assert complete in ['False', 'True']
        self._complete = ast.literal_eval(complete)
        self._rowClustId = ast.literal_eval(rowClustId)
        self._colClustId = ast.literal_eval(colClustId)
        for id in [self._rowClustId, self._colClustId]:
            if id is not None:
                assert isinstance(id, int)
        silenceRWarnings()

    def _compute(self):
        if not isIter(self._region):
            #return {'Result':{'Matrix': None}}
            return None

        childRes = self._children[0].getResult()
        if childRes is None:
            return None
        
        childRes = childRes['Result']
        matrix = numpy.array(copy(childRes.get('Matrix')), dtype='float64')
        rows, cols, counts, pvals, significance = [numpy.array(copy(childRes.get(member))) if member in childRes else None \
                                           for member in ['Rows', 'Cols', 'Counts', 'Pvals', 'Significance']]
        
        if not self._complete:
            matrix, rows, cols, counts, pvals, significance = \
                self._removeNanLines(matrix, rows, cols, counts, pvals, significance)

        rowClust = self._getRowCluster(matrix)
        colClust = self._getColCluster(matrix)

        rowOrder, colOrder = self._getRowAndColOrders(rowClust, colClust)

        rows = self._cleanUpNameArray(rows, rowOrder)
        cols = self._cleanUpNameArray(cols, colOrder)

        if all(x == 1 for x in [self._numClustersRows, self._numClustersCols]):
            ret = {'Result': OrderedDict([('Matrix', matrix), ('Rows', rows), ('Cols', cols),\
                             ('RowClust', rowClust), ('ColClust', colClust),\
                             ('RowOrder', rowOrder), ('ColOrder', colOrder),\
                             ('Counts', counts)])}
            if pvals is not None:
                ret['Result']['Pvals'] = pvals
            if significance is not None:
                ret['Result']['Significance'] = significance
            return ret
        else:
            rowGroups = self._getGroups(rowClust, self._numClustersRows)
            colGroups = self._getGroups(colClust, self._numClustersCols)
            
            ret = {}
            for rowNo in xrange(rowGroups.max() + 1):
                for colNo in xrange(colGroups.max() + 1):
                    #print matrix, rows, cols, rowGroups, colGroups, rowNo, colNo
                    #print rowGroups == rowNo, colGroups ==colNo
                
                    newMatrix = copy(matrix[numpy.ix_(rowGroups==rowNo, colGroups==colNo)])
                    newCounts = copy(counts[numpy.ix_(rowGroups==rowNo, colGroups==colNo)])

                    if pvals is not None:
                        newPvals = copy(pvals[numpy.ix_(rowGroups==rowNo, colGroups==colNo)])

                    if significance is not None:
                        newSignificance = copy(significance[numpy.ix_(rowGroups==rowNo, colGroups==colNo)])

                    newRows = copy(rows[rowGroups==rowNo])
                    newCols = copy(cols[colGroups==colNo])

                    # if isIter(self._region):
                    rowClust = self._getRowCluster(newMatrix)
                    colClust = self._getColCluster(newMatrix)

                    rowOrder, colOrder = self._getRowAndColOrders(rowClust, colClust)

                    # print {'Matrix': newMatrix, 'Rows': newRows,
                    #        'Cols': newCols, 'RowClust': rowClust,
                    #        'ColClust': colClust}
                
                    label = 'Part_' + str(rowNo+1) + '_' + str(colNo+1)
                    ret[label] = {'Matrix': newMatrix, 'Rows': newRows,
                                  'Cols': newCols, 'Counts': newCounts}

                    if pvals is not None:
                        ret[label]['Pvals'] = newPvals

                    if significance is not None:
                        ret[label]['Significance'] = newSignificance

                    if rowClust is not None:
                        ret[label]['RowClust'] = rowClust
                        ret[label]['RowOrder'] = rowOrder

                    if colClust is not None:
                        ret[label]['ColClust'] = colClust
                        ret[label]['ColOrder'] = colOrder
            return ret

    def _getGroups(self, clust, numParts):
        # return numpy.array(rpy.r('function(clust, k){library(maptree);
        #   clip.clust(clust, k=k)}')(clust, numParts)) - 1
        from proto.RSetup import r
        return numpy.array(r('function(clust, k){cutree(clust, k=k)}')(clust, numParts)) - 1

    def _filterMatrix(self, matrix, minVal):
        matrix = copy(matrix)
        matrix[matrix<minVal] = 0
        return matrix

    def _getCluster(self, matrix, transpose):
        rFunc = '''
function(matrix, distMethod, clustMethod, distMatrix){
  if (distMethod == "spearman") {
    library(bioDist);
    distMatrix = spearman.dist(matrix, abs=FALSE);
  } else if (distMethod == "inversedotproduct" | distMethod == "correlation" | distMethod == "absolutecorrelation") {
    distMatrix = as.dist(distMatrix)
  } else {
    distMatrix = dist(matrix, method=distMethod, p=3);
  }

  if (clustMethod == "diana") {
    library(cluster);
    return(as.hclust(diana(distMatrix)));
  } else {
    library(flashClust);
    return(flashClust(distMatrix, method=clustMethod));
  }
}
'''
        matrix = copy(matrix)
        if transpose:
            matrix = matrix.transpose()

        matrix[numpy.isnan(matrix)] = matrix[numpy.isfinite(matrix)].mean()
        
        distMethod = self._distMethod
        if distMethod.endswith('_positive'):
            matrix = self._filterMatrix(matrix, 0)
            distMethod = distMethod.split('_')[0]
        else:
            minStr = '_min_'
            index = distMethod.find(minStr)
            if index >= 0:
                minVal = float(distMethod[index + len(minStr):])
                matrix = self._filterMatrix(matrix, minVal)
                distMethod = distMethod.split('_')[0]

        if distMethod == 'inversedotproduct':
            numVectors = matrix.shape[0]
            distMatrix = numpy.zeros(shape=[numVectors, numVectors])
            assert (matrix<0).sum() == 0, 'Inverse dot product does not work correctly on negative numbers.'
            for j in xrange(numVectors):
                for i in xrange(j, numVectors):
                    if not i == j:
                        distMatrix[i,j] = 1.0/(numpy.dot(matrix[i,:], matrix[j,:])+1)
            #print distMatrix
        elif distMethod == 'correlation':
            distMatrix = 1 - matrix
        elif distMethod == 'absolutecorrelation':
            distMatrix = 1 - numpy.absolute(matrix)
        else:
            distMatrix = None
            
        from proto.RSetup import r
        return r(rFunc)(matrix, distMethod, self._clustMethod, distMatrix)
    
    def _getClustFromPickledResult(self, id, clustKey, assertLen):
        from proto.RSetup import r
        from proto.hyperbrowser.StaticFile import RunSpecificPickleFile
        from quick.util.CommonFunctions import createFullGalaxyIdFromNumber
        
        res = RunSpecificPickleFile(createFullGalaxyIdFromNumber(id)).loadPickledObject()
        clust = res[0].getGlobalResult()['Result'][clustKey]
        hclust = r('function(clust){as.hclust(clust)}')(clust)
        
        assert len(hclust.rx2('order')) == assertLen
        
        return hclust
        
    def _getRowCluster(self, matrix):
        if self._rowClustId is None:
            return self._getCluster(matrix, transpose=False) if len(matrix) > 0 and matrix.shape[0] > 1 else None
        else:
            return self._getClustFromPickledResult(self._rowClustId, 'RowClust', matrix.shape[0])
        
    def _getColCluster(self, matrix):
        if self._colClustId is None:
            return self._getCluster(matrix, transpose=True) if len(matrix) > 0 and matrix.shape[1] > 1 else None            
        else:
            return self._getClustFromPickledResult(self._colClustId, 'ColClust', matrix.shape[1])

    def _getRowAndColOrders(self, rowClust, colClust):
        #logMessage(str(rowClust))
        rowOrder, colOrder = [numpy.array(clust.rx2('order')) - 1 if clust is not None else None for clust in [rowClust, colClust]]
        if rowOrder is not None:
            rowOrder = rowOrder[numpy.arange(len(rowOrder),0,-1) - 1] #reverse
        return rowOrder, colOrder

    def _removeNanLines(self, matrix, rows, cols, counts, pvals, significance):
        if len(matrix) == 0:
            return matrix, rows, cols, counts, pvals, significance
        
        nanColMask = numpy.all(numpy.isnan(matrix), axis=0)
        nanRowMask = numpy.all(numpy.isnan(matrix), axis=1)

        matrix = matrix.compress(numpy.logical_not(nanColMask), axis=1)
        matrix = matrix.compress(numpy.logical_not(nanRowMask), axis=0)

        if counts is not None:
            counts = counts.compress(numpy.logical_not(nanColMask), axis=1)
            counts = counts.compress(numpy.logical_not(nanRowMask), axis=0)

        if pvals is not None:
            pvals = pvals.compress(numpy.logical_not(nanColMask), axis=1)
            pvals = pvals.compress(numpy.logical_not(nanRowMask), axis=0)

        if significance is not None:
            significance = significance.compress(numpy.logical_not(nanColMask), axis=1)
            significance = significance.compress(numpy.logical_not(nanRowMask), axis=0)

        cols = cols[numpy.logical_not(nanColMask)]
        rows = rows[numpy.logical_not(nanRowMask)]
        
        return matrix, rows, cols, counts, pvals, significance

    def _cleanUpNameArray(self, nameArray, order):
        newNames = []
        sortMapping = order.argsort() if order is not None \
          else range(len(nameArray))

        for i, name in enumerate(nameArray):
            # fixme: Temporary hack to fix PWM names. Track names should not
            # have underscore in them, but these do.
            #       Don't know how to fix this in a nice manner
            # if not name[1] == '$':
            #    name = name.replace('_', ' ')
            newNames.append(str(sortMapping[i]+1) + '. ' + name)
            # newNames.append(str(i+1) + '. ' + name)

        return numpy.array(newNames)
            
    def _createChildren(self):
        kwArgs = copy(self._kwArgs)
        if 'childStat' in kwArgs:
            del kwArgs['childStat']
        del kwArgs['distMethod']
        del kwArgs['clustMethod']
        del kwArgs['numClustersRows']
        del kwArgs['numClustersCols']
        if 'rowClustId' in kwArgs:
            del kwArgs['rowClustId']
        if 'colClustId' in kwArgs:
            del kwArgs['colClustId']

        self._addChild( self._childStat(self._region, self._track, self._track2 if hasattr(self, '_track2') else None, **kwArgs) )
