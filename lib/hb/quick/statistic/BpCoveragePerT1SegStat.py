'''
Created on Feb 15, 2016

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.BpCoveragePerT2SegStat import BpCoveragePerT2SegStat


class BpCoveragePerT1SegStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class BpCoveragePerT1SegStatSplittable(StatisticSumResSplittable):
#    pass
            
class BpCoveragePerT1SegStatUnsplittable(Statistic):    
    def _compute(self):
        return self._children[0].getResult()
    
    def _createChildren(self):
        self._addChild(BpCoveragePerT2SegStat(self._region, self._track2, self._track, **self._kwArgs))
