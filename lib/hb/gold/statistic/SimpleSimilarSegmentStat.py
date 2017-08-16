from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.CountElementStat import CountElementStat
from gold.statistic.SimilarSegmentStat import SimilarSegmentStatUnsplittable

class SimpleSimilarSegmentStat(MagicStatFactory):
    pass

#class SimpleSimilarSegmentStatSplittable(StatisticSumResSplittable):
#    pass
            
class SimpleSimilarSegmentStatUnsplittable(SimilarSegmentStatUnsplittable):    
    def __init__(self, region, track, track2, minRelSimilarity=1, **kwArgs):
        self._minRelSimilarity = float(minRelSimilarity)
        assert( 0 <= self._minRelSimilarity <= 1 )
        
        Statistic.__init__(self, region, track, track2, minRelSimilarity=minRelSimilarity, **kwArgs)
    
    def _compute(self):
        similarCount = SimilarSegmentStatUnsplittable._compute(self)
        
        tr1SegCount = self._children[2].getResult()
        tr2SegCount = self._children[3].getResult()
        
        return 1.0 * similarCount / (tr1SegCount + tr2SegCount)
    
    def _similar(self, s1, s2):
        unionLen = max(s1.end(), s2.end()) - min(s1.start(), s2.start())
        relSimilarities = (1.0*len(s1)/unionLen, 1.0*len(s2)/unionLen )
        return all(similarity > self._minRelSimilarity for similarity in relSimilarities)
    
    def _createChildren(self):
        SimilarSegmentStatUnsplittable._createChildren(self)
        self._addChild( CountElementStat(self._region, self._track))
        self._addChild( CountElementStat(self._region, self._track2))
