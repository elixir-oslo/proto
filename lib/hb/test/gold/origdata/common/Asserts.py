from gold.origdata.GenomeElement import GenomeElement
from gold.origdata.GenomeElementSource import BoundingRegionTuple
from gold.track.GenomeRegion import GenomeRegion
from copy import copy

class MyGeIter:
    def __init__(self, valDataType, valDim, edgeWeightDataType, edgeWeightDim):
        self.iter = []
        self.boundingRegionTuples = []
        self._boundingRegionTuplesToReturn = []
        self._valDataType = valDataType
        self._valDim = valDim
        self._edgeWeightDataType = edgeWeightDim
        self._edgeWeightDim = edgeWeightDim

    def __iter__(self):
        self = copy(self)
        self._geIter = self.iter.__iter__()
        return self
        
    def next(self):
        try:
            return self._geIter.next()
        except StopIteration:
            self._boundingRegionTuplesToReturn = self.boundingRegionTuples
            raise
        
    def getPrefixList(self):
        return [prefix for prefix in ['start', 'end', 'val', 'strand'] \
                if self.iter[0].__dict__.get(prefix) is not None]
        
    def getValDataType(self):
        return self._valDataType
        
    def getValDim(self):
        return self._valDim
    
    def getBoundingRegionTuples(self):
        return self._boundingRegionTuplesToReturn
        
    def getEdgeWeightDataType(self):
        return self._edgeWeightDataType
        
    def getEdgeWeightDim(self):
        return self._edgeWeightDim
        
    def anyWarnings(self):
        return False
        
    def getLastWarning(self):
        return None
        
    def hasBoundingRegionTuples(self):
        return len(self.getBoundingRegionTuples()) > 0
        
def _getIter(elList, valDataType, valDim, edgeWeightDataType, edgeWeightDim, brList=[]):
    geIter = MyGeIter(valDataType, valDim, edgeWeightDataType, edgeWeightDim)
    
    for i in xrange(len(elList)):
        ge = GenomeElement(genome=elList[i][0], chr=elList[i][1], start=elList[i][2], end=elList[i][3])
        if len(elList[i]) == 5:
            for prefix in elList[i][4]:
                setattr(ge, prefix, elList[i][4][prefix])
        geIter.iter.append(ge)
        
    for i in xrange(len(brList)):
        br = GenomeRegion(genome=brList[i][0], chr=brList[i][1], start=brList[i][2], end=brList[i][3])
        geIter.boundingRegionTuples.append(BoundingRegionTuple(br, brList[i][4]))
        
    return geIter

def assertDecorator(decoratorClass, assertFunc, processedList, origList, valDataType='float64', valDim=1, edgeWeightDataType='float64', edgeWeightDim=1):
    decorated = decoratorClass(_getIter(origList, valDataType, valDim, edgeWeightDataType, edgeWeightDim))
    for i in range(3):
        j = -1
        for j, el in enumerate(decorated):
            assert j < len(processedList), '%s < %s' % (j, len(processedList))
            assertFunc(processedList[j][0], el.genome)
            assertFunc(processedList[j][1], el.chr)
            assertFunc(processedList[j][2], el.start)
            assertFunc(processedList[j][3], el.end)
            if len(processedList[j]) == 5:
                for prefix in processedList[j][4]:
                    assertFunc(processedList[j][4][prefix], getattr(el, prefix))
            
        assertFunc(len(processedList), j+1)

def assertBoundingRegions(decoratorClass, assertFunc, processedBoundingRegionTuples, origBoundingRegionTuples, \
                          geList, sendBoundingRegionsToDecorator=False):
    geIter = _getIter(geList, 'float64', 1, 'float64', 1, origBoundingRegionTuples)
    if sendBoundingRegionsToDecorator:
        decorated = decoratorClass(geIter, geIter.boundingRegionTuples)
    else:
        decorated = decoratorClass(geIter)
        
    for i in range(3):
        for el in enumerate(decorated):
            pass
    
        j = -1
        for j, br in enumerate(decorated.getBoundingRegionTuples()):
            assertFunc(processedBoundingRegionTuples[j][0], br.region.genome)
            assertFunc(processedBoundingRegionTuples[j][1], br.region.chr)
            assertFunc(processedBoundingRegionTuples[j][2], br.region.start)
            assertFunc(processedBoundingRegionTuples[j][3], br.region.end)
            assertFunc(processedBoundingRegionTuples[j][4], br.elCount)
        assertFunc(len(processedBoundingRegionTuples), j+1)
