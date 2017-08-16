from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.DerivedOverlapStat import DerivedOverlapStat

class OverlapEnrichmentBasedDistanceStat(MagicStatFactory):
    pass

class OverlapEnrichmentBasedDistanceStatUnsplittable(Statistic):
    def _createChildren(self):
        self._addChild( DerivedOverlapStat(self._region, self._track, self._track2) )
        
    def _compute(self):
        derivedOverlap = self._children[0].getResult()
        try:
            averagedEnrichment = (derivedOverlap['1in2'] + derivedOverlap['2in1']) / 2.0
        except: #if None returned from derivedOverlap
            return 1.0
        
        return 1.0/(1 + averagedEnrichment)
