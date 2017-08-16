from gold.track.TrackStructure import TrackStructure
from quick.statistic.GSuiteSimilarityToQueryTrackRankingsV2Stat import GSuiteSimilarityToQueryTrackRankingsV2Stat
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic


class GSuiteSimilarityToQueryTrackRankingsWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass


#class GSuiteSimilarityToQueryTrackRankingsWrapperStatSplittable(StatisticSumResSplittable):
#    pass


class GSuiteSimilarityToQueryTrackRankingsWrapperStatUnsplittable(MultipleTrackStatistic):
        
    def _compute(self):
        return self._children[0].getResult()
    
    def _createChildren(self):
    
        ts = TrackStructure()
        ts[TrackStructure.QUERY_KEY] = [self._tracks[0]]
        ts[TrackStructure.REF_KEY] = self._tracks[1:]
        self._addChild(GSuiteSimilarityToQueryTrackRankingsV2Stat(self._region, ts, **self._kwArgs))
