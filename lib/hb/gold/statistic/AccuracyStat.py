import math
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawOverlapStat import RawOverlapStat
from gold.statistic.DerivedOverlapStat import DerivedOverlapStat

class AccuracyStat(MagicStatFactory):
    pass

class AccuracyStatUnsplittable(Statistic):
    def __init__(self, region, track, track2, **kwArgs):
        Statistic.__init__(self, region, track, track2, **kwArgs)

    def _createChildren(self):
        self._addChild( RawOverlapStat(self._region, self._track, self._track2) )
        self._addChild( DerivedOverlapStat(self._region, self._track, self._track2) )
        
    def _compute(self):
        accus = {}
        accus["recall"] = self._children[1].getResult()["1inside2"]
        accus["precision"] = self._children[1].getResult()["2inside1"]
        #tp = self._children[0].getResult()["TP"]
        #tn = self._children[0].getResult()["TN"]
        #fp = self._children[0].getResult()["FP"]
        #fn = self._children[0].getResult()["FN"]
        tn,fp,fn,tp = [ float(self._children[0].getResult()[key]) for key in ['Neither','Only1','Only2','Both'] ]
        
        #tp,tn,fp,fn = [float(x) for x in [tp,tn,fp,fn]]
        
        if 0 in [ (tp + fp) , (tn + fn) , (tp + fn) , (tn + fp)]:
            accus["cc"] = None
        else:
            accus["cc"]= ((tp * tn) - (fp * fn) ) / (math.sqrt(tp + fp)*math.sqrt(tn + fn)*math.sqrt(tp + fn)*math.sqrt(tn + fp))
        accus["hammingDistance"] = fp + fn
        
        return accus


