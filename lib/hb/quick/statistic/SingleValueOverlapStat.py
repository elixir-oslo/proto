'''
Created on Jan 21, 2016

@author: boris
'''

from gold.statistic.RawOverlapStat import RawOverlapStat
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.SingleValExtractorStat import SingleValExtractorStat


class SingleValueOverlapStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class SingleValueOverlapStatSplittable(StatisticSumResSplittable):
#    pass
            
class SingleValueOverlapStatUnsplittable(Statistic):    
    def _compute(self):
        return self._children[0].getResult()
    
    def _createChildren(self):
        self._addChild(SingleValExtractorStat(self._region, self._track, self._track2, childClass=RawOverlapStat, resultKey='Both', **self._kwArgs))
