from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawOverlapStat import RawOverlapStat
from quick.util.debug import DebugUtil


class DerivedOverlapStat(MagicStatFactory):
    pass

class DerivedOverlapStatUnsplittable(Statistic):
    def _createChildren(self):
        self._addChild( RawOverlapStat(self._region, self._track, self._track2) )
        
    def _compute(self):
        props = {}
        #tp = self._children[0].getResult()["TP"]
        #tn = self._children[0].getResult()["TN"]
        #fp = self._children[0].getResult()["FP"]
        #fn = self._children[0].getResult()["FN"]
        tn,fp,fn,tp = [ self._children[0].getResult()[key] for key in ['Neither','Only1','Only2','Both'] ]
        t1Coverage = tp+fp
        t2Coverage = tp+fn
        binSize = tn+fp+fn+tp
        
        if (fn+tp)>0:
            props["1inside2"] = 1.0*tp/(fn+tp)#1.0*tp/(tp+fp)
        else:
            props["1inside2"] = None #to mark N/A..
        if (fp+tn)>0:
            props["1outside2"] = 1.0*fp/(fp+tn)#1.0*fn/(fn+tn)
        else:
            props["1outside2"] = None
        if (tp+fp)>0:
            props["2inside1"] = 1.0*tp/(tp+fp)#1.0*tp/(fn+tp)
        else:
            props["2inside1"] = None
        if (fn+tn)>0:
            props["2outside1"] = 1.0*fn/(fn+tn)#1.0*fp/(fp+tn)
        else:
            props["2outside1"] = None
        if (fp+fn+tp)>0:
            props['intersectionToUnionRatio'] = 1.0*tp / (fp+fn+tp)
        else:
            props['intersectionToUnionRatio'] = None
            
        if not None in (props["1inside2"] , props["1outside2"]) and props["1outside2"] > 0:
            props["1in2"] = props["1inside2"] / props["1outside2"]
        else:
            props["1in2"] = None
        if not None in (props["2inside1"], props["2outside1"]) and props["2outside1"] > 0:
            props["2in1"] = props["2inside1"] / props["2outside1"]
        else:
            props["2in1"] = None
                
        expOverlap = (t1Coverage/float(binSize)) * t2Coverage
        props['expOverlap'] = expOverlap
        import numpy as np
        props['overlapToExpOverlapRatio'] = (tp / expOverlap) if expOverlap > 0 else np.nan
        
        return props

