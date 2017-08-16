from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.NearestPointDistsStat import NearestPointDistsStatUnsplittable
from gold.statistic.NearestPointMarkDiffStat import NearestPointMarkDiffStatUnsplittable
from quick.statistic.CommonStatisticalTests import pearsonCC

class CorrespondingPointMarkCCStat(MagicStatFactory):
    pass

#class CorrespondingPointMarkCCStatSplittable(StatisticSumResSplittable):
#    pass
            
class CorrespondingPointMarkCCStatUnsplittable(NearestPointMarkDiffStatUnsplittable):    
    def _compute(self):
        pairs = [x for x in NearestPointDistsStatUnsplittable._compute(self) if x is not None]
        if len(pairs) == 0:
            return None
        else:
            return pearsonCC( *zip( pairs ) )


    @staticmethod
    def _getObservator(p1, p2):
        return (p1.val(), p2.val()) if (p2 != None and p1.start() == p2.start()) else None
    
