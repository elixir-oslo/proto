import time
FASTA_FN = '/hyperdata/RunBioRun/chr1.fa'
PREPROC_FN = '/work/hyperbrowser/preProcessed/100000/noOverlaps/hg18/sequence/chr1/val.S1'
NMER_LEN = 3

def slowPlainSolution(fn):
    def bpIter(fastaFn):
        for line in open(fastaFn):
            if not line.startswith('>'):
                for bp in line.strip():
                    yield bp.lower()
                  
    def nmerSlidingWindow(bpIter, n):
        win = []
        for bp in bpIter:
            win.append(bp)
            if len(win)>n:
                win.pop(0)
            if len(win)==n:
                yield ''.join(win)
            
            
    
    nmerCounts = {}
    for nmer in nmerSlidingWindow(bpIter(fn), NMER_LEN):
        if not nmer in nmerCounts:
            nmerCounts[nmer] = 0
        nmerCounts[nmer]+=1
        
    for key in sorted(nmerCounts.keys()):
        print key, ' : ',nmerCounts[key]
    print 'SUM all nmers: ', sum(nmerCounts.values())
    
from numpy import *            
def fastNumpySolution(fnOrArray):
    if isinstance(fnOrArray, basestring):
        numpyFn = fnOrArray
        s1Seq = memmap(numpyFn,dtype='S1')[:]
    else:
        s1Seq = fnOrArray
    #take lower case?
    codedSeq = zeros( len(s1Seq),'i' ) + 4 #4 should denote N or other symbols..
    for bp,code in [['a',0],['c',1],['g',2],['t',3]]:
        codedSeq[ s1Seq == bp] = code
        codedSeq[ s1Seq == bp.upper()] = code
    nmerSeq = codedSeq[:-2]*25 + codedSeq[1:-1]*5 + codedSeq[2:]
    counts = bincount(nmerSeq)
    #print 'counts: ', counts
    baseCounts = [counts[i] for i in range(len(counts)) if not any([(i/5**k) % (5**(k+1))==4 for k in range(3)])]
    #print 'baseCounts: ', baseCounts
    print '\n'.join([str(x) for x in baseCounts])
    print 'Sum, valid nmers: ', sum(baseCounts)

def printTiming(func, fn):
    befTime = time.time()
    print 'Answer: ', func(fn)    
    afTime = time.time()
    print 'Execution time: ', afTime-befTime

print 'SLOW PLAIN: '
printTiming(slowPlainSolution, FASTA_FN)

print 'FAST NUMPY: '
printTiming(fastNumpySolution, PREPROC_FN)

print 'FAST NUMPY, without disk: '
s1Seq = memmap(PREPROC_FN,dtype='S1')[:]
printTiming(fastNumpySolution, s1Seq)
