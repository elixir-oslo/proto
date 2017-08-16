from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic

class GenericFactorsAgainstReferenceResDictKeyStat(MagicStatFactory):
    pass

#class GenericFactorsAgainstReferenceResDictKeyStatSplittable(StatisticSumResSplittable):
#    pass
            
class GenericFactorsAgainstReferenceResDictKeyStatUnsplittable(Statistic):    
    def _init(self, rawStatistic=None, referenceResDictKey='Result', **kwArgs):
        self._referenceResDictKey = referenceResDictKey
        self._rawStatistic = self.getRawStatisticClass(rawStatistic)
        
    def _compute(self):
        rawNumbers = self._children[0].getResult()
        referenceNumber = float(rawNumbers[self._referenceResDictKey])
        return dict([(key,val/referenceNumber) for key,val in rawNumbers.items()])
    
    def _createChildren(self):
        self._addChild( self._rawStatistic(self._region, self._track, self._track2, **self._kwArgs))
