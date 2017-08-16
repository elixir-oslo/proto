from gold.extra.nmers.NmerTools import NmerTools

class NmerAsIntSlidingWindow:
    def __init__(self, n, bpIter):
        self._n = n
        self._bpIter = bpIter
        
    def __iter__(self):
        bps = 'acgtACGT'
        nmer2int = dict( zip(bps, [NmerTools.nmerAsInt(bp.lower()) for bp in bps]) )
        
        numBps = 0
        validBps = 0
        curNmerAsInt = 0
        for bp in self._bpIter:
            numBps += 1
            if bp in bps:
                validBps += 1
                curNmerAsInt = (curNmerAsInt % 4**(self._n-1)) * 4 + nmer2int[bp]
            else:
                validBps = 0
                curNmerAsInt = 0
            
            if validBps >= self._n:
                yield curNmerAsInt
            elif numBps >= self._n:
                yield None #menas not valid value
            #else we are filling up window from start of sequence..
