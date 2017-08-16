#Note: Not yet tested. Should have unit and intTest.
import third_party.stats as stats
import math
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.CountPointStat import CountPointStat
from quick.statistic.CountPointAllowingOverlapStat import CountPointAllowingOverlapStat
from gold.util.CustomExceptions import SplittableStatNotAvailableError
from gold.util.CommonFunctions import isIter
from collections import OrderedDict
from quick.statistic.GenericRelativeToGlobalStat import GenericRelativeToGlobalStatUnsplittable

class DiffRelFreqPValStat(MagicStatFactory):
    resultLabel = 'P-value'
    MIN_POP_FOR_GAUSSIAN_APPROXIMATION = 5
    MIN_SUM_OF_POP_FOR_FISHER_TEST = 5 #Note that this restricts sum of counts inside bins, while Gaussian approximation restricts count per track in bin.
    #cfgGlobalSource = GlobalBinSource(DEFAULT_GENOME)
    
    #@classmethod
    #def minimize(cls, genome):
        #cls.cfgGlobalSource = MinimalBinSource(genome)

class DiffRelFreqPValStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    
    def __init__(self, region, track, track2, tail='more', globalSource='', minimal=False, **kwArgs):
        if isIter(region):
            raise SplittableStatNotAvailableError()
        
        #if minimal == True:
        #    self._globalSource = MinimalBinSource(region.genome)
        #elif globalSource == 'test':
        #    self._globalSource = UserBinSource('TestGenome:chr21:10000000-15000000','1000000')
        #else:
        #    self._globalSource = GlobalBinSource(region.genome)
        self._globalSource = GenericRelativeToGlobalStatUnsplittable.getGlobalSource(globalSource, region.genome, minimal)
        
        assert tail in ['more', 'less', 'different']
        self._tail = tail
        
        super(self.__class__, self).__init__(region, track, track2, tail=tail, globalSource=globalSource, minimal=minimal, **kwArgs)
    
    def _createChildren(self):
        countClass = CountPointAllowingOverlapStat if self._configuredToAllowOverlaps(strict=False) else CountPointStat 
        globCount1 = countClass(self._globalSource , self._track)
        globCount2 = countClass(self._globalSource , self._track2)
        binCount1 = countClass(self._region, self._track)
        binCount2 = countClass(self._region, self._track2)

        self._addChild(globCount1)
        self._addChild(globCount2)
        self._addChild(binCount1)
        self._addChild(binCount2)

    def _compute(self):    
        n1 = self._children[0].getResult()
        n2 = self._children[1].getResult()
        c1 = self._children[2].getResult()
        c2 = self._children[3].getResult()
        #print '*',c1,c2,n1,n2
        
        p = 1.0 * c1 / n1
        q = 1.0 * c2 / n2
        r = 1.0 * (n1*p+n2*q) / (n1+n2)
        
        if c1>=DiffRelFreqPValStat.MIN_POP_FOR_GAUSSIAN_APPROXIMATION \
            and c2>=DiffRelFreqPValStat.MIN_POP_FOR_GAUSSIAN_APPROXIMATION:
            se = math.sqrt( r*(1-r)/n1 + r*(1-r)/n2)
            zScore = (p-q) / se
            if self._tail == 'more':
                pval = 1.0-stats.zprob(zScore)
            elif self._tail == 'less':
                pval = stats.zprob(zScore)
            elif self._tail == 'different':
                #fixme: which of these two solutions are correct?
                #pval = 2.0*(1.0-zprob(abs(zScore)))
                pval = min(1.0, 2.0*min(1.0-stats.zprob(zScore), stats.zprob(zScore)))
        elif c1+c2 >= DiffRelFreqPValStat.MIN_SUM_OF_POP_FOR_FISHER_TEST and self._tail == 'different':
            #import traceback
            #from gold.util.CustomExceptions import ShouldNotOccurError
            #from gold.util.CommonFunctions import getClassName
            #try:
            a = int(c1) #p*n1
            b = int(n1-c1) #n1-a
            c = int(c2) #q*n2
            d = int(n2-c2)# n2-c
            from proto.RSetup import r, robjects
            twoByTwo = r.matrix(robjects.IntVector([a,b,c,d]), nrow=2) 
            res = r('fisher.test')(twoByTwo)
            pval = r('function(x){x$p.value}')(res)
            se = None            
            zScore = '(2x2=%i,%i,%i,%i)' % (a,b,c,d)
            #except Exception,e:
            #    raise ShouldNotOccurError('Repackaged exception.., original was: ' + getClassName(e) + ' - '+str(e) + ' - ' + traceback.format_exc())
        else:
            zScore = pval = se = None
            
        return OrderedDict([ ('P-value', pval), ('Test statistic: Z-score', zScore), ('EstDiff', p-q), \
                            ('SEDiff', se), ('CountTrack1', c1), ('CountTrack2', c2) ])
            
