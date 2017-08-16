import ast

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import numpy as np

class PwmScoreArrayStat(MagicStatFactory):
    pass

#class PwmScoreArrayStatSplittable(StatisticSumResSplittable):
#    pass
            
class PwmScoreArrayStatUnsplittable(Statistic):
    def _init(self, pfmFileName='', complement='False', **kwArgs):
        assert pfmFileName != ''
        self._pfmFileName = pfmFileName.replace('^','/')
        
        assert complement in ['True', 'False']
        self._complement = ast.literal_eval(complement)

    def _compute(self):
        from Bio.Alphabet import IUPAC
        from Bio.Seq import Seq
        from Bio import Motif
        
        sequence = self._sequenceStat.getResult().valsAsNumpyArray()
        bioSeq = Seq(sequence.tostring(), alphabet=IUPAC.unambiguous_dna)

        thisPwm = Motif.read(open(self._pfmFileName), "jaspar-pfm")
        if self._complement:
            thisPwm = thisPwm.reverse_complement()
            
        try:
            pwmScoreArray = thisPwm.scanPWM(bioSeq)
        except MemoryError, e: #when sequence is shorter than pwm
            return
        
        pwmScoreArray = np.append( pwmScoreArray, np.zeros(len(thisPwm)-1) + np.nan )
        return pwmScoreArray
    
    def _createChildren(self):
        self._sequenceStat = self._addChild(RawDataStat(self._region, self._track, TrackFormatReq(val='char', dense=True, interval=False)) )
