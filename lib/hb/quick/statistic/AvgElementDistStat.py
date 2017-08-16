'''
Created on Feb 24, 2016

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.AvgSegDistStat import AvgSegDistStatUnsplittable
from quick.statistic.ElementDistancesStat import ElementDistancesStat


class AvgElementDistStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class AvgElementDistStatSplittable(StatisticSumResSplittable):
#    pass
            
class AvgElementDistStatUnsplittable(AvgSegDistStatUnsplittable):    

    def _createChildren(self):
        self._addChild( ElementDistancesStat(self._region, self._track) )
