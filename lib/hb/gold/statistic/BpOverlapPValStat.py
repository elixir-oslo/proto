from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawOverlapStat import RawOverlapStat
from gold.util.CustomExceptions import IncompatibleAssumptionsError
from quick.statistic.CommonStatisticalTests import BinomialTools
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq
from collections import OrderedDict

class BpOverlapPValStat(MagicStatFactory):
    pass

#class BpOverlapPValStatSplittable(StatisticSumResSplittable):
#    pass
            
class BpOverlapPValStatUnsplittable(Statistic):
    MIN_SUCCESSES_FOR_NORM_APPROXIMATION = 5
    MAX_SUCCESSES_FOR_BINOMIAL_RUNTIME = 100

    def __init__(self, region, track, track2, tail='more', **kwArgs):
        assert( tail in ['less','more','different'])
        self._tail = tail
        Statistic.__init__(self, region, track, track2, tail=tail, **kwArgs)

    def _checkAssumptions(self, assumptions):
        if not assumptions == 'bothIndependentBps':
            raise IncompatibleAssumptionsError

    def _compute(self):
        neither,only1,only2,both = [ self._children[0].getResult()[key] for key in ['Neither','Only1','Only2','Both'] ]

        size = neither+only1+only2+both
        prob = (1.0*(only1+both)/size) * (1.0*(only2+both)/size)
        x = both
        
        if both == 0 and (only1 == 0 or only2 == 0):
            pval = None
        elif prob*size >= self.MIN_SUCCESSES_FOR_NORM_APPROXIMATION <= (1-prob)*size:
            from proto.RSetup import r
            mean = size * prob
            sd = (size*prob*(1-prob))**0.5
            lessPval = r.pnorm(x,mean,sd)
            if self._tail=='less':
                pval = lessPval                
            elif self._tail=='more':
                pval = 1 - lessPval
            elif self._tail=='different':
                pval = min(1,2*min( lessPval, 1-lessPval))
        elif x > self.MAX_SUCCESSES_FOR_BINOMIAL_RUNTIME:
            return None
            #raise NotImplementedError()
        else:
            pval = BinomialTools._computeBinomialTail(x, size, prob, self._tail)
        return OrderedDict([('P-value', pval), ('Test statistic: ObsBpOverlap', x), ('E(Test statistic): ExpBpOverlap', prob*size), \
                            ('DiffFromMean', x-prob*size), ('NumBpInBin', size), \
                            ('track1Coverage', (1.0*(only1+both)/size)), ('track2Coverage', (1.0*(only2+both)/size))])
#    return {'P-value':pval, 'ExpBpOverlap':prob*size, 'ObsBpOverlap':x, 'BpsInTrack2Segments':size, 'track1Coverage':(1.0*(only1+both)/all), 'track2Coverage':(1.0*(only2+both)/all)}
    
    def _createChildren(self):
        self._addChild( RawOverlapStat(self._region, self._track, self._track2) )
        self._addChild( FormatSpecStat(self._region, self._track, TrackFormatReq(dense=False, interval=True)) )
        self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True)) )

