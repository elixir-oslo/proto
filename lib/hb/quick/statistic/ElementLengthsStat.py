from gold.statistic.Statistic import OnlyGloballySplittable,\
    StatisticConcatDictOfNumpyArrayResSplittable
'''
Created on Feb 24, 2016

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.SegmentLengthsStat import SegmentLengthsStatUnsplittable
from gold.track.TrackFormat import TrackFormatReq


class ElementLengthsStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

class ElementLengthsStatSplittable(StatisticConcatDictOfNumpyArrayResSplittable, OnlyGloballySplittable):
    IS_MEMOIZABLE = False
            
class ElementLengthsStatUnsplittable(SegmentLengthsStatUnsplittable):    
    IS_MEMOIZABLE = False
    
    def _compute(self):
        tv = self._children[0].getResult()
        import numpy
        res = tv.endsAsNumpyArray() - tv.startsAsNumpyArray() if tv._endList is not None else numpy.ones(len(tv._startList))
        return dict([('Result', res)])
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps = (self._withOverlaps == 'yes') ) ) )
