#Note: Not yet tested. Should have unit and intTest.
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.CountStat import CountStat
from quick.statistic.ProportionCountPerBinAvgStat import ProportionCountPerBinAvgStat
from quick.statistic.GenericRelativeToGlobalStat import GenericRelativeToGlobalStatUnsplittable
from collections import OrderedDict
from quick.statistic.KernelWeightedCountStat import KernelWeightedCountStat
from quick.statistic.CatCoverageNormalizedCountStat import CatCoverageNormalizedCountStat

class DiffRelCoverageStat(MagicStatFactory):
    pass

class DiffRelCoverageStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    
    def _init(self, globalSource='', kernelType='uniform', minimal=False, **kwArgs):
        self._globalSource = GenericRelativeToGlobalStatUnsplittable.getGlobalSource(globalSource, self.getGenome(), minimal)
        self._kernelType = kernelType
                    
    def _createChildren(self):
        #countClass = CountPointAllowingOverlapStat if self._configuredToAllowOverlaps(strict=False) else CountPointStat
        globCount1 = CountStat(self._globalSource , self._track, **self._kwArgs)
        globCount2 = CountStat(self._globalSource , self._track2, **self._kwArgs)

        if self._kernelType == 'uniform':
            binCountClass = CountStat
        elif self._kernelType == 'binSizeNormalized':
            binCountClass = ProportionCountPerBinAvgStat
        elif self._kernelType == 'catCoverageNormalized':
            binCountClass = CatCoverageNormalizedCountStat
        else:
            binCountClass = KernelWeightedCountStat
        binCount1 = binCountClass(self._region, self._track, **self._kwArgs)
        binCount2 = binCountClass (self._region, self._track2, **self._kwArgs)

        self._addChild(globCount1)
        self._addChild(globCount2)
        self._addChild(binCount1)
        self._addChild(binCount2)

    def _compute(self):    
        n1 = self._children[0].getResult()
        n2 = self._children[1].getResult()
        c1 = self._children[2].getResult()
        c2 = self._children[3].getResult()
        
        t1BinProportion = 1.0 * c1 / n1
        t2BinProportion = 1.0 * c2 / n2
        res = (t1BinProportion / t2BinProportion) if t2BinProportion is not None else None
        res = float(res)
        return OrderedDict([('Differential relative coverage',res), ('Global bp coverage of T1',n1), ('Bp coverage of T1 within analysis regions',c1), ('Global bp coverage of T2',n2), ('Bp coverage of T2 within analysis regions',c2)])
