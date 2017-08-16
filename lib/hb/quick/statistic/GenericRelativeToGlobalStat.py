from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.util.CommonFunctions import isIter
from gold.util.CustomExceptions import SplittableStatNotAvailableError, ShouldNotOccurError
from quick.application.UserBinSource import MinimalBinSource, UserBinSource
from quick.util.GenomeInfo import GenomeInfo


class GenericRelativeToGlobalStat(MagicStatFactory):
    pass

class GenericRelativeToGlobalStatUnsplittable(Statistic):
#    IS_MEMOIZABLE = False
    
    def _init(self, rawStatistic=None, globalSource='', minimal=False, **kwArgs):
        if isIter(self._region):
            raise SplittableStatNotAvailableError()

        self._rawStatistic = self.getRawStatisticClass(rawStatistic)
        self._globalSource = GenericRelativeToGlobalStatUnsplittable.getGlobalSource(globalSource, self._region.genome, minimal)        
            
    @staticmethod
    def getGlobalSource(globalSourceStr, genome, minimal):
        if minimal == True:
            return MinimalBinSource(genome)
        elif globalSourceStr == 'test':
            return UserBinSource('TestGenome:chr21:10000000-15000000','1000000')
        elif globalSourceStr == 'chrs':
            return GenomeInfo.getChrRegs(genome)
        elif globalSourceStr == 'chrarms':
            return GenomeInfo.getChrArmRegs(genome)
        elif globalSourceStr == 'ensembl':
            return GenomeInfo.getStdGeneRegs(genome)
        elif globalSourceStr == 'userbins':
            from gold.application.StatRunner import StatJob
            assert StatJob.USER_BIN_SOURCE is not None
            return StatJob.USER_BIN_SOURCE
            #return kwArgs['userBins']
        else:
            raise ShouldNotOccurError('globalSource not recognized')
            #return GlobalBinSource(genome)
        
    def _createChildren(self):
        globCount1 = self._rawStatistic(self._globalSource , self._track)
        binCount1 = self._rawStatistic(self._region, self._track)

        self._addChild(globCount1)
        self._addChild(binCount1)

    def _compute(self):    
        n1 = self._children[0].getResult()
        c1 = self._children[1].getResult()
        #print '*',c1,c2,n1,n2
        
        return 1.0*c1/n1
            
