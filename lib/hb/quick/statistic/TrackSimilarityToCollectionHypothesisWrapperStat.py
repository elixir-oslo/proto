from gold.track.TrackStructure import TrackStructure
from quick.statistic.TrackSimilarityToCollectionHypothesisV2Stat import TrackSimilarityToCollectionHypothesisV2Stat
'''
Created on Nov 3, 2015

@author: boris
'''


from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic


class TrackSimilarityToCollectionHypothesisWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class TrackSimilarityToCollectionHypothesisWrapperStatSplittable(StatisticSumResSplittable):
#    pass
            
class TrackSimilarityToCollectionHypothesisWrapperStatUnsplittable(MultipleTrackStatistic):    
    
    def _compute(self):
        return self._children[0].getResult()

    def getTrackStructureFromTracks(self, tracks):
        ts = TrackStructure()
        queryTracks = [tracks[0]]
        refTracks = tracks[1:]
            
        ts[TrackStructure.QUERY_KEY] = queryTracks
        ts[TrackStructure.REF_KEY] = refTracks
        return ts
    
    def _createChildren(self):
        trackStructure = self.getTrackStructureFromTracks(self._tracks)
        self._addChild(TrackSimilarityToCollectionHypothesisV2Stat(self._region, trackStructure, **self._kwArgs))
