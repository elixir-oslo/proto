from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSplittable
#from gold.statistic.RawDataStat import RawDataStat
#from gold.track.TrackFormat import TrackFormatReq

class LocalResultsCollectionStat(MagicStatFactory):
    pass

class LocalResultsCollectionStatSplittable(StatisticSplittable):
    def _combineResults(self):
        self._result = dict( zip( list(self._region),self._childResults) )#reduce(lambda l1,l2:l1+l2, self._childResults)

            
class LocalResultsCollectionStatUnsplittable(Statistic):
    '''Takes as parameter a rawStatistic, which should be a class that returns a single numerical value as getResult.
    LocalResultsCollectionStat will then compute these values from all bins, and for each bin normalize these according to
    a specified normalizationType, e.g. so that all values per bin are scaled between zero and one.
    The normalized values are then returned by getResult.
    '''
    
    def __init__(self, region, track, track2, rawStatistic=None, **kwArgs):
        Statistic.__init__(self, region, track, track2, rawStatistic=rawStatistic, **kwArgs)        

        if type(rawStatistic) is str:
            from gold.statistic.AllStatistics import STAT_CLASS_DICT
            rawStatistic = STAT_CLASS_DICT[rawStatistic]
     
        self._rawStatistic = rawStatistic

        
    def _compute(self):
        return self._children[0].getResult()

    def _createChildren(self):
        self._addChild( self._rawStatistic(self._region, self._track) ) #might also add self._track2        
