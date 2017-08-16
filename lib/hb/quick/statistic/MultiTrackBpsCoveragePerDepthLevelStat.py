'''
Created on Jun 30, 2015

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.MultitrackCoverageDepthStat import MultitrackCoverageDepthStat
from gold.statistic.Statistic import Statistic, StatisticDictSumResSplittable
from collections import OrderedDict


class MultiTrackBpsCoveragePerDepthLevelStat(MagicStatFactory):
    '''
    Returns an ordered dictionary where the key k is the depth level, 
    and the value is the count of base-pairs that are covered by exactly k tracks times k.
    '''
    pass

class MultiTrackBpsCoveragePerDepthLevelStatSplittable(StatisticDictSumResSplittable):
    pass
            
class MultiTrackBpsCoveragePerDepthLevelStatUnsplittable(Statistic):    
    def _compute(self):
        childRes = self._children[0].getResult()
        res = OrderedDict()
        for depthLevel in xrange(1, len(childRes)):
            res[depthLevel-1] = childRes[depthLevel]*depthLevel
        
        return res
    
    def _createChildren(self):
        self._addChild(MultitrackCoverageDepthStat(self._region, self._track, self._track2, **self._kwArgs))
