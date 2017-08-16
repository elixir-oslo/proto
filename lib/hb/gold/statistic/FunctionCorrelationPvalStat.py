from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.BinScaledFunctionAvgStat import BinScaledFunctionAvgStatUnsplittable
from quick.util.CommonFunctions import silenceRWarnings
from gold.util.CustomExceptions import IncompatibleAssumptionsError
from collections import OrderedDict

class FunctionCorrelationPvalStat(MagicStatFactory):
    pass

#class FunctionCorrelationPvalStatSplittable(StatisticSumResSplittable):
#    pass
            
class FunctionCorrelationPvalStatUnsplittable(Statistic):    
    def __init__(self, region, track, track2, numSubBins=10, method='pearson', tail='different', **kwArgs):
        assert method in ['pearson','spearman','kendall']
        assert tail in ['more', 'less', 'different']
        tailMapping = {'more': "greater", 'less': "less", 'different': "two.sided"}

        silenceRWarnings()

        self._numSubBins = numSubBins
        self._method = method
        self._rTail = tailMapping[tail]
        Statistic.__init__(self, region, track, track2, method=method, tail=tail, **kwArgs)
    
    def _checkAssumptions(self, assumptions):
        if not assumptions == 'summarize':
            raise IncompatibleAssumptionsError
    
    def _compute(self):        
        x = self._children[0].getResult()
        y = self._children[1].getResult()
        if len(x)<2 or len(y)<2:
            pval = None
            testStat = None
        else:
            from proto.RSetup import r
            xAsR = r.unlist([float(num) for num in x])
            yAsR = r.unlist([float(num) for num in y])
            #corTestRes = r('cor.test')(xAsR, yAsR, alternative=self._rTail, method=self._method)
            #pval = corTestRes['p.value']            
            #testStat = corTestRes['statistic'].values()[0]

            pval, testStat, correlation = r('function(xAsR, yAsR, alternative,method){res = cor.test(xAsR, yAsR, alternative=alternative,method=method); return(list(res$p.value,res$statistic,res$estimate))}')(xAsR, yAsR, alternative=self._rTail, method=self._method)

            #corTestRes = r('cor.test')(xAsR, yAsR, alternative=self._rTail, method=self._method)
            #pval = corTestRes.rx('p.value')
            #testStat = corTestRes.rx('statistic').rx('t')
        return OrderedDict([ ('P-value', pval), ('Test statistic: ' + self._method, testStat), ('Correlation, '+self._method,correlation)])
    
    def _createChildren(self):
        #self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='number', dense=True)) )
        #self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(val='number', dense=True)) )
        self._addChild( BinScaledFunctionAvgStatUnsplittable(self._region, self._track, numSubBins=self._numSubBins) ) #Use unsplittable stat directly to avoid global computations. Could be improved by making binScaled..Stats have equal resDicts in local and global analysis, instead introducing a separate stat to create the mean and stdDev..
        self._addChild( BinScaledFunctionAvgStatUnsplittable(self._region, self._track2, numSubBins=self._numSubBins) )
