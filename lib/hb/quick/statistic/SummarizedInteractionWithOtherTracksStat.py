'''
Created on Apr 30, 2015

@author: boris
'''
from gold.util.CommonFunctions import smartMeanWithNones, smartSum
from gold.util.CustomExceptions import ShouldNotOccurError
from numpy import mean
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic


class SummarizedInteractionWithOtherTracksStat(MagicStatFactory):
    '''
    STAT Q k,n
    
    Calculate the summary function (min, max, avg, sum) for all the interactions of first track
    in self._tracks with the rest of the tracks. An interaction is defined by the pair-wise statistic
    whose name is passed in as the argument rawStatistic.
    @rawStatistic - str
    @summaryFunc - function
    @reverse - boolean
    '''
    pass

#class SummarizedInteractionWithOtherTracksStatSplittable(StatisticSumResSplittable):
#    pass
            
class SummarizedInteractionWithOtherTracksStatUnsplittable(MultipleTrackStatistic):

    functionDict = {
                    'sum': smartSum,
                    'avg': smartMeanWithNones,
                    'max': max,
                    'min': min
                    }
    
    def _init(self, pairwiseStatistic=None, summaryFunc=None, reverse='No', **kwArgs):
        self._rawStatistic = self.getRawStatisticClass(pairwiseStatistic)
        self._summaryFunction = self._resolveFunction(summaryFunc)
        assert reverse in ['Yes', 'No'], 'reverse must be one of "Yes" or "No"'
        self._reversed = reverse
    
    def _resolveFunction(self, summaryFunc):
        if summaryFunc not in self.functionDict:
            raise ShouldNotOccurError(str(summaryFunc) + 
                                      ' not in list, must be one of ' + 
                                      str(sorted(self.functionDict.keys())))
        else: 
            return self.functionDict[summaryFunc]
        
    def _compute(self):
        if self._summaryFunction:
            results = []
            for i, child in enumerate(self._children):
                results.append(child.getResult())
            return self._summaryFunction(results)
        else:
            raise ShouldNotOccurError('The summary function is not defined')
            #we could return the list of results to make it more generic
            #but we should add this only if needed in the future
            
            
    def _createChildren(self):
        t1 = self._tracks[0]
        for t2 in self._tracks[1:]:
            if self._reversed == 'Yes':
                self._addChild( self._rawStatistic(self._region, t2, t1, **self._kwArgs) )
            else:
                self._addChild( self._rawStatistic(self._region, t1, t2, **self._kwArgs) )
