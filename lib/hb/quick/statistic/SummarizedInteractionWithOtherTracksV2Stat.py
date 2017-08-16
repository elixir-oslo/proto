"""
Created on Nov 3, 2015

@author: boris
"""
from gold.util.CommonFunctions import smartMeanWithNones, smartSum
from quick.statistic.StatisticV2 import StatisticV2
from gold.util.CustomExceptions import ShouldNotOccurError
from gold.statistic.MagicStatFactory import MagicStatFactory


class SummarizedInteractionWithOtherTracksV2Stat(MagicStatFactory):
    """
    STAT Q k,n

    Calculate the summary function (min, max, avg, sum) for all the interactions of first track
    in self._tracks with the rest of the tracks. An interaction is defined by the pair-wise statistic
    whose name is passed in as the argument rawStatistic.
    @rawStatistic - str
    @summaryFunc - function
    @reverse - boolean
    """
    pass

#class SummarizedInteractionWithOtherTracksStatSplittable(StatisticSumResSplittable):
#    pass

class SummarizedInteractionWithOtherTracksV2StatUnsplittable(StatisticV2):

    functionDict = {
                    'sum': smartSum,
                    'avg': smartMeanWithNones,
                    'max': max,
                    'min': min,
                    'raw': 'RawResults'
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
            if self._summaryFunction == 'RawResults':
                resultList = [child.getResult() for child in self._children]
                return resultList
            else:
                childrenResList = [child.getResult() for child in self._children]
                return self._summaryFunction(childrenResList)
        else:
            raise ShouldNotOccurError('The summary function is not defined. Must be one of %' % str(sorted(self.functionDict.keys())))
            #we could return the list of results to make it more generic
            #but we should add this only if needed in the future
            
            
    def _createChildren(self):
        t1 = self._trackStructure.getQueryTrackList()[0]
        for t2 in self._trackStructure.getReferenceTrackList():
            if self._reversed == 'Yes':
                self._addChild( self._rawStatistic(self._region, t2, t1, **self._kwArgs))
            else:
                self._addChild( self._rawStatistic(self._region, t1, t2, **self._kwArgs))
