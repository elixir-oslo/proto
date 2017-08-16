from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic

class ListCollapserStat(MagicStatFactory):
    pass
        
class ListCollapserStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    
    def __init__(self, region, track, track2, childClass, collapseFunc, **kwArgs):
        Statistic.__init__(self, region, track, track2, childClass=childClass, collapseFunc=collapseFunc, **kwArgs)
        self._childClass = childClass
        self._collapseFunc = collapseFunc
        self._kwArgs = kwArgs
        
    def _createChildren(self):
        self._addChild(self._childClass(self._region, self._track, self._track2, **self._kwArgs) )

    def _compute(self):
        res = self._children[0].getResult()
        if isinstance(res, dict):
            res = res['Result']
        assert(isinstance(res, list))
        return self._collapseFunc(res)

