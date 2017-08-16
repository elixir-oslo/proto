#UNTESTED
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.util.CustomExceptions import ShouldNotOccurError
from copy import copy

class ZipperStat(MagicStatFactory):
    pass

class ZipperStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    
    def __init__(self, region, track, track2, statClassList=None, **kwArgs):
        Statistic.__init__(self, region, track, track2, statClassList=statClassList, **kwArgs)
        #self._kwArgs = kwArgs
        if type(statClassList) == list:
            self._statClassList = statClassList
        elif isinstance(statClassList, basestring):
            from gold.statistic.AllStatistics import STAT_CLASS_DICT
            self._statClassList = [STAT_CLASS_DICT[x] for x in \
                statClassList.replace(' ','').replace('^','|').split('|')]
        else:
            raise ShouldNotOccurError
    
    def _createChildren(self):
        kwArgs = copy(self._kwArgs)
        if 'statClassList' in kwArgs:
            del kwArgs['statClassList']
        for statClass in self._statClassList:
            self._addChild( statClass(self._region, self._track, (self._track2 if hasattr(self, '_track2') else None), **kwArgs) )
            
    def _compute(self):
        return [child.getResult() for child in self._children]
    
