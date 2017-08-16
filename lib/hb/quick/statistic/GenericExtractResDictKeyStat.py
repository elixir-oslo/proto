#See SingleValExtractorStat..
# GenericExtractResDictKeyStat is a better name, so code should be merged and name changed to start with generic..

#from gold.statistic.MagicStatFactory import MagicStatFactory
#from gold.statistic.Statistic import Statistic
#import re
#
#class GenericExtractResDictKeyStat(MagicStatFactory):
#    pass
#
##class GenericExtractResDictKeyStatSplittable(StatisticSumResSplittable):
##    pass
#            
#class GenericExtractResDictKeyStatUnsplittable(Statistic):
#    def _init(self, rawStatistic=None, resDictKey=None, **kwArgs):
#        self._rawStatistic = self.getRawStatisticClass(rawStatistic)
#        self._resDictKey = resDictKey
#        
#    def _compute(self):
#        resDict = self._children[0].getResult()
#        return resDict.get(self._resDictKey) if (resDict is not None and resDict is not None) else None
#            
#    
#    def _createChildren(self):
#        self._addChild( self._rawStatistic(self._region, self._track, **self._kwArgs) )
