'''
Created on Feb 24, 2016

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import Statistic, OnlyGloballySplittable,\
    StatisticConcatDictOfNumpyArrayResSplittable
from gold.track.TrackFormat import TrackFormatReq


class ElementDistancesStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

class ElementDistancesStatSplittable(StatisticConcatDictOfNumpyArrayResSplittable, OnlyGloballySplittable):
    pass
            
class ElementDistancesStatUnsplittable(Statistic):    
    
    IS_MEMOIZABLE = False

    def _init(self, withOverlaps='no', **kwArgs):
        assert( withOverlaps in ['no','yes'] )
        self._withOverlaps = withOverlaps
    
    def _compute(self):
        tv = self._children[0].getResult()
        if tv._endList is not None:
            dists = tv.startsAsNumpyArray()[1:]-tv.endsAsNumpyArray()[:-1]
        else:
            dists = tv.startsAsNumpyArray()[1:] - tv.startsAsNumpyArray()[:-1]
        
        dists[dists<0] = 0
        return dict([('Result', dists)])
            
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps = (self._withOverlaps == 'yes') ) ) )
