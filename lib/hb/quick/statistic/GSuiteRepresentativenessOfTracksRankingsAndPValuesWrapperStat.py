from gold.track.TrackStructure import TrackStructure
from quick.statistic.GSuiteRepresentativenessOfTracksRankingsAndPValuesV2Stat import GSuiteRepresentativenessOfTracksRankingsAndPValuesV2Stat
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic


class GSuiteRepresentativenessOfTracksRankingsAndPValuesWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class GSuiteRepresentativenessOfTracksRankingsAndPValuesWrapperStatSplittable(StatisticSumResSplittable):
#    pass
            
class GSuiteRepresentativenessOfTracksRankingsAndPValuesWrapperStatUnsplittable(MultipleTrackStatistic):    
    def _compute(self):
        return self._children[0].getResult()
    
    def _createChildren(self):
        ts = TrackStructure()
        ts[TrackStructure.QUERY_KEY] = self._tracks
        self._addChild(GSuiteRepresentativenessOfTracksRankingsAndPValuesV2Stat(self._region, ts, **self._kwArgs))
