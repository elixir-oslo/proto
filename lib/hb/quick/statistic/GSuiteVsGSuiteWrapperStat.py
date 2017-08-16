'''
Created on Feb 29, 2016

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic
from gold.track.TrackStructure import TrackStructure
from quick.statistic.GSuiteVsGSuiteFullAnalysisV2Stat import GSuiteVsGSuiteFullAnalysisV2Stat


class GSuiteVsGSuiteWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class GSuiteVsGSuiteWrapperStatSplittable(StatisticSumResSplittable):
#    pass
            
class GSuiteVsGSuiteWrapperStatUnsplittable(MultipleTrackStatistic):
    
    def _init(self, queryTracksNum, refTracksNum, **kwArgs):
        self._queryTracksNum = int(queryTracksNum)
        self._refTracksNum = int(refTracksNum)
        
    def _compute(self):
        return self._children[0].getResult()
    
    def _createChildren(self):
        ts = TrackStructure()
        
        ts[TrackStructure.QUERY_KEY] = self._tracks[:self._queryTracksNum]
        ts[TrackStructure.REF_KEY] = self._tracks[self._queryTracksNum:]
        self._addChild(GSuiteVsGSuiteFullAnalysisV2Stat(self._region, ts, **self._kwArgs))
