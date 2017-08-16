from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.PwmScoreArrayStat import PwmScoreArrayStat
import numpy as np

class MaxPwmScoreInWindowArrayStat(MagicStatFactory):
    pass

#class MaxPwmScoreInWindowArrayStatSplittable(StatisticSumResSplittable):
#    pass
            
class MaxPwmScoreInWindowArrayStatUnsplittable(Statistic):
    def _init(self, pfmFileName='', **kwArgs):
        assert pfmFileName != ''
        self._pfmFileName = pfmFileName.replace('^','/')
    
    def _compute(self):
        from Bio import Motif

        windowLen = len(Motif.read(open(self._pfmFileName), "jaspar-pfm"))
        pwmScores = self._pwmScoreArrayStat.getResult()
        complementPwmScores = self._complementPwmScoreArrayStat.getResult()
        
        ret = np.zeros((windowLen*2, len(pwmScores)), dtype='float32') + np.float32(np.nan)
        for n in range(0, windowLen):
            ret[2*n,n:] = pwmScores[0:len(pwmScores)-n]
            ret[2*n + 1,n:] = complementPwmScores[0:len(complementPwmScores)-n]
            
        return np.nanmax(ret, axis=0)
    
    def _createChildren(self):
        self._pwmScoreArrayStat = self._addChild(PwmScoreArrayStat(self._region, self._track, \
                                                  complement='False', **self._kwArgs))
        self._complementPwmScoreArrayStat = self._addChild(PwmScoreArrayStat(self._region, self._track, \
                                                            complement='True', **self._kwArgs))
