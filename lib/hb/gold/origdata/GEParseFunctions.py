def getStart(ge):
    return ge.start

def getEnd(ge):
    return ge.end

def getVal(ge):
    return ge.val

def getStrand(ge):
    return ge.strand

def getId(ge):
    return ge.id
    
def getEdges(ge):
    return ge.edges
    
def getWeights(ge):
    return ge.weights
    
def getNone(ge):
    return None

def getPointEnd(ge):
    return ge.start + 1

class GetExtra:
    def __init__(self, prefix):
        self._prefix = prefix
        
    def parse(self, ge):
        if self._prefix == 'extra':
            return ge.extra['extra']
        return getattr(ge, self._prefix)

class GetPartitionStart:
    def __init__(self):
        self._prevEnd = 0
        
    def parse(self, ge):
        #print self, ge, ge.end
        tempPrevEnd = self._prevEnd
        self._prevEnd = ge.end
        return tempPrevEnd
        
def writeNoSlice(mmap, index, ge, parseFunc):
    #print index, ge, parseFunc.__name__, parseFunc(ge)
    mmap[index] = parseFunc(ge)

def writeSliceFromFront(mmap, index, ge, parseFunc):
    #print index, ge, ge.edges, ge.weights, parseFunc.__name__
    geLen = sum(1 for x in parseFunc(ge))
    if geLen >= 1:
        mmap[index][:geLen] = parseFunc(ge)
