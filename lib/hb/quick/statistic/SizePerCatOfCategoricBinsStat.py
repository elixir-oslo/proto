from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticDynamicDictSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class SizePerCatOfCategoricBinsStat(MagicStatFactory):
    '''
    For a given bin, simply returns a dict from category of bin over to size of bin.
    At global level, returns a dict that maps bin categories over to sum of size of all bins having that category.
     '''
    pass

class SizePerCatOfCategoricBinsStatSplittable(StatisticDynamicDictSumResSplittable):
    pass
            
class SizePerCatOfCategoricBinsStatUnsplittable(Statistic):    
    def _compute(self):
        if self._kwArgs.get('minimal')==True:
            return {'Dummy':0}
        else:
            return {self._region.val: len(self._region)}
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=self._configuredToAllowOverlaps(strict=False))) )
        pass
