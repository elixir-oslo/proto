from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic


class SingleValExtractorStat(MagicStatFactory):
    pass


class SingleValExtractorStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    
    def _init(self, childClass='', resultKey='',  **kwArgs):
        assert childClass, childClass
        assert resultKey, resultKey
        
        if type(childClass) is str:
            childClass = self.getRawStatisticClass(childClass)
        self._childClass = childClass
        self._resultKey = resultKey
        self._kwArgs = kwArgs
    
    def _createChildren(self):
        self._addChild( self._childClass(self._region, self._track, self._track2, **self._kwArgs) )

    def _compute(self):
        result = self._children[0].getResult()
        return result[self._resultKey]
