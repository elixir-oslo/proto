from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticConcatResSplittable
#from quick.statistic.GlobalGraphStat import GlobalGraphStat
#from quick.statistic.NodeIdsInBinStat import NodeIdsInBinStat
from quick.statistic.NeighborhoodOverlap3dStat import NeighborhoodOverlap3dStat

class NeighborhoodCorrespondenceDistribution3dStat(MagicStatFactory):
    pass

class NeighborhoodCorrespondenceDistribution3dStatSplittable(StatisticConcatResSplittable):
    pass

class NeighborhoodCorrespondenceDistribution3dStatUnsplittable(Statistic):        
    def _compute(self):
        return [self._children[0].getResult()['NeighborOverlapEnrichment']]
    
    def _createChildren(self):
        self._addChild(NeighborhoodOverlap3dStat(self._region, self._track, **self._kwArgs) )
        
