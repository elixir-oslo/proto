from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.CountPointStat import CountPointStat
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class MeanOfMeanSdStat(MagicStatFactory):
    pass

#class MeanOfMeanSdStatSplittable(StatisticSumResSplittable):
#    pass
            
class MeanOfMeanSdStatUnsplittable(Statistic):    
    IS_MEMOIZABLE = False
    
    def _compute(self):
        #computes the mean of mean and sd for each segment without any wegihting..
        return dict(zip(['meanOfMean','meanOfStdDev'], [sum([el.val()[i] for el in self._children[1].getResult()]) / self._children[0].getResult() for i in [0,1]]))
    
    def _createChildren(self):
        self._addChild( CountPointStat(self._region, self._track) )
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, val='mean_sd')) )
