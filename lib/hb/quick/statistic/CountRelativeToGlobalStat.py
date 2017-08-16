from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.CountPointStat import CountPointStat
from gold.util.CustomExceptions import SplittableStatNotAvailableError
from quick.application.UserBinSource import GlobalBinSource, MinimalBinSource, UserBinSource
from gold.util.CommonFunctions import isIter

class CountRelativeToGlobalStat(MagicStatFactory):
    pass

class CountRelativeToGlobalStatUnsplittable(Statistic):
#    IS_MEMOIZABLE = False
    
    def __init__(self, region, track, track2, globalSource='', minimal=False, **kwArgs):
        if isIter(region):
            raise SplittableStatNotAvailableError()

        if minimal == True:
            self._globalSource = MinimalBinSource(region.genome)
        elif globalSource == 'test':
            self._globalSource = UserBinSource('TestGenome:chr21:10000000-15000000','1000000')
        else:
            self._globalSource = GlobalBinSource(region.genome)
        
        super(self.__class__, self).__init__(region, track, track2, globalSource=globalSource, minimal=minimal, **kwArgs)
    
    def _createChildren(self):
        globCount1 = CountPointStat(self._globalSource , self._track)
        binCount1 = CountPointStat(self._region, self._track)

        self._addChild(globCount1)
        self._addChild(binCount1)

    def _compute(self):    
        n1 = self._children[0].getResult()
        c1 = self._children[1].getResult()
        #print '*',c1,c2,n1,n2
        
        return 1.0*c1/n1
            
