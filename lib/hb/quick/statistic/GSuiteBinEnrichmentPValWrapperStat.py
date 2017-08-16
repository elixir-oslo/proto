from gold.track.TrackStructure import TrackStructure
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic
from quick.statistic.SummarizedStat import SummarizedStat
from quick.statistic.GSuiteBinEnrichmentPValStat import GSuiteBinEnrichmentPValStat

class GSuiteBinEnrichmentPValWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass


class GSuiteBinEnrichmentPValWrapperStatUnsplittable(MultipleTrackStatistic):
    def _compute(self):
        res = self._children[0].getResult()
        return res

    def _createChildren(self):
        trackStructure = TrackStructure()
        trackStructure[TrackStructure.QUERY_KEY] = self._tracks
        self._addChild(GSuiteBinEnrichmentPValStat(self._region, trackStructure, **self._kwArgs))
