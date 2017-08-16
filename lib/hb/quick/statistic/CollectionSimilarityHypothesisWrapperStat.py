'''
Created on Nov 9, 2015

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic
from gold.track.TrackStructure import TrackStructure
from quick.statistic.CollectionSimilarityHypothesisV2Stat import CollectionSimilarityHypothesisV2Stat


class CollectionSimilarityHypothesisWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class CollectionSimilarityHypothesisWrapperStatSplittable(StatisticSumResSplittable):
#    pass
            
class CollectionSimilarityHypothesisWrapperStatUnsplittable(MultipleTrackStatistic):    
    def _compute(self):
        return self._children[0].getResult()
    
    
    def getTrackStructureFromTracks(self, tracks):
        ts = TrackStructure()
            
        ts[TrackStructure.QUERY_KEY] = tracks
        return ts
    
    def _createChildren(self):
        self._addChild(CollectionSimilarityHypothesisV2Stat(self._region, 
                                                          self.getTrackStructureFromTracks(self._tracks), 
                                                          **self._kwArgs))
