# DD

from numpy import zeros

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import MultipleTrackStatistic
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.BinSizeStat import BinSizeStat


class SumTrackPointsStat(MagicStatFactory):
    pass

# class SumTrackPointsStatSplittable(StatisticSplittable):
#     def _combineResults(self):
#         self._result = RawVisualizationResultType(self._childResults)
#         
    
class SumTrackPointsStatUnsplittable(MultipleTrackStatistic):
    IS_MEMOIZABLE = False
        
    def _compute(self):
        # print 'bin:::' + str(self._binSizeStat.getResult()) + '<br />'
        if self._binSizeStat.getResult() > 1:
            result = zeros(self._binSizeStat.getResult())
            
            # print 'result:::' + str(result)
            for track in self._children[:-1]:
                # print 'track:::' + str(track)
                result += track.getResult().getBinaryBpLevelArray()

            # print result
            exit()

    def _createChildren(self):
        for track in self._tracks:
            self._addChild( RawDataStat(self._region, track, TrackFormatReq(dense=False), **self._kwArgs) )
        self._binSizeStat = self._addChild(BinSizeStat(self._region, self._tracks[0]))
