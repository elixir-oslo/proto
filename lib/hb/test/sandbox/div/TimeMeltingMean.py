import time
from numpy import memmap

def printTiming(func, fn):
    befTime = time.time()
    print 'Answer: ', func(fn)    
    afTime = time.time()
    print 'Execution time: ', afTime-befTime
    
def basic(fn):
    file = open(fn)
    [file.readline() for i in range(2)]
    tempSum = tempCount = 0.0
    for line in file:
        tempSum += float(line)
        tempCount += 1
    return tempSum / tempCount

def basicWithBufSize(fn):
    file = open(fn,'r',2*10**7)
    [file.readline() for i in range(2)]
    tempSum = tempCount = 0.0
    for line in file:
        tempSum += float(line)
        tempCount += 1
    return tempSum / tempCount

def byMemmap(memmapFn):
    mm = memmap(memmapFn, memmapFn.split('.')[-1], 'r', 0)
    return mm.mean(dtype='float64')

def byNumpyInRam(meltArray):
    return meltArray.mean()
    
#printTiming(basic, )
WIG_FN = '/hyperdata/RunBioRun/MeltingChr1.wig'
MEMMAP_FN = '/work/hyperbrowser/preProcessed/100000/noOverlaps/hg18/DNA structure/Melting/Meltmap/chr1/val.float32'

print 'BASIC: '
printTiming(basicWithBufSize, WIG_FN)

print 'MEmmap-based: '
printTiming(byMemmap, MEMMAP_FN)

memmapFn = MEMMAP_FN
mm = memmap(memmapFn, memmapFn.split('.')[-1], 'r', 0)
meltArray = mm.astype('float64')
print 'When already in memory: '
printTiming(byNumpyInRam, meltArray)

