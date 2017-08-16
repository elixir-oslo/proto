from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.CountPointStat import CountPointStat
from quick.statistic.PointCountInsideSegsStat import PointCountInsideSegsStat
from gold.statistic.ProportionCountStat import ProportionCountStat
#from proto.RSetup import r
import math
from collections import OrderedDict

class PointCountInSegsPvalStat(MagicStatFactory):
    pass

#class PointCountInSegsPvalStatSplittable(StatisticSumResSplittable):
#    pass
            
class PointCountInSegsPvalStatUnsplittable(Statistic):
    def __init__(self, region, track, track2, assumptions='poissonPoints', tail='different', **kwArgs):
        assert( tail in ['less','more','different'])
        assert assumptions=='poissonPoints'
        
        self._tail = tail
        Statistic.__init__(self, region, track, track2, assumptions=assumptions, tail=tail, **kwArgs)
    
    def _compute(self):
        from proto.RSetup import r
        #r("require(Defaults)")
        #r('setDefaults(q, save="no")')
        #r("useDefaults(q)")

        x = self._numPointsInside.getResult() 
        size = self._numPointsTotal.getResult()
        prob = self._segmentCoverProportion.getResult()
        se = math.sqrt(1.0*(prob)*(1-prob)/size)
        if size < 1 or prob in [0,1]:
            return None
        if self._tail=='less':
            pval = r.pbinom(x,size,prob)
        elif self._tail=='more':
            pval = 1 - r.pbinom(x-1,size,prob)
        elif self._tail=='different':
            pval = min(1, 2*min( r.pbinom(x,size,prob), 1 - r.pbinom(x-1,size,prob)))
            
        #return {'P-value':pval, 'SegCover':prob, 'PointsInside':x, 'PointsTotal':size}
        return OrderedDict([ ('P-value', float(pval)), ('Test statistic: PointsInside', x), ('E(Test statistic): ExpPointsInside', prob*size), \
                             ('DiffFromExpected', x-prob*size), ('PointsTotal', size), ('SegCoverage', prob) ])
    
    def _createChildren(self):
        self._numPointsInside = self._addChild( PointCountInsideSegsStat(self._region, self._track, self._track2))
        self._numPointsTotal = self._addChild( CountPointStat(self._region, self._track))
        self._segmentCoverProportion = self._addChild( ProportionCountStat(self._region, self._track2))
