import numpy
from itertools import chain
from collections import OrderedDict
from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
from gold.origdata.GEDependentAttributesHolder import GEDependentAttributesHolder, iterateOverBRTuplesWithContainedGEs
from gold.origdata.GtrackComposer import StdGtrackComposer, ExtendedGtrackComposer
from gold.origdata.GESourceWrapper import SortedListGESourceWrapper
from gold.track.TrackFormat import TrackFormat
from gold.util.CustomExceptions import ShouldNotOccurError, InvalidFormatError

# WithoutSorting(GtrackGenomeElementSource)
# - Bounding regions needs to be defined if needed, and all data lines must be found under each bounding region,
#   but everything else may be in unsorted order.

class UnsortedGtrackGenomeElementSource(GtrackGenomeElementSource):
    def _checkBoundingRegionSorting(self, br, lastBoundingRegion):
        pass
        
    def _checkEndOfLastBoundingRegion(self):
        pass
    
    def _checkOverlappingAndSortedElements(self, ge):
        pass
        
    def _checkDenseSorting(self, ge):
        pass


def _getSortedBoundingRegionsAndGenomeElements(geSource):
    geSource = GEDependentAttributesHolder(geSource)
    
    doubleElList = [[brTuple, geList] for brTuple, geList in iterateOverBRTuplesWithContainedGEs(geSource)]
    
    noBoundingRegions = doubleElList[0][0] is None
    if not noBoundingRegions:
        doubleElList.sort(key=lambda x:x[0].region)
    
    for x in doubleElList:
        if len(x[1]) >= 2:
            if x[1][0].reprIsDense():
                break
            x[1].sort()
            
    return doubleElList, geSource
        
def _commonSortGtrackFile(fn, genome):
    gtrackGESource = UnsortedGtrackGenomeElementSource(fn, genome, printWarnings=False)
    useExtendedGtrack = gtrackGESource.isExtendedGtrackFile()
    
    doubleElList, geSource = _getSortedBoundingRegionsAndGenomeElements(gtrackGESource)
    noBoundingRegions = doubleElList[0][0] is None
    
    sortedGESource = SortedListGESourceWrapper(geSource, list(chain(*(x[1] for x in doubleElList))), \
                                               [x[0] for x in doubleElList] if not noBoundingRegions else [])
    
    
    composerCls = ExtendedGtrackComposer if useExtendedGtrack else StdGtrackComposer
    return composerCls( sortedGESource )

def sortedGeSourceHasOverlappingRegions(geSource):
    doubleElList = _getSortedBoundingRegionsAndGenomeElements(geSource)[0]
    
    hasOverlaps = False
    prevSortedElement = None
    for ge in chain(*(x[1] for x in doubleElList)):
        if prevSortedElement is not None and ge.overlaps(prevSortedElement):
            hasOverlaps = True
            break
        prevSortedElement = ge
    
    return hasOverlaps
    
def sortGtrackFileAndReturnContents(inFn, genome=None):
    return _commonSortGtrackFile(inFn, genome).returnComposed()
    
def sortGtrackFileAndWriteToFile(inFn, outFn, genome=None):
    return _commonSortGtrackFile(inFn, genome).composeToFile(outFn)

