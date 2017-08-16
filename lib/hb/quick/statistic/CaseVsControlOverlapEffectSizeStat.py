from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.RawCaseVsControlOverlapDifferenceStat import RawCaseVsControlOverlapDifferenceStat
from collections import OrderedDict

class CaseVsControlOverlapEffectSizeStat(MagicStatFactory):
    '''
    Computes varied measures related to effect size of preferential coverage of T1 case vs T1 control segments against segments of T2.
    Normalized diff: (X/n)/(n2/g) - (Y/m)/(n2/g) = (X/n - Y/m)*(g/n2)
    Ratio: [ (X/n)/(n2/g) ]/[ (Y/m) / (n2/g) ] = Xm/Yn
    where X is overlap T2 vs case T1, Y is overlap T2 vs control T1, n is coverage case T1, m is coverage control T1, g is binsize, and n2 is coverage T2
    '''
    pass

#class CaseVsControlOverlapEffectSizeStatSplittable(StatisticSumResSplittable):
#    pass

class CaseVsControlOverlapEffectSizeStatUnsplittable(Statistic):

    from gold.util.CommonFunctions import repackageException
    from gold.util.CustomExceptions import ShouldNotOccurError
    @repackageException(Exception, ShouldNotOccurError)
    def _compute(self):
        rawCaseControlOverlap = self._children[0].getResult()
        X = rawCaseControlOverlap['tpCase']
        Y = rawCaseControlOverlap['tpControl']
        n = rawCaseControlOverlap['tpCase'] + rawCaseControlOverlap['fpCase']
        m = rawCaseControlOverlap['tpControl'] + rawCaseControlOverlap['fpControl']
        g = rawCaseControlOverlap['tpCase'] + rawCaseControlOverlap['fpCase'] + rawCaseControlOverlap['fnCase'] + rawCaseControlOverlap['tnCase']
        n2 = rawCaseControlOverlap['tpCase'] + rawCaseControlOverlap['fnCase']

        fX = rawCaseControlOverlap['fpCase']
        fY = rawCaseControlOverlap['fpControl']
        labels = ['Ratio of case vs control',
                  'Normalized difference between case and control',
                  'Proportion of T1 case segments covered by T2 segments',
                  'Proportion of T1 control segments covered by T2 segments',
                  'Proportion of analysis region covered by T2 segments',
                  'Proportion of all T1 coverage being case',
                  'Proportion of T1 coverage inside T2 being marked as case',
                  'Proportion of T1 coverage outside T2 being marked as case',
                  'Overlap between case T1 segments and T2',
                  'Overlap between control T1 segments and T2',
                  'Expected overlap between random T1 case segments and T2'
                  'Coverage by case T1 segments',
                  'Coverage by control T1 segments',
                  'Coverage by T2 segments']

        if (n==0 or m==0 or (Y*n)==0 or n2==0):
            return OrderedDict(zip(labels, [None]*5 + [n, m, n2]))
        else:
            ratio = float(X*m) / (Y*n)
            diff = (float(X)/n - float(Y)/m)*(float(g)/n2)
#            return OrderedDict(zip(labels,[ratio, diff, float(X)/n, float(Y)/m , float(n2)/g, float(X+fX)/(X+fX+Y+fY), float(X)/(X+Y),float(fX)/(fX+fY), n, m, n2]))
            return OrderedDict(zip(labels,[ratio, diff, float(X)/n, float(Y)/m , float(n2)/g, float(n)/(n+m), float(X)/(X+Y), float(fX)/(fX+fY), X, Y, float(X+Y)*n/(n+m), n, m, n2]))

    def _createChildren(self):
        self._addChild(RawCaseVsControlOverlapDifferenceStat(self._region, self._track, self._track2 ))
