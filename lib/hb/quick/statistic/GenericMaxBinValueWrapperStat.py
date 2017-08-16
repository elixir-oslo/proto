from gold.track.TrackStructure import TrackStructure
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic
from quick.statistic.GenericMaxBinValueStat import GenericMaxBinValueStat
from quick.statistic.SummarizedStat import SummarizedStat


class GenericMaxBinValueWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class GSuiteRepresentativenessOfTracksRankingsWrapperStatSplittable(StatisticSumResSplittable):
#    pass

class GenericMaxBinValueWrapperStatUnsplittable(MultipleTrackStatistic):
    def _compute(self):
        res = self._children[0].getResult()
        return res

    def _createChildren(self):
        trackStructure = TrackStructure()
        trackStructure[TrackStructure.QUERY_KEY] = self._tracks
        self._addChild(GenericMaxBinValueStat(self._region, trackStructure, **self._kwArgs))
