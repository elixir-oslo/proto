'''
Created on Sep 23, 2015

@author: boris
'''


from quick.statistic.QueryToReferenceCollectionStat import QueryToReferenceCollectionStatUnsplittable
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic
from gold.track.TrackStructure import TrackStructure


class QueryToReferenceCollectionWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class QueryToReferenceCollectionWrapperStatSplittable(StatisticSumResSplittable):
#    pass
            
class QueryToReferenceCollectionWrapperStatUnsplittable(MultipleTrackStatistic):
    
    def _compute(self):
        #2. call the new type statistic
        #3. return the result
        return self._newStat._compute()
    
    def _createChildren(self):
        queryTracks = self._tracks[:1]
        refTracks = self._tracks[1:]
        trackStructure = TrackStructure()
        trackStructure[TrackStructure.QUERY_KEY] = queryTracks
        trackStructure[TrackStructure.REF_KEY] = refTracks
        if 'extraTracks' in self._kwArgs:
            del self._kwArgs['extraTracks']
#         self._kwArgs['trackStructure'] = trackStructure
        self._newStat = QueryToReferenceCollectionStatUnsplittable(self._region, trackStructure, **self._kwArgs)        
        self._newStat._createChildren()
