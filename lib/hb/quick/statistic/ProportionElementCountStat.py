'''
Created on Feb 24, 2016

@author: boris
'''

from gold.statistic.CountElementStat import CountElementStat
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import RatioStatUnsplittable
from quick.statistic.BinSizeStat import BinSizeStat


class ProportionElementCountStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class ProportionElementCountStatSplittable(StatisticSumResSplittable):
#    pass
            
class ProportionElementCountStatUnsplittable(RatioStatUnsplittable):    
    
    def _createChildren(self):
        self._addChild( CountElementStat(self._region, self._track, **self._kwArgs) )
        self._addChild( BinSizeStat(self._region, self._track) )
