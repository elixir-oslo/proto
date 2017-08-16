from gold.track.TrackStructure import TrackStructure
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic
from quick.statistic.GSuiteRepresentativenessOfTracksRankingsV2Stat import GSuiteRepresentativenessOfTracksRankingsV2Stat


class GSuiteRepresentativenessOfTracksRankingsWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class GSuiteRepresentativenessOfTracksRankingsWrapperStatSplittable(StatisticSumResSplittable):
#    pass
            
class GSuiteRepresentativenessOfTracksRankingsWrapperStatUnsplittable(MultipleTrackStatistic):    
    def _compute(self):
        res = self._children[0].getResult()
        return res

    def _createChildren(self):
        trackStructure = TrackStructure()
        trackStructure[TrackStructure.QUERY_KEY] = self._tracks
        self._addChild(GSuiteRepresentativenessOfTracksRankingsV2Stat(self._region, trackStructure, **self._kwArgs))
