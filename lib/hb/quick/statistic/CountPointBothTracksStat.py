from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.CountPointStat import CountPointStat

class CountPointBothTracksStat(MagicStatFactory):
    pass

#class CountPointBothTracksStatSplittable(StatisticSumResSplittable):
#    pass

class CountPointBothTracksStatUnsplittable(Statistic):
    def _compute(self):
        return {'track1_count':self._children[0].getResult(), 'track2_count':self._children[1].getResult()}
    
    def _createChildren(self):
        self._addChild( CountPointStat(self._region, self._track) )
        self._addChild( CountPointStat(self._region, self._track2) )
