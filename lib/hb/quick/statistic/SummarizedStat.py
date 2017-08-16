from gold.util.CommonFunctions import smartMeanWithNones, smartSum
from quick.statistic.StatisticV2 import StatisticV2
from gold.util.CustomExceptions import ShouldNotOccurError
from gold.statistic.MagicStatFactory import MagicStatFactory


class SummarizedStat(MagicStatFactory):
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


class SummarizedStatUnsplittable(StatisticV2):

    functionDict = {
                    'sum': smartSum,
                    'avg': smartMeanWithNones,
                    'max': max,
                    'min': min,
                    'raw': 'RawResults'
                    }

    def _init(self, pairwiseStatistic=None, summaryFunc=None,
              reverse='No', **kwArgs):
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
                return [child.getResult() for child in self._children]
            else:
                return self._summaryFunction([child.getResult()
                                              for child in self._children])
        else:
            raise ShouldNotOccurError('The summary function is not defined. Must be one of %' % str(sorted(self.functionDict.keys())))
            #we could return the list of results to make it more generic
            #but we should add this only if needed in the future

    def _createChildren(self):
        for t1 in self._trackStructure.getQueryTrackList():
            self._addChild(self._rawStatistic(self._region,
                                              t1, **self._kwArgs))
