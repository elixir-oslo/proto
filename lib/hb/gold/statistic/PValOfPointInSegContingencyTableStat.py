##
#from gold.statistic.MagicStatFactory import MagicStatFactory
#from gold.statistic.Statistic import Statistic
#from proto.RSetup import r
#from gold.statistic.CategoryPointCountInSegsMatrixStat import CategoryPointCountInSegsMatrixStat
#from quick.statistic.CategoryPointCountNoOverlapsStat import CategoryPointCountNoOverlapsStat
#
#import numpy
#
#class PValOfPointInSegContingencyTableStat(MagicStatFactory):
#    pass
#
##class PValOfPointInSegContingencyTableStatSplittable(StatisticSumResSplittable):
##    pass
#            
#from gold.util.CommonFunctions import repackageException
#class PValOfPointInSegContingencyTableStatUnsplittable(Statistic):
#    @repackageException(Exception,RuntimeError)
#    def _compute(self):
#        res = self._children[0].getResult()['Result']
#        rowNames = res['Rows']
#        
#        O = numpy.array( res['Matrix'] )
#        S = O.sum(axis=0)
#        
#        N =  self._children[1].getResult()
#        Ntotal = sum( N.values() )
#        
#        pval = numpy.zeros(O.shape, dtype='d')
#        for i in range(O.shape[0]):
#            for j in range(O.shape[1]):
#                #prepare vars for r-call:
#                x = q = O[i][j]
#                m = S[j]
#                n = Ntotal - m
#                k = N[ rowNames[i] ]
#                rawPval = min( r.phyper(q,m,n,k), r.phyper(q,m,n,k,False)+r.dhyper(x,m,n,k) )
#                pval[i][j] = min(rawPval*2, 1) #correct for two-tail..
#        
#        return pval
#        
#    
#    def _createChildren(self):
#        #kwArgs = copy(self._kwArgs)
#        self._addChild( CategoryPointCountInSegsMatrixStat(self._region, self._track, self._track2, **self._kwArgs) )
#        self._addChild( CategoryPointCountNoOverlapsStat(self._region, self._track) )
