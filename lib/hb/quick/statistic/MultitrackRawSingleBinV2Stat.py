from gold.util.CommonFunctions import smartMeanWithNones
from quick.statistic.StatisticV2 import StatisticV2
from gold.track.TrackStructure import TrackStructure
from quick.util.debug import DebugUtil
from quick.statistic.RawDBGCodedEventsStat import RawDBGCodedEventsStat
import numpy as np
from _collections import defaultdict
from quick.statistic.BinSizeStat import BinSizeStat
from gold.track.Track import Track
'''
Created on Nov 3, 2015

@author: boris
'''


from gold.util.CustomExceptions import ShouldNotOccurError
from numpy import mean
from gold.statistic.MagicStatFactory import MagicStatFactory


class MultitrackRawSingleBinV2Stat(MagicStatFactory):
    '''
    '''
    pass

#class SummarizedInteractionWithOtherTracksStatSplittable(StatisticSumResSplittable):
#    pass
            
class MultitrackRawSingleBinV2StatUnsplittable(StatisticV2):
    

    functionDict = {
                    'sum': sum,
                    'avg': smartMeanWithNones,
                    'max': max,
                    'min': min
                    }

    
    def question6stat(self, O,E):
        if not E>0:
            T = 0
        else:
            T = np.sum(np.power((O-E),2)/E);
        return T

    def question7stat(self,O,E):
        if E==0:
            return 0 
        T = np.max(O)/E
        return T

    def _init(self, question="question 6", summaryFunc=None, reverse='No', **kwArgs):

        statFuncDict = {
            'question 6':self.question6stat,
            'question 7':self.question7stat,
            }
        
        self._summaryFunction = self._resolveFunction(summaryFunc)
        self._statistic = statFuncDict[question]
    
    def _resolveFunction(self, summaryFunc):
        if summaryFunc not in self.functionDict:
            raise ShouldNotOccurError(str(summaryFunc) + 
                                      ' not in list, must be one of ' + 
                                      str(sorted(self.functionDict.keys())))
        else: 
            return self.functionDict[summaryFunc]
        
    def _compute(self):
        O,E = self._children[0].getResult()
        return [self._statistic(O,E)]
#        return res
            
            
    def _createChildren(self):
        tracks = self._trackStructure.getQueryTrackList()
        t1 = tracks[0]
        t2 = tracks[1]
        self._addChild(RawDBGCodedEventsStat(self._region, t1, t2, extraTracks = tuple(tracks[2:]), **self._kwArgs))

#        self._binSizeStat = self._addChild( BinSizeStat(self._region, t1))
