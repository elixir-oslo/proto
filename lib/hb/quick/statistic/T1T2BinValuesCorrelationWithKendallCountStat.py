'''
Created on Mar 1, 2016

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.GenericT1T2BinValuesCorrelationStat import GenericT1T2BinValuesCorrelationStat


class T1T2BinValuesCorrelationWithKendallCountStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class T1T2BinValuesCorrelationWithKendallCountStatSplittable(StatisticSumResSplittable):
#    pass
            
class T1T2BinValuesCorrelationWithKendallCountStatUnsplittable(Statistic):    
    def _compute(self):
        return self._children[0].getResult()
    
    def _createChildren(self):
        self._addChild(GenericT1T2BinValuesCorrelationStat(self._region, self._track, self._track2, perBinStatistic='CountStat', corrMethod='kendall'))
