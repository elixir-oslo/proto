'''
Created on Sep 23, 2015

@author: boris
'''


from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.StatisticV2 import StatisticV2


class QueryToReferenceCollectionStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class QueryToReferenceCollectionStatSplittable(StatisticSumResSplittable):
#    pass
            
class QueryToReferenceCollectionStatUnsplittable(StatisticV2):    
    
    def _init(self, pairwiseStat = None, **kwArgs):
        self._pairwiseStat = self.getRawStatisticClass(pairwiseStat)
    
    def _compute(self):
        for child in self._children:
            print child.getResult()
            print '_________'
    
    def _createChildren(self):
        queryTrack = self._trackStructure.getQueryTrackList()[0]
        for refTrack in self._trackStructure.getReferenceTrackList():
            self._addChild(self._pairwiseStat(self._region, queryTrack, refTrack, **self._kwArgs))
