from math import sqrt
#from proto.RSetup import r

class BinomialTools:
    MIN_SUCCESSES_FOR_NORM_APPROXIMATION = 5
    MAX_SUCCESSES_FOR_BINOMIAL_RUNTIME = 100
    
    @classmethod
    def _computeBinomialTail(cls, x, size, prob, tail):
        from proto.RSetup import r
        x, size, prob = int(x), int(size), float(prob)
        if prob*size >= cls.MIN_SUCCESSES_FOR_NORM_APPROXIMATION <= (1-prob)*size:
            mean = size * prob
            sd = (size*prob*(1-prob))**0.5
            lessPval = r.pnorm(x,mean,sd)
            if tail=='less':
                pval = lessPval                
            elif tail=='more':
                pval = 1 - lessPval
            elif tail=='different':
                pval = min(1, 2*min( lessPval, 1-lessPval))
            else:
                from gold.application.LogSetup import logMessage, logging
                logMessage('Unsupported tail (%s) encountered in _computeBinomialTail.'%tail, level=logging.WARN)
        elif x > cls.MAX_SUCCESSES_FOR_BINOMIAL_RUNTIME:
            return None
            #raise NotImplementedError()
        else:
            if tail=='less':
                pval = r.pbinom(x,size,prob)
            elif tail=='more':
                pval = 1 - r.pbinom(x-1,size,prob)
            elif tail=='different':
                pval = min(1,2*min( r.pbinom(x,size,prob), 1 - r.pbinom(x-1,size,prob)))
        return pval


def pearsonCC(x,y):
    n = len(x)
    assert len(y) == n
    sumx = sum(x)
    sumy = sum(y)
    sumx2 = sum(a**2 for a in x)
    sumy2 = sum(a**2 for a in y)
    sumxy = sum([x[i]*y[i] for i in xrange(n)])
    return (n*sumxy-sumx*sumy)/((n*sumx2-sumx**2)**(0.5)*(n*sumy2-sumy**2)**(0.5))
    
def studentsT_eqSize_eqVar(n, mean1, mean2, var1, var2):
    return ( mean1 - mean2 ) / (sdPooled(var1, var2) * sqrt(2.0/n))

def studentsT_uneqSize_eqVar(n1, n2, mean1, mean2, var1, var2):
    return ( mean1 - mean2 ) / ( sdCommon(n1, n2, var1, var2) * sqrt((1.0/n1) + (1.0/n2)) )

def studentsT_uneqSize_uneqVar(n1, n2, mean1, mean2, var1, var2):
    return ( mean1 - mean2 ) / sdDiff(n1, n2, var1, var2)

def sdPooled(var1, var2):
    return sqrt((var1 + var2) / 2.0)

def sdCommon(n1, n2, var1, var2):
    return sqrt( ((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2) )
    
def sdDiff(n1, n2, var1, var2):
    return sqrt( (var1/n1) + (var2/n2) )
    
def df(n1, n2):
    return n1 + n2 - 2
    
def dfWelchSatterthwaite(n1, n2, var1, var2):
    return ( (var1/n1 + var2/n2)**2 / ((var1/n1)**2/(n1-1) + (var2/n2)**2/(n2-1)) )

def variance(sqSum, nSum, n):
    sqMean = 1.0 * sqSum / n
    mean = 1.0 * nSum / n
    return sqMean - mean**2

def unbiasedVar(sqSum, nSum, n):
    return 1.0 * variance(sqSum, nSum, n) * n / (n-1)
