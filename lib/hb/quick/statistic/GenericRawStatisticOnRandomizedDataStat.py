from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.RandomizedTrackStat import RandomizedTrackStatUnsplittable

class GenericRawStatisticOnRandomizedDataStat(MagicStatFactory):
    pass

class GenericRawStatisticOnRandomizedDataStatUnsplittable(RandomizedTrackStatUnsplittable):
    def _init(self, rawStatistic=None, randTrackClass=None, **kwArgs):
        self._rawStatistic = self.getRawStatisticClass(rawStatistic)
        self._randTrackClass = self.getRandTrackClass(randTrackClass)
        
    def _createChildren(self):
        self._addChild( self._createRandomizedStat(self._rawStatistic, 0) )

    def _compute(self):
        return self._children[0].getResult()
