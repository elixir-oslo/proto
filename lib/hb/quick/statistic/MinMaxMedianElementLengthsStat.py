'''
Created on Feb 24, 2016

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.ElementLengthsStat import ElementLengthsStat
from quick.statistic.MinMaxMedianSegmentLengthsStat import MinMaxMedianSegmentLengthsStatUnsplittable


class MinMaxMedianElementLengthsStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class MinMaxMedianElementLengthsStatSplittable(StatisticSumResSplittable):
#    pass
            
class MinMaxMedianElementLengthsStatUnsplittable(MinMaxMedianSegmentLengthsStatUnsplittable):    
    
    def _createChildren(self):
        self._addChild( ElementLengthsStat(self._region, self._track, withOverlaps=self._withOverlaps) )
