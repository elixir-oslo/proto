from gold.util.CommonFunctions import smartMeanWithNones, smartSum
from gold.util.CustomExceptions import ShouldNotOccurError
from numpy import mean
from gold.track.TrackStructure import TrackStructure
from quick.statistic.SummarizedInteractionWithOtherTracksV2Stat import SummarizedInteractionWithOtherTracksV2Stat
'''
Created on Nov 9, 2015

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.StatisticV2 import StatisticV2


class MultitrackSummarizedInteractionV2Stat(MagicStatFactory):
    '''
    (TrackStructure version)
    STAT Rk,s,i
    
    R_(k,s,1) (A)=[min]_i (Q_(k,s) [(A]_i,A_(-i))) measures the minimum interaction with the other tracks.
    R_(k,s,2) (A)=[max]_i (Q_(k,s) [(A]_i,A_(-i))) measures the maximum interaction with the other tracks.
    R_(k,s,3) (A)=Sum_i[Q_(k,s) [(A_i,A_(-i))]  measures the average interaction with the other tracks.

    R_(k,s,u) (A) measures how similar is the tracks in the collection A
    '''
    pass

#class MultitrackSummarizedInteractionV2StatSplittable(StatisticSumResSplittable):
#    pass
            
class MultitrackSummarizedInteractionV2StatUnsplittable(StatisticV2):    
    
    functionDict = {
                'sum': smartSum,
                'avg': smartMeanWithNones,
                'max': max,
                'min': min,
                'raw': 'RawResults'
                }
    
    def _resolveFunction(self, summaryFunc):
        if summaryFunc not in self.functionDict:
            raise ShouldNotOccurError(str(summaryFunc) + 
                                      ' is not in the list of allowed summary functions, must be one of ' + 
                                      str(sorted(self.functionDict.keys())))
        else: 
            return self.functionDict[summaryFunc]
    
    def _init(self, multitrackSummaryFunc=None, **kwArgs):
        self._multitrackSummaryFunc = self._resolveFunction(multitrackSummaryFunc)
       
    def _compute(self):
        if self._multitrackSummaryFunc:
            res = [child.getResult() for child in self._children]
            if self._multitrackSummaryFunc == 'RawResults':
                return res
            else:
                return self._multitrackSummaryFunc(res)
        else:
            raise ShouldNotOccurError('The summary function is not defined')
    
    def _createChildren(self):
        trackList = self._trackStructure[TrackStructure.QUERY_KEY]
        for i, track in enumerate(trackList):
            ts = TrackStructure({TrackStructure.QUERY_KEY : [track], TrackStructure.REF_KEY : trackList[:i]+trackList[i+1:]})
#             print ts
#             for key, val in ts.iteritems():
#                 print key
#                 for t in val:
#                     print t.trackName
            self._addChild(SummarizedInteractionWithOtherTracksV2Stat(self._region, ts, **self._kwArgs))
            
