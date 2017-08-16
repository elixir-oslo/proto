from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.ProportionCountStat import ProportionCountStatUnsplittable

class AssemblyGapCoverageStat(MagicStatFactory):
    pass

class AssemblyGapCoverageStatUnsplittable(ProportionCountStatUnsplittable):
    def _compute(self):
        return {'Assembly_gap_coverage': float(ProportionCountStatUnsplittable._compute(self))}
