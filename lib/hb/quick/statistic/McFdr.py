import numpy
from gold.util.CommonFunctions import mean
from config.Config import IS_EXPERIMENTAL_INSTALLATION

class McFdr:
    MIN_NUM_TESTS_FOR_PI0_ESTIMATION = 100
    
    @staticmethod
    def _initMcFdr():
        from proto.RSetup import r
        r('library(pi0)') 
        r('histf1SeqPerm <- function(p) {histf1(p,seq.perm=TRUE)}')

    #@staticmethod
    #def adjustPvalues(pvals, estimationMethod='Pounds&Cheng'):
    #    from proto.RSetup import r
    #    allPvals = numpy.array([x if x is not None else numpy.nan for x in pvals])
    #    notNoneIndicator = numpy.isnan(allPvals)==False
    #    if not notNoneIndicator.any():
    #        return list(allPvals)
    #
    #    notNonePvals = allPvals[notNoneIndicator]
    #
    #    if estimationMethod:
    #        if estimationMethod == 'Convest':
    #            pi0 = r.convest(notNonePvals)
    #        elif estimationMethod == 'Histf1':
    #            #r('histf1SeqPerm <- function(p) {histf1(p,seq.perm=TRUE)}')
    #            #pi0 = r.histf1SeqPerm(pvals)
    #            pi0 = r.histf1(notNonePvals)
    #        elif estimationMethod == 'Pounds&Cheng':                
    #            pi0 = min(1.0, notNonePvals.mean(dtype='float64')*2.0)                
    #        else:
    #            raise Exception('Invalid estimationMethod: ' + str(estimationMethod))
    #
    #    notNonefdrVals = r.fdr(notNonePvals, pi0)
    #    if not type(notNonefdrVals) in (list,tuple):
    #        notNonefdrVals = [fdrVals]
    #    
    #    fdrVals = numpy.zeros(len(pvals))
    #    fdrVals[:]=numpy.nan
    #    
    #    assert notNoneIndicator.sum(dtype='float64') == len(notNonefdrVals)
    #    fdrVals[notNoneIndicator] = notNonefdrVals
    #    
    #    return list(fdrVals)

    @classmethod
    def adjustPvalues(cls, pvals, estimationMethod='Pounds&Cheng', verbose=True):
        #from sys import stderr
        #stderr.write('McFdr.adjustPvalues starting')
        from proto.RSetup import r
        
        pvals = [x if x is not None else numpy.nan for x in pvals]
        
        #notNoneIndices = [i for i in range(len(pvals)) if pvals[i] is not None]
        #notNonePvals =
        #print 'PVALS: ',pvals
        nonNanPvals = [p for p in pvals if not numpy.isnan(p)]
        if len(nonNanPvals)==0:
            #stderr.write('McFdr.adjustPvalues ending early.')
            return pvals #either empty or only nan-values..
            
        if len(nonNanPvals)<cls.MIN_NUM_TESTS_FOR_PI0_ESTIMATION:
            pi0 = 1.0
        else:
            if estimationMethod == 'Convest':
                pi0 = r.convest(pvals)
            elif estimationMethod == 'Histf1':
                pi0 = r.histf1(pvals)
            elif estimationMethod == 'Pounds&Cheng':                
                pi0 = min(1.0, mean( nonNanPvals )*2.0)                
                #r('histf1SeqPerm <- function(p) {histf1(p,seq.perm=TRUE)}')
                #pi0 = r.histf1SeqPerm(pvals)
            else:
                raise Exception('Invalid estimationMethod: ' + str(estimationMethod))

        if IS_EXPERIMENTAL_INSTALLATION and verbose:
            print 'Estimated pi0: ',pi0

        #fdrVals = r.fdr(pvals, pi0)
        nonNanFdrVals = r('fdrFunc <- function(pv,pi0){ vec1 <- unlist(pv); fdr(vec1,pi0)}')(nonNanPvals,pi0)
        #r('fdrFunc <- function(pv,pi0){ vec1 <- unlist(pv); vec1}')(pvals,pi0)
        
        if len(nonNanPvals)==1:
            nonNanFdrVals  = [nonNanFdrVals]
        #if not type(fdrVals) in (list,tuple):
            #print 'type(fdrVals): ',type(fdrVals)
            #fdrVals = [fdrVals]

        if len(nonNanPvals) != len(pvals):            
            nonNanFdrVals = numpy.array(list(nonNanFdrVals)) #from R vector to python list to numpy array (to avoid numpy being confused by direct conversion from rpy.FloatVector)
            nonNanPvalIndicator = (numpy.isnan(pvals)==False)
            fdrVals = numpy.zeros( len(pvals))
            fdrVals[:] = numpy.NaN
            assert sum(nonNanPvalIndicator) == len(nonNanFdrVals)
            #print repr(nonNanPvalIndicator), repr(nonNanFdrVals)
            #print 'Types: ', nonNanPvalIndicator.dtype, nonNanFdrVals.dtype
            fdrVals[nonNanPvalIndicator] = nonNanFdrVals
            fdrVals = list(fdrVals) #back to python list
        else:
            fdrVals = nonNanFdrVals
        #stderr.write('McFdr.adjustPvalues ending')
        return fdrVals
    
    @classmethod
    def dummyStub(cls, stats):
        from gold.util.RandomUtil import random
        for stat in stats:
            if not hasattr(stat,'det'):
                stat.det = False
                
            x = random.uniform(0,1000) 
            if stat._numResamplings > x:
                stat.det = True
            elif stat.det == False:
                stat._numResamplings+=100
                del stat._result
        print 'ALL: ',all([x.det for x in stats])
        return all([x.det for x in stats])
