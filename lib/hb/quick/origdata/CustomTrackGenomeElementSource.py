from copy import copy
from gold.origdata.GenomeElementSource import GenomeElementSource
#import math #in case of use by func expressions
#from rpy import r
#cachedDNorm = dict( zip(range(-5001,5001), [r.dnorm(x,0,2000) for x in range(-5001,5001)]) )

class CustomTrackGenomeElementSource(GenomeElementSource):
    _hasOrigFile = False
    
    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)
        
    def __init__(self, windowSource, genome, trackName, chr, func):
        GenomeElementSource.__init__(self, None, genome=genome, trackName=trackName)
        self._windowSource = windowSource
        self._windowIter = None
        self._genomeElement.chr = chr
        self._func = func

    def __iter__(self):
        self = copy(self)
        self._windowIter = self._windowSource.__iter__()
        return self
        
    def next(self):
        nextEl = self._windowIter.next()
        #print 'ONLY EL',nextEl
        self._genomeElement.val = self._func(nextEl)
        #print 'El and val: ', nextEl,[x.end if x is not None else '-' for x in nextEl],' and ', self._genomeElement.val
        return self._genomeElement

    def getNumElements(self):
        return len(self._windowSource)
        
    def getPrefixList(self):
        return ['val']
    
    def getValDataType(self):
        return 'float64'
