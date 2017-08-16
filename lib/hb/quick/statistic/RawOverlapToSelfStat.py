from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticDictSumResSplittable
from quick.statistic.BinSizeStat import BinSizeStat
from collections import OrderedDict
from gold.statistic.CountStat import CountStat

class RawOverlapToSelfStat(MagicStatFactory):
    '''
    To mimic raw overlap of same track.
    '''
    pass

class RawOverlapToSelfStatSplittable(StatisticDictSumResSplittable):
    pass

class RawOverlapToSelfStatUnsplittable(Statistic):

    def _compute(self): #Numpy Version..

        tp = self._children[0].getResult()
        binSize = self._binSizeStat.getResult()
        tn = binSize - tp

        return OrderedDict(zip(['Neither','Only1','Only2','Both'] , (tn,0,0,tp)))



    def _createChildren(self):
        self._addChild( CountStat(self._region, self._track) )
        self._binSizeStat = self._addChild( BinSizeStat(self._region, self._track))
