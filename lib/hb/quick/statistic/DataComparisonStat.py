from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.XYPairStat import XYPairStat

class DataComparisonStat(MagicStatFactory):
    pass

#class DataComparisonStatStatSplittable(StatisticSumResSplittable):
#    pass
            
class DataComparisonStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    
    def __init__(self, region, track, track2, track1SummarizerName, track2SummarizerName, *args, **kwArgs):
        Statistic.__init__(self, region, track, track2, track1SummarizerName=track1SummarizerName, \
                           track2SummarizerName=track2SummarizerName, allowIdenticalTracks=True, **kwArgs)
        from gold.statistic.AllStatistics import STAT_CLASS_DICT
        assert( track1SummarizerName in STAT_CLASS_DICT and track2SummarizerName in STAT_CLASS_DICT)
        
        self._track1Summarizer = STAT_CLASS_DICT[track1SummarizerName]
        self._track2Summarizer = STAT_CLASS_DICT[track2SummarizerName]
        
    def _compute(self):
        res = self._children[0].getResult()
        return res #self._children[0].getResult()
    
    def _createChildren(self):
        self._addChild( XYPairStat(self._region, self._track, self._track2, self._track1Summarizer, self._track2Summarizer) )
