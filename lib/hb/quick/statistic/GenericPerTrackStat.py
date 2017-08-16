from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic

class GenericPerTrackStat(MagicStatFactory):
    pass

#class GenericPerTrackStatSplittable(StatisticSumResSplittable):
#    pass
            
class GenericPerTrackStatUnsplittable(MultipleTrackStatistic):
    def _init(self, rawStatistic=None, **kwArgs):
        self._rawStatistic = self.getRawStatisticClass(rawStatistic)
                
    def _compute(self):
        return [child.getResult() for child in self._children]
            
    
    def _createChildren(self):
        for track in self._tracks:
            self._addChild( self._rawStatistic(self._region, track, **self._kwArgs) )
