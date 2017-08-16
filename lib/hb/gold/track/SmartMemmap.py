import os
from numpy import memmap
from functools import partial, update_wrapper
import numpy
from config.Config import MEMMAP_BIN_SIZE
from gold.track.CommonMemmapFunctions import calcShape

#def convertToNumpyScalarIfFuncReturnsMemmapScalar(func, *args, **kwArgs):
#    ret = func(*args, **kwArgs)
#    if isinstance(ret, numpy.memmap) and len(ret.shape) == 0:
#        return ret.dtype.type(ret)
#    return ret
#    
#
#class memmapSth(memmap):
#    def __new__(cls, *args, **kwArgs):
#        return numpy.ndarray.__new__()
#
#    def __init__(self, mmap, member):
#        self._mmap = mmap
#        self._member = member
#        
#    def method(self, *args, **kwArgs):
#        ret = self._member(*args, **kwArgs)
#        if isinstance(ret, numpy.memmap) and len(ret.shape) == 0:
#            return ret.dtype.type(ret)
#        return ret
#
#class memmapWhichReturnsNumpyScalars(memmap):
#    def __init__(self, *args, **kwArgs):
#        memmap.__init__(self, *args, **kwArgs)
#        self.myMethod
#    
#    def method(self, *args, **kwArgs):
#        ret = self._member(*args, **kwArgs)
#        if isinstance(ret, numpy.memmap) and len(ret.shape) == 0:
#            return ret.dtype.type(ret)
#        return ret
#        
#    def __getattribute__(self, attr):
#        member = object.__getattribute__(self, attr)
#        if callable(member):
#            return memmapSth(self, member).method
#            #return partial(convertToNumpyScalarIfFuncReturnsMemmapScalar, member)
#        else:
#            return member

class SmartMemmap(object):
    def __init__(self, fn, elementDim=None, dtype='int32', dtypeDim=1, mode='r'):
        self._fn = fn
        self._dtype = dtype
        self._mode = mode
        self._dTypeSize = numpy.dtype(dtype).itemsize
        self._origShape = calcShape(self._fn, elementDim, dtypeDim, dtype)
        self._cachedMemmapBinNum = None
        self._cachedMemmap = None

    def _crossesBoundary(self, i, j):
        return self._calcBinNum(i) != self._calcBinNum(j)
    
    def _createMemmap(self, i, j):
        if j > self._origShape[0]:
            j = self._origShape[0]

        if j == 0:
            shape = None
        else:
            shape = tuple([j-i] + self._origShape[1:])
        
        return memmap(self._fn, self._dtype, self._mode, offset = i*self._dTypeSize, shape = shape)
    
    def _calcBinNum(self, i):
        return i / MEMMAP_BIN_SIZE
    
    def _getLocalBinCoords(self, i, j):
        return i % MEMMAP_BIN_SIZE, j % MEMMAP_BIN_SIZE

    def _getBinMemmap(self, binNum):        
        if self._cachedMemmapBinNum != binNum:
            self._cachedMemmap = self._createMemmap(binNum * MEMMAP_BIN_SIZE, (binNum+1) * MEMMAP_BIN_SIZE)
            self._cachedMemmapBinNum = binNum
            
        return self._cachedMemmap
    
    def __getslice__(self, i, j):
        if self._crossesBoundary(i, j):
            return self._createMemmap(i, j)[:]
        
        binNum = self._calcBinNum(i)
        localI, localJ = self._getLocalBinCoords(i, j)
        return self._getBinMemmap(binNum)[localI:localJ]
    
    def __getitem__(self, i):
        binNum = self._calcBinNum(i)
        localI = self._getLocalBinCoords(i, 0)[0]
        item = self._getBinMemmap(binNum)[localI]
        return item

    def getShape(self):
        return tuple(self._origShape)
    
    def getDType(self):
        return self._dtype
        
    def getFilename(self):
        return self._fn
    
    shape = property( getShape )
    dtype = property( getDType )
    filename = property( getFilename )
