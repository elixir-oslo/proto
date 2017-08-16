from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic

class XYPairStat(MagicStatFactory):
    pass

class XYPairStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    
    def __init__(self, region, track, track2, statClass1=None, statClass2=None, **kwArgs):
        self._statClass1 = statClass1
        self._statClass2 = statClass2                
        Statistic.__init__(self, region, track, track2, statClass1=statClass1, statClass2=statClass2, **kwArgs)
    
    def _createChildren(self): 
        self._addChild( self._statClass1(self._region, self._track, **self._kwArgs) )
        self._addChild( self._statClass2(self._region, self._track2, **self._kwArgs) )
    
    def _compute(self):
        return [self._children[0].getResult(), self._children[1].getResult()]
    
