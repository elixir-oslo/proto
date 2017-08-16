from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.BinScaledSegCoverageStat import *

class BinScaledPointCoverageStat(MagicStatFactory):
    pass

class BinScaledPointCoverageStatSplittable(BinScaledSegCoverageStatSplittable):
    pass
            
class BinScaledPointCoverageStatUnsplittable(BinScaledSegCoverageStatUnsplittable):    
    def _createChildren(self):
        self._addChild( BinSizeStat(self._region, self._track))
        #allowOverlaps = (self._kwArgs.get('allowOverlaps') in [True,'True','true']) #Will be false if set to false, but also if missing..
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False, allowOverlaps=self._configuredToAllowOverlaps())) )
