from gold.track.TrackStructure import TrackStructure
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic
from quick.statistic.SummarizedInteractionWithOtherTracksV2Stat import SummarizedInteractionWithOtherTracksV2Stat


class SummarizedInteractionWithOtherTracksWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class GSuiteRepresentativenessOfTracksRankingsWrapperStatSplittable(StatisticSumResSplittable):
#    pass
            
class SummarizedInteractionWithOtherTracksWrapperStatUnsplittable(MultipleTrackStatistic):
    def _compute(self):
        res = self._children[0].getResult()
        return res

    def _createChildren(self):
        trackStructure = TrackStructure()
        trackStructure[TrackStructure.QUERY_KEY] = self._tracks
        self._addChild(SummarizedInteractionWithOtherTracksV2Stat(self._region, trackStructure, **self._kwArgs))
