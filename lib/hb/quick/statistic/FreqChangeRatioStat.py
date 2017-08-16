from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.FreqChangeStat import FreqChangeStat

class FreqChangeRatioStat(MagicStatFactory):
    pass

                        
class FreqChangeRatioStatUnsplittable(Statistic):    
    def _compute(self):
        freqs = self._children[0].getResult()
        return 1.0 * freqs[1] / freqs[0]
    
    def _createChildren(self):
        self._addChild( FreqChangeStat(self._region, self._track))
