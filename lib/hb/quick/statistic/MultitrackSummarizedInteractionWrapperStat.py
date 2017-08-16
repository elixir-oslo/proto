from gold.track.TrackStructure import TrackStructure
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic
from quick.statistic.MultitrackSummarizedInteractionV2Stat import \
    MultitrackSummarizedInteractionV2Stat


class MultitrackSummarizedInteractionWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass


class MultitrackSummarizedInteractionWrapperStatUnsplittable(MultipleTrackStatistic):
    def _compute(self):
        res = self._children[0].getResult()
        return res

    def _createChildren(self):
        trackStructure = TrackStructure()
        trackStructure[TrackStructure.QUERY_KEY] = self._tracks
        self._addChild(
            MultitrackSummarizedInteractionV2Stat(
                self._region, trackStructure, **self._kwArgs
            )
        )
