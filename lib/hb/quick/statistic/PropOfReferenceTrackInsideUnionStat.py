'''
Created on Apr 27, 2015

@author: boris
'''


from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawOverlapStat import RawOverlapStat
from gold.statistic.Statistic import Statistic


class PropOfReferenceTrackInsideUnionStat(MagicStatFactory):
    '''
    STAT T2
    
    For tracks t1 (target track) and t2 (reference track) calculate
    bp(t2)/bp(t1 U t2) where bp is the number of basepairs covered.
    '''
    pass

#class PropOfReferenceTrackInsideUnionStatSplittable(StatisticSumResSplittable):
#    pass
            
class PropOfReferenceTrackInsideUnionStatUnsplittable(Statistic):    
    def _compute(self):
        only1,only2,both = [ self._children[0].getResult()[key] for key in ['Only1','Only2','Both'] ]
        if only1 + only2 + both == 0:
            return 0.0
        return float(only2 + both)/(only1 + only2 + both)
    
    
    def _createChildren(self):
        self._addChild(RawOverlapStat(self._region, self._track, self._track2))
