#from quick.statistic.CategoryMatrixStat import CategoryMatrixStat
from gold.statistic.CategoryPointCountInSegsMatrixStat import CategoryPointCountInSegsMatrixStat
from quick.statistic.CategoryBinaryPointCountInSegsMatrixStat import CategoryBinaryPointCountInSegsMatrixStat
from quick.statistic.CategoryLogPointCountInSegsMatrixStat import CategoryLogPointCountInSegsMatrixStat
from quick.statistic.CategoryPointCountNoOverlapsStat import CategoryPointCountNoOverlapsStat
#from quick.statistic.GeneralTwoTracksIterateValsMatrixStat import GeneralTwoTracksIterateValsMatrixStat
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.util.CustomExceptions import ShouldNotOccurError
import numpy
#from proto.RSetup import r
from gold.statistic.Statistic import Statistic
from copy import copy
from gold.util.CommonFunctions import isIter
from collections import OrderedDict
#from gold.track.Track import Track
#from gold.statistic.RawDataStat import RawDataStat
#from gold.track.TrackFormat import TrackFormatReq
#from copy import copy
#from quick.application.ProcTrackOptions import ProcTrackOptions
#import os
#from numpy import array
#from gold.statistic.ResultsMemoizer import ResultsMemoizer

class CategoryDivergenceMatrixStat(MagicStatFactory):
    pass

#class DivergentRowsInCategoryMatrixStatSplittable(StatisticDictSumResSplittable):
#    pass
            
#class CategoryDivergenceMatrixStatUnsplittable(CategoryMatrixStatUnsplittable):
class CategoryDivergenceMatrixStatUnsplittable(Statistic):
    def __init__(self, region, track, track2, countMethod='count', normalizePointsBy='rowSum', \
                 pValueAdjustment='unadjusted', threshold='0.05', **kwArgs):
        assert countMethod in ['count', 'binary', 'logOfCount']
        self._countMethod = countMethod
        assert normalizePointsBy in ['nothing', 'rowSum', 'rowSumBalanced', 'rowCount', 'rowCountBalanced']
        self._normalizePointsBy = normalizePointsBy
        assert pValueAdjustment in ['unadjusted', 'fdr']
        self._pValueAdjustment = pValueAdjustment
        self._threshold = float(threshold)
        assert 0.0 <= self._threshold <= 1.0
        Statistic.__init__(self, region, track, track2, countMethod=countMethod, normalizePointsBy=normalizePointsBy, \
                           pValueAdjustment=pValueAdjustment, threshold=threshold, **kwArgs)


    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)
    def _compute(self):
        if not isIter(self._region):
            return None
            #return {'Result':{'Matrix': None}}
        
#        res = CategoryMatrixStatUnsplittable._compute(self)
        res = self._children[0].getResult()['Result']
        if len(res['Matrix'])==0:
            return None
        
        rowCountDict = self._children[1].getResult()
        colCountDict = self._children[2].getResult()
        
        rownames, colnames = res['Rows'], numpy.array(res['Cols'])
        matrix = numpy.array( res['Matrix'] )
                
        totIndex = numpy.where(colnames == 'Totals')[0]
        assert len(totIndex) == 1
        totIndex = totIndex[0]
        
        colnames = numpy.concatenate((colnames[:totIndex], colnames[totIndex+1:]))
        rowCounts = matrix[:,totIndex]
        matrix = numpy.concatenate((matrix[:,:totIndex], matrix[:,totIndex+1:]), axis=1)

        rownames = self._appendCountsToNameArray(rownames, rowCountDict)
        colnames = self._appendCountsToNameArray(colnames, colCountDict)

        colSums = matrix.sum(axis=0)
        
        if self._normalizePointsBy == 'nothing':                        
            return {'Result': OrderedDict([('Matrix', matrix), ('Rows', rownames), ('Cols', colnames)])}
        elif self._normalizePointsBy in ['rowSum', 'rowSumBalanced']:
            rowSums = matrix.sum(axis=1, dtype='float64')
            N = matrix.sum(dtype='float64')
            expMatrix = numpy.outer(rowSums, colSums) * 1.0 / N
            #pValMatrix = self._calcHypergeometricPVals(matrix, colSums, rowSums, N)
            pValMatrix = self._calcBinomialPVals(matrix, colSums, rowSums, N)
        elif self._normalizePointsBy in ['rowCount', 'rowCountBalanced']:
            #rowCounts = numpy.array([rowCountDict[x] for x in res['Rows']])
            N = rowCounts.sum()
            expMatrix = numpy.outer(rowCounts, colSums) * 1.0 / N
            pValMatrix = self._calcHypergeometricPVals(matrix, colSums, rowCounts, N)
        else:
            raise ShouldNotOccurError

        signMatrix = self._calcSignificanceMatrix(pValMatrix)

        basicDiffs = (matrix - expMatrix) 
        #diffTerms = (1.0*basicDiffs**2 ) / expMatrix
        #assert matrix.shape == diffTerms.shape
        #x = diffTerms.sum()
        
        #numRows, numCols = matrix.shape
        #df = (numRows-1)*(numCols-1)
        
        #pval = 1.0-r.pchisq(x,df)
        
        #Could be used..: pval = r.pchisq(x,df,0,False)
                
        #Ranking based on simpleRatio..:
        if self._normalizePointsBy.endswith('Balanced'):
            #rowCounts = numpy.array([rowCountDict[x] for x in res['Rows']])
            rowCounts.shape = [len(rowCounts), 1]
            rowCountMatrix = numpy.hstack([rowCounts] * matrix.shape[1])
            simpleRatio_diffTerms = (1.0*basicDiffs) / numpy.sqrt(expMatrix * (1.0 - (expMatrix/rowCountMatrix)))
        else:
            simpleRatio_diffTerms = (1.0*basicDiffs) / expMatrix

        newRes = {'Result': OrderedDict([('Matrix', simpleRatio_diffTerms), ('Rows', rownames), ('Cols', colnames), \
                                         ('Counts', matrix), ('Pvals', pValMatrix), ('Significance', signMatrix)])}
        return newRes

    def _calcBinomialPVals(self, countMatrix, colSums, rowSums, N):
        from proto.RSetup import r
        pValMatrix = numpy.zeros(countMatrix.shape)
        for i in xrange(pValMatrix.shape[0]):
            for j in xrange(pValMatrix.shape[1]):
                q = x = int(countMatrix[i,j])
                size = int(colSums[j])
                prob = float(rowSums[i])/N
#                print q,size,prob
                rawPval = min( r.pbinom(q, size, prob, True), r.pbinom(q, size, prob, False) + r.dbinom(q, size, prob) )
#                rawPval = min( r.pbinom(q, size, prob, True) - 0.5 * r.dbinom(q, size, prob), \
#                               r.pbinom(q, size, prob, False) + 0.5 * r.dbinom(q, size, prob) )
                pValMatrix[i,j] = min(rawPval*2, 1) #correct for two-tail..
        return pValMatrix
    
    def _calcHypergeometricPVals(self, countMatrix, colSums, rowCounts, N):
        from proto.RSetup import r
        pValMatrix = numpy.zeros(countMatrix.shape)
        for i in xrange(pValMatrix.shape[0]):
            for j in xrange(pValMatrix.shape[1]):
                q = x = int(countMatrix[i,j])
                m = int(rowCounts[i])
                n = int(N - m)
                k = int(colSums[j])
#                print q,m,n,k
                rawPval = min( r.phyper(q, m, n, k, True), r.phyper(q, m, n, k, False) + r.dhyper(x, m, n, k) )
#                rawPval = min( r.phyper(q, m, n, k, True) - 0.5 * r.dhyper(x, m, n, k), \
#                               r.phyper(q, m, n, k, False) + 0.5 * r.dhyper(x, m, n, k) )
                pValMatrix[i,j] = min(rawPval*2, 1) #correct for two-tail..
        return pValMatrix

    def _calcSignificanceMatrix(self, pValMatrix):
        if self._pValueAdjustment == 'fdr':
            from proto.RSetup import r
            pValMatrix = r('p.adjust')(pValMatrix, 'fdr')
        return pValMatrix < self._threshold
    
    def _appendCountsToNameArray(self, nameArray, countDict):
        newNames = []
        for name in nameArray:
            newNames.append(name + ' (' + self._formatCount(countDict[name]) + ')')
        return numpy.array(newNames)
    
    def _formatCount(self, count):
        if count >= 1000000:
            return "%.1fm" % (count/1000000.0)
        elif count >= 1000:
            return "%.1fk" % (count/1000.0)
        return str(count)

    def _createChildren(self):
        kwArgs = copy(self._kwArgs)
        del kwArgs['normalizePointsBy']
        del kwArgs['pValueAdjustment']
        del kwArgs['threshold']
        del kwArgs['countMethod']
#        allKwArgs.update({'rawStatistic':'PointCountIsideSegsStat'})
#        self._addChild( GeneralTwoTracksIterateValsMatrixStat(self._region, self._track, self._track2, **allKwArgs))
        if self._countMethod == 'count':
            self._addChild( CategoryPointCountInSegsMatrixStat(self._region, self._track, self._track2, \
                                                               calcPointTotals=True, **kwArgs) )
        elif self._countMethod == 'binary':
            self._addChild( CategoryBinaryPointCountInSegsMatrixStat(self._region, self._track, self._track2, \
                                                                     calcPointTotals=True, **kwArgs) )
        elif self._countMethod == 'logOfCount':
            self._addChild( CategoryLogPointCountInSegsMatrixStat(self._region, self._track, self._track2, \
                                                                  calcPointTotals=True, **kwArgs) )
        else:
            raise ShouldNotOccurError
        self._addChild( CategoryPointCountNoOverlapsStat(self._region, self._track) )
        self._addChild( CategoryPointCountNoOverlapsStat(self._region, self._track2) )
        #self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, val='category') ) ) #category
        #self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, val='tc') ) )
        #self._addChild( self._rawStatistic(self._region, self._track, self._track2, **kwArgs) )
        #try:
        
        #tr1Subtypes = ProcTrackOptions.getSubtypes(self._region.genome, self._track.trackName, True)
        #for subtype1 in tr1Subtypes:#['0','1']:
        #    for subtype2 in ['0','1']:
        #        track1 = Track( self._track.trackName + [subtype1])
        #        track1.formatConverters = self._track.formatConverters
        #        track2 = Track( self._track2.trackName + [subtype2])
        #        track2.formatConverters = self._track2.formatConverters
        #        self._addChild(self._rawStatistic(self._region, track1, track2, **kwArgs) )
                
                
        
