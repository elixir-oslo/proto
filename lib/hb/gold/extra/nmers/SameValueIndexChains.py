from numpy import memmap, zeros
from quick.util.CommonFunctions import ensurePathExists
#from stat import S_IRWXU, S_IRWXG, S_IRXO

import os

class SameValueIndexChainsFactory(object):
    CHAIN_LIST_SUFFIX = '.chains'
    START_LIST_SUFFIX = '.starts'
    
    @classmethod
    def load(cls, path, fnPrefix):
        fns = cls._getFileNames(path, fnPrefix)
        assert all(os.path.exists(fn) for fn in fns), str(fns)
        return SameValueIndexChains(*[memmap(fn, 'int32', 'r') for fn in fns])
    
    @classmethod
    def generate(cls, valIter, valIterLen, maxValue, path, fnPrefix):
        "Assumes valIter gives values between 0 and maxValue"
        assert valIterLen > 0
        chainsFn, startsFn = cls._getFileNames(path, fnPrefix)
        ensurePathExists(chainsFn)
        chains = memmap(chainsFn, 'int32', 'w+', shape=valIterLen)
        starts = memmap(startsFn, 'int32', 'w+', shape=maxValue)
        curPositions = zeros(maxValue, 'int32') - 1
        starts[:] = curPositions
        #os.chmod(chainsFn, S_IRWXU|S_IRWXG|S_IRXO)
        #os.chmod(startsFn, S_IRWXU|S_IRWXG|S_IRXO)
                
        valIterIndex = 0
        for val in valIter:
            if val == None:
                pass
            elif curPositions[val] < 0:
                starts[val] = curPositions[val] = valIterIndex
            else:
                chains[ curPositions[val] ] = valIterIndex
                curPositions[val] = valIterIndex
            valIterIndex += 1
            if valIterIndex%10e6==0:
                print '.',
        #for index in curPositions:
        #    if index >= 0:
        #        chains[ index ] = -1
        chains[ curPositions[curPositions >= 0] ] = -1
        chains.flush()
        starts.flush()
        return SameValueIndexChains(chains, starts)
    
    @classmethod
    def _getFileNames(cls, path, fnPrefix):
        return [ path + os.sep + fnPrefix + suffix for suffix in [cls.CHAIN_LIST_SUFFIX, cls.START_LIST_SUFFIX] ]
        
class SameValueIndexChains(object):
    def __init__(self, chainList, startList):
        self._chainList = chainList
        self._startList = startList
    
    def getIndexGenerator(self, val):
        return SameValueIndexGenerator(self, val)
        
class SameValueIndexGenerator(object):
    def __init__(self, indexChains, val):
        self._indexChains = indexChains
        self._val = val
        
    def __iter__(self):
        if self._val is None:
            return
        
        curIndex = self._indexChains._startList[self._val]
        
        while curIndex >= 0:
            yield curIndex
            curIndex = self._indexChains._chainList[curIndex]
        
