from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawOverlapStat import RawOverlapStat

class SimpleExpectedBpOverlapStat(MagicStatFactory):
    pass
            
class SimpleExpectedBpOverlapStatUnsplittable(Statistic):
    def _compute(self):
        neither,only1,only2,both = [ self._children[0].getResult()[key] for key in ['Neither','Only1','Only2','Both'] ]

        size = neither+only1+only2+both
        prob = (1.0*(only1+both)/size) * (1.0*(only2+both)/size)
        return prob*size
    
    def _createChildren(self):
        self._addChild( RawOverlapStat(self._region, self._track, self._track2) )

