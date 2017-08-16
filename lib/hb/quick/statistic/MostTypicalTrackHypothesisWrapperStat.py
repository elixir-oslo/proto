'''
Created on Nov 10, 2015

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic
from gold.track.TrackStructure import TrackStructure
from quick.statistic.MostTypicalTrackHypothesisV2Stat import MostTypicalTrackHypothesisV2Stat


class MostTypicalTrackHypothesisWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class MostTypicalTrackHypothesisWrapperStatSplittable(StatisticSumResSplittable):
#    pass
            
class MostTypicalTrackHypothesisWrapperStatUnsplittable(MultipleTrackStatistic):    
    def _compute(self):
        return self._children[0].getResult()
    
    def getTrackStructureFromTracks(self, tracks):
        ts = TrackStructure()
        ts[TrackStructure.QUERY_KEY] = tracks
        return ts
    
    def _createChildren(self):
        self._addChild(MostTypicalTrackHypothesisV2Stat(self._region, 
                                                          self.getTrackStructureFromTracks(self._tracks), 
                                                          **self._kwArgs))
