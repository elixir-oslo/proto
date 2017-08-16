from gold.track.TrackStructure import TrackStructure
from quick.statistic.CollectionBinnedHypothesisV2Stat import CollectionBinnedHypothesisV2Stat
from quick.util.debug import DebugUtil
'''
Created on Nov 3, 2015

@author: boris
'''


from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic

class CollectionBinnedHypothesisWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class TrackSimilarityToCollectionHypothesisWrapperStatSplittable(StatisticSumResSplittable):
#    pass
            
class CollectionBinnedHypothesisWrapperStatUnsplittable(MultipleTrackStatistic):    
    
    def _compute(self):
        res = self._children[0].getResult()
        return res

    def getTrackStructureFromTracks(self, tracks):
        ts = TrackStructure()
        queryTracks = tracks
        refTracks = []
        ts[TrackStructure.QUERY_KEY] = queryTracks
        ts[TrackStructure.REF_KEY] = refTracks
        return ts
    
    def _createChildren(self):
        trackStructure = self.getTrackStructureFromTracks(self._tracks)
        self._addChild(CollectionBinnedHypothesisV2Stat(self._region, trackStructure, **self._kwArgs))
