from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.GenericNodeValueStat import GenericNodeValueStat
from gold.statistic.ProportionCountStat import ProportionCountStat
from gold.statistic.GraphStat import GraphStat

class AvgEdgeWeightDifferenceForBinsWithHighCoverageVsAllBinsStat(MagicStatFactory):
    pass

class AvgEdgeWeightDifferenceForBinsWithHighCoverageVsAllBinsStatUnsplittable(Statistic): #LowerEdgeWeightsForBinsWithHighCoverageStatUnsplittable:
    def _compute(self):
        nodeValThreshold = 0.001 #from init..
        nodeValues = self._nodeValueStat.getResult()
        qualifiedNodes = [x for x,val in nodeValues.iteritems() if val>nodeValThreshold]
        fullGraph = self._graphStat.getResult()
        subGraph = fullGraph.getSubGraphFromNodeIdSet(qualifiedNodes)
        return subGraph.getAvgEdgeWeight() - fullGraph.getAvgEdgeWeight() 
            
    def _createChildren(self):
        #self._track: 3D data
        #self._track2: analysis data, segments (e.g. repeats)
        self._graphStat = self._addChild(GraphStat(self._region, self._track) )
        #self._nodeValueStat = self._addChild(NodeCoverageValueStat(self._track, self._track2) )
        self._nodeValueStat = self._addChild(GenericNodeValueStat(self._region, self._track, self._track2, rawStatistic=ProportionCountStat) )
