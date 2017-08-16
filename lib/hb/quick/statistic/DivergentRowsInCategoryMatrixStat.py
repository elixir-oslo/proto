from quick.statistic.CategoryMatrixStat import CategoryMatrixStatUnsplittable
from gold.statistic.MagicStatFactory import MagicStatFactory
import numpy
from collections import OrderedDict
#from proto.RSetup import r
#from gold.statistic.Statistic import Statistic, StatisticDictSumResSplittable
#from gold.track.Track import Track
#from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq
from copy import copy
#from quick.application.ProcTrackOptions import ProcTrackOptions
#import os
#from numpy import array
#from gold.statistic.ResultsMemoizer import ResultsMemoizer

class DivergentRowsInCategoryMatrixStat(MagicStatFactory):
    pass

#class DivergentRowsInCategoryMatrixStatSplittable(StatisticDictSumResSplittable):
#    pass
            
class DivergentRowsInCategoryMatrixStatUnsplittable(CategoryMatrixStatUnsplittable):    
    #def __init__(self, region, track, track2, rawStatistic=None, **kwArgs):        
    #    assert rawStatistic is not None
    #    assert isinstance(rawStatistic, basestring)
    #    from gold.statistic.AllStatistics import STAT_CLASS_DICT
    #    self._rawStatistic = STAT_CLASS_DICT[rawStatistic] 
    #    
    #    Statistic.__init__(self, region, track, track2, rawStatistic=rawStatistic, **kwArgs)

    def _compute(self):
        res = CategoryMatrixStatUnsplittable._compute(self)['Result']
        if len(res['Matrix'])==0:
            return None
        
        matrix = numpy.array( res['Matrix'] )
        
        rowSums = matrix.sum(axis=1)
        colSums = matrix.sum(axis=0)
        expMatrix = numpy.outer(rowSums, colSums) * 1.0 / (matrix.sum(dtype='float64'))
        basicDiffs = (matrix - expMatrix) 
        diffTerms = (1.0*basicDiffs**2 ) / expMatrix
        assert matrix.shape == diffTerms.shape
        x = diffTerms.sum(dtype='float64')
        
        numRows, numCols = matrix.shape
        df = (numRows-1)*(numCols-1)
        
        #pval = 1.0-r.pchisq(x,df)
        from proto.RSetup import r
        pval = r.pchisq(x,df,0,False)
        
        rowDiffCase = diffTerms[:,0]
        rowRanking = list(reversed(rowDiffCase.argsort()))
        rankedRows = [res['Rows'][i] for i in rowRanking]

        basicDiffsCase = basicDiffs[:,0]
        basicDiffsCaseForRankedRows = [basicDiffsCase[i] for i in rowRanking]
        
        rankedRowsMoreInCase = [rankedRows[i] for i in range(len(rankedRows)) if basicDiffsCaseForRankedRows[i]>0]
        rankedRowsLessInCase = [rankedRows[i] for i in range(len(rankedRows)) if basicDiffsCaseForRankedRows[i]<0]
        
        #Ranking based on simpleRatio..:
        simpleRatio_diffTerms = (1.0*basicDiffs) / expMatrix
        simpleRatio_rowDiffCase = simpleRatio_diffTerms[:,0]
        simpleRatio_rowRanking = list(reversed(simpleRatio_rowDiffCase.argsort()))
        simpleRatio_rankedRows = [res['Rows'][i] for i in simpleRatio_rowRanking]
        simpleRatio_rankedRowDiffs = [simpleRatio_rowDiffCase[i] for i in simpleRatio_rowRanking]
        #simpleRatio_rankedRowsMoreInCase = [simpleRatio_rankedRows[i] for i in range(len(simpleRatio_rankedRows)) if basicDiffsCaseForRankedRows[i]>0]
        #simpleRatio_rankedRowsLessInCase = [simpleRatio_rankedRows[i] for i in range(len(simpleRatio_rankedRows)) if basicDiffsCaseForRankedRows[i]<0]
        #end simpleRatio..
        
        additionalRes = OrderedDict([('P-value', pval), ('RankedRowsMoreInCase', rankedRowsMoreInCase), ('RankedRowsLessInCase', rankedRowsLessInCase)])
        res.update(additionalRes)
        res.update(OrderedDict([('simpleRatioRankedRowsMostCaseToLeastCase', simpleRatio_rankedRows), ('simpleRatioRankedRowDiffs', simpleRatio_rankedRowDiffs)]))
        return res
    
    def _createChildren(self):
        kwArgs = copy(self._kwArgs)
        if 'rawStatistic' in kwArgs:
            del kwArgs['rawStatistic']
        self._addChild( FormatSpecStat(self._region, self._track, TrackFormatReq(dense=False, val='category') ) )
        self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(dense=False, val='tc') ) )
        self._addChild( self._rawStatistic(self._region, self._track, self._track2, **kwArgs) )

    #def _createChildren(self):
        #self._addChild( CategoryMatrixStat(self._region, self._track, self._track2, **self._kwArgs)
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
                
                
        
