'''
Created on Feb 24, 2016

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.AvgSegLenStat import AvgSegLenStatUnsplittable
from quick.statistic.ElementLengthsStat import ElementLengthsStat


class AvgElementLengthStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class AvgElementLengthStatSplittable(StatisticSumResSplittable):
#    pass
            
class AvgElementLengthStatUnsplittable(AvgSegLenStatUnsplittable):    

    def _createChildren(self):
        self._addChild( ElementLengthsStat(self._region, self._track, withOverlaps=self._withOverlaps) )
