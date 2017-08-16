from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.util.CommonFunctions import getClassName

class GenericResultsCombinerStat(MagicStatFactory):
    pass

#class GenericResultsCombinerStatSplittable(StatisticSumResSplittable):
#    pass
            
class GenericResultsCombinerStatUnsplittable(Statistic):
    def _init(self, rawStatistics=[], **kwArgs):
        if isinstance(rawStatistics, basestring):
            from gold.statistic.AllStatistics import STAT_CLASS_DICT
            
            rawStatistics = [STAT_CLASS_DICT[rawStat] for rawStat in rawStatistics.split('^')]
        self._rawStatistics = rawStatistics
        
        if not hasattr(self, '_track2'):
            self._track2 = None #to allow track2 to be passed on as None to rawStatistics without error. For use by single-track statistics
        
    def _compute(self):
        from collections import OrderedDict
        #res = {}
        res = OrderedDict()
        for childStat in self._children:
            childRes = childStat.getResult()
            #print '1',str(self._region), str(childRes)
            if not isinstance(childRes, dict):
                childRes = {getClassName(childStat).replace('Unsplittable','').replace('Splittable',''):childRes}
            #print '2',str(self._region), str(childRes)
            for key in childRes:
                assert not key in res
                res[key] = childRes[key]
            #print '3',str(self._region), str(res)
            #res.update(  childRes)
        return res
    
    def _createChildren(self):
        for rawStat in self._rawStatistics:
            self._addChild( rawStat(self._region, self._track, self._track2, **self._kwArgs) )
