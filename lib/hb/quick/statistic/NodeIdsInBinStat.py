from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class NodeIdsInBinStat(MagicStatFactory):
    pass
            
class NodeIdsInBinStatUnsplittable(Statistic):    
    def _compute(self):
        return list(self._rawDataStat.getResult().idsAsNumpyArray())
            
    def _createChildren(self):
        self._rawDataStat = self._addChild(RawDataStat(self._region, self._track, TrackFormatReq() ) )
