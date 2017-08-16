from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic
from quick.statistic.SummarizedInteractionWithOtherTracksV2Stat import SummarizedInteractionWithOtherTracksV2Stat
from gold.track.TrackStructure import TrackStructure
from quick.util.debug import DebugUtil


class NormalizedObservedVsExpectedStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class NormalizedObservedVsExpectedStatSplittable(StatisticSumResSplittable):
#    pass
            
class NormalizedObservedVsExpectedStatUnsplittable(MultipleTrackStatistic):
    """The statistic is normalized in relation to the reference GSuite."""

    def _init(self, queryTracksNum=None, **kwArgs):
        self._queryTracksNum = int(queryTracksNum)

    def _compute(self):
        nominator = self._nominator.getResult()
        denominator = self._denominator.getResult()
        # if nominator and denominator and denominator > 0:
        #     return float(nominator)/denominator
        if nominator is not None and denominator is not None and denominator > 0:
            return float(nominator)/denominator
        else:
            from numpy import nan
            return nan
    
    def _createChildren(self):
        
        ts = TrackStructure()
        ts[TrackStructure.QUERY_KEY] = [self._tracks[0]]
        ts[TrackStructure.REF_KEY] = self._tracks[self._queryTracksNum:]
        # DebugUtil.insertBreakPoint()
        from quick.statistic.StatFacades import ObservedVsExpectedStat
        self._nominator = self._addChild(ObservedVsExpectedStat(self._region, self._track, self._track2, **self._kwArgs))
        self._denominator = self._addChild(
            SummarizedInteractionWithOtherTracksV2Stat(
                self._region,
                ts,
                pairwiseStatistic='ObservedVsExpectedStat',
                summaryFunc='avg',
                reverse=(self._kwArgs['reverse'] if 'reverse' in self._kwArgs else 'No'))
        )
