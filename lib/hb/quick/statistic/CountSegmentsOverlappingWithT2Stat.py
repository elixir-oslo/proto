from quick.statistic.BpCoveragePerT1SegStat import BpCoveragePerT1SegStat
'''
Created on Feb 15, 2016

@author: boris
'''


from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic


class CountSegmentsOverlappingWithT2Stat(MagicStatFactory):
    '''
    Count the number of segments in track 1 that are covered by at least 1 bp from track 2.
    '''
    pass

#class CountSegmentsOverlappingWithT2StatSplittable(StatisticSumResSplittable):
#    pass
            
class CountSegmentsOverlappingWithT2StatUnsplittable(Statistic):    
    def _compute(self):
        return sum(self._children[0].getResult() > 0)
    
    def _createChildren(self):
        self._addChild(BpCoveragePerT1SegStat(self._region, self._track, self._track2, **self._kwArgs))
