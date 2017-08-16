from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.BinsScaledDistributionStat import *
from quick.statistic.BinSizeStat import BinSizeStat
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import numpy

class BinScaledSegCoverageStat(MagicStatFactory):
    pass

class BinScaledSegCoverageStatSplittable(BinsScaledDistributionStatSplittable):
    pass
            
class BinScaledSegCoverageStatUnsplittable(BinsScaledDistributionStatUnsplittable):        
    def _compute(self):
        if self._configuredToAllowOverlaps(strict=False):
            return self._computeThatHandlesOverlap()
        else:
            return self._computeWithoutOverlapsUsingNumpyComputations()
            
    def _computeThatHandlesOverlap(self):
        #print 'TEMP Allowing overlap!'
        tv1 = self._children[1].getResult()
        
        if len(tv1) < self._numSubBins:
            return None

        splitPointsAsNumpy = self._getSplitPoints()
        subBinSizesAsNumpy = splitPointsAsNumpy[1:] - splitPointsAsNumpy[:-1]
        splitPoints = list(splitPointsAsNumpy)        
        subBinIntervals = zip(splitPoints[:-1], splitPoints[1:])

        subBinMultiCoverage = [0]*len(subBinIntervals) #multi, as counted so that the interval can be covered multiple times, and get coverage higher than number of bps..
        #print 'TEMP overlap: ', self._children[1]._track._trackFormatReq
        #print 'TEMP Num segs in bin %s: %s' % (self._region, len(list(tv1)))
        for segment in tv1:
            for i, (subBinStart, subBinEnd) in enumerate(subBinIntervals):
                subBinMultiCoverage[i] += max(0, min(segment.end(), subBinEnd) - max(segment.start(), subBinStart))
        
        subBinMultiCoverageAsNumpy = numpy.array( subBinMultiCoverage )

        res = 1.0 * subBinMultiCoverageAsNumpy / subBinSizesAsNumpy
        if self._region.strand == False:
            res = res[::-1]
        return res    
        
        
    def _computeWithoutOverlapsUsingNumpyComputations(self):
        #FIXME: based on a good test with many border-cases: handle many border-cases, such as first/last in splitPoints and segIndexesForSubBins, how to handle equality in the add.reduceat ...
        tv1 = self._children[1].getResult()
        
        if len(tv1) < self._numSubBins:
            return None

        segStarts = tv1.startsAsNumpyArray()
        if len(segStarts)==0:
            return numpy.zeros(self._numSubBins)
            
        segEnds = tv1.endsAsNumpyArray()
        segLens = segEnds - segStarts
        splitPoints = self._getSplitPoints()
        subBinSizes = splitPoints[1:] - splitPoints[:-1]
        #for each subBin, find the index of the first segStart not in that bin..
        nextSegIndexesAfterSplitPoints = segStarts.searchsorted(splitPoints)
        #no start-index should be beyond last splitPoint which is bin-length..
        assert nextSegIndexesAfterSplitPoints[-1] == len(segStarts)
        segIndexesForSubBins = nextSegIndexesAfterSplitPoints[:-1]
        
        #basic sum of lenghts within each subBin
        #appends zero, as numpy does not allow indexes in reduceat beyond array itself.. (we would like an index beyond length to denote zero)
        appendedSegLens = numpy.append(segLens, 0)
        subBinCoverage = numpy.add.reduceat(appendedSegLens, segIndexesForSubBins)
        #print 'TEMP: ',subBinCoverage
        #adjust for numpy-choice when a_i == a_i+1, where we would like value at i to become 0, while numpy assigns value at position i.
        numSegsInSubBins = segIndexesForSubBins[1:] - segIndexesForSubBins[:-1]
        emptySubBins = (numSegsInSubBins == 0)
        subBinCoverage[:-1][emptySubBins] = 0
        
        #Handle the last segments of each subBin, which may cross bin Borders.
        #Should then move part of their bp-coverage to next bin..        
        #FIXME: here there must be perfect correspondence between indexes of different arrays..
        #numpy-code for this:
        #segIndexesForSubBins has the first segment starting in bin i. lastSegStartingInSubBinIndexes has the last segment in bin i-1.
        #lastSegStartingInSubBinIndexes = segIndexesForSubBins[1:] - 1
        lastSegStartingInSubBinIndexes = nextSegIndexesAfterSplitPoints[1:] - 1
        
        spillOver = segEnds[lastSegStartingInSubBinIndexes] - splitPoints[1:]
        spillOver = numpy.maximum(spillOver, numpy.zeros(len(spillOver)) )
        spillOver = spillOver.astype(int)
        #should be no spillover from bins strictly before first segment
        #firstBinWithSegs = segStarts.searchsorted(splitPoints) (kanskje noko meire her? -1 )
        spillOver[ lastSegStartingInSubBinIndexes == -1] = 0
        subBinCoverage -= spillOver
        subBinCoverage[1:] += spillOver[:-1]
        
        #old code..:
        #for i in range(splitPoints):
        #    splitPoint = splitPoints[i]
        #    crossingCandidateIndex = segIndexesForSubBins[i]-1 #last el in each subBin
        #    assert segStarts[crossingCandidateIndex] < splitPoint
        #    if segEnds[crossingCandidateIndex] > splitPoint:
        #        numBpsToMove = segEnds[crossingCandidateIndex] - splitPoint
        #        subBinCoverage[i] -= numBpsToMove
        #        subBinCoverage[i+1] += numBpsToMove
                
        #print 'BIN: ',1.0 * subBinCoverage / subBinSizes
        res = 1.0 * subBinCoverage / subBinSizes
        if self._region.strand == False:
            res = res[::-1]
        return res    

    
    def _createChildren(self):
        self._addChild( BinSizeStat(self._region, self._track))
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=True)) )
