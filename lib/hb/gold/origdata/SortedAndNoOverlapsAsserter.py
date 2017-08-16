from gold.origdata.GESourceWrapper import GESourceWrapper
from gold.util.CustomExceptions import NotValidGESequence
from copy import copy

class SortedAndNoOverlapsAsserter(GESourceWrapper):
    def __init__(self, geSource):
        GESourceWrapper.__init__(self, geSource)
        self._geIter = None
        self._chrMaxCoords = {}
        
    def __iter__(self):
        if not True in [attrs in self._geSource.getPrefixList() for attrs in ['start', 'end']]:
            return self._geSource.__iter__()    
        else:
            self = copy(self)
            self._chrMaxCoords = {}
            self._geIter = self._geSource.__iter__()
            return self
    
    def next(self):
        nextEl = self._geIter.next()
        nextCoord = nextEl.start if not nextEl.start is None else nextEl.end-1
        if self._chrMaxCoords.get(nextEl.chr) >= nextCoord:
            raise NotValidGESequence('Element at ' + str(nextEl) + \
                                     ' is located before last element seen in same chromosome: ' + \
                                     str(self._chrMaxCoords.get(nextEl.chr)) )
        
        self._chrMaxCoords[nextEl.chr] = nextEl.end-1 if not nextEl.end is None else nextEl.start
        return nextEl
