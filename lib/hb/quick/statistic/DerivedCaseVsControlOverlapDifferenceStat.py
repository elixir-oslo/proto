from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.RawCaseVsControlOverlapDifferenceStat import RawCaseVsControlOverlapDifferenceStat

class DerivedCaseVsControlOverlapDifferenceStat(MagicStatFactory):
    pass

class DerivedCaseVsControlOverlapDifferenceStatUnsplittable(Statistic):
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)            
    def _compute(self): #Numpy Version..
        res = self._children[0].getResult()
        tnCase,fpCase,fnCase,tpCase,tnControl,fpControl,fnControl,tpControl = [res[x] for x in 'tnCase,fpCase,fnCase,tpCase,tnControl,fpControl,fnControl,tpControl'.split(',')]
        
        controlBpOverlap = tpControl
        controlPropOverlapping = 1.0*tpControl/(tpControl+fpControl) if (tpControl+fpControl)>0 else None
        caseBpOverlap =tpCase
        casePropOverlapping = 1.0*tpCase/(tpCase+fpCase) if (tpCase+fpCase)>0 else None
        caseVsControlPropRatio = (casePropOverlapping / controlPropOverlapping) if controlPropOverlapping>0 else None

        return dict(zip('caseBpOverlap,controlBpOverlap,casePropOverlapping,controlPropOverlapping,caseVsControlPropRatio'.split(','), \
                [caseBpOverlap,controlBpOverlap,casePropOverlapping, controlPropOverlapping, caseVsControlPropRatio]))

        
    def _createChildren(self):
        self._addChild(RawCaseVsControlOverlapDifferenceStat(self._region, self._track, self._track2 ))
