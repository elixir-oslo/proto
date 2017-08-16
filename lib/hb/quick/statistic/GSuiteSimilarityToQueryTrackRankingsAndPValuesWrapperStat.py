from gold.track.TrackStructure import TrackStructure
from quick.statistic.GSuiteSimilarityToQueryTrackRankingsAndPValuesV2Stat import GSuiteSimilarityToQueryTrackRankingsAndPValuesV2Stat
from gold.util.CommonFunctions import prettyPrintTrackName
'''
Created on Dec 22, 2015

@author: boris
'''


from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, MultipleTrackStatistic


class GSuiteSimilarityToQueryTrackRankingsAndPValuesWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class GSuiteSimilarityToQueryTrackRankingsAndPValuesWrapperStatSplittable(StatisticSumResSplittable):
#    pass
            
class GSuiteSimilarityToQueryTrackRankingsAndPValuesWrapperStatUnsplittable(MultipleTrackStatistic):    
    def _compute(self):
        return self._children[0].getResult()
    
    def _createChildren(self):
        
#         for t in self._tracks:
#             print prettyPrintTrackName(t.trackName)
#         
#         
        ts = TrackStructure()
        ts[TrackStructure.QUERY_KEY] = [self._tracks[0]]
        ts[TrackStructure.REF_KEY] = self._tracks[1:]
        self._addChild(GSuiteSimilarityToQueryTrackRankingsAndPValuesV2Stat(self._region, ts, **self._kwArgs))
        
