from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.track.TrackView import TrackView
import numpy as np
from copy import copy

class ConvertToNonOverlappingCategorySegmentsStat(MagicStatFactory):
    pass

#class ConvertToNonOverlappingCategorySegmentsStatSplittable(StatisticSumResSplittable):
#    pass
            
class ConvertToNonOverlappingCategorySegmentsStatUnsplittable(Statistic):
    def _countDuplicates(self, a):
        a = copy(a)
        if len(a) == 0:
            return a, np.zeros(0, dtype='int32')
        a.sort()
        diff = np.concatenate((np.array([True]), a[:-1] != a[1:]))
        idx = np.concatenate((np.where(diff)[0], [len(a)]))
        uniqueElements = a[idx[:-1]]
        numDuplicates = np.diff(idx)
        return uniqueElements, numDuplicates
    
    def _compute(self):
        tv = self._children[0].getResult()
        nElements = tv.getNumElements()
        starts, ends, vals = tv.startsAsNumpyArray(), tv.endsAsNumpyArray(), tv.valsAsNumpyArray()
        sortedToOriginalEndIndices = np.argsort(ends)# neccessary to find the correct values for end events
        
        uniqueSortedPositions, uniquePosIndices = np.unique1d(np.concatenate((starts, ends)), return_inverse=True)
        if uniqueSortedPositions.size > 1:
            posEventArray = np.zeros( (uniqueSortedPositions.size,2), dtype='int32') #the number of segments starting and ending at each unique position
     
            # starts
            indices, counts = self._countDuplicates(uniquePosIndices[:nElements])
            posEventArray[indices,0] = counts
            # ends
            indices, counts = self._countDuplicates(uniquePosIndices[nElements:])
            posEventArray[indices,1] = counts
            del starts, ends, indices, counts, uniquePosIndices # delete unneccessary arrays to free memory
            
            newVals = np.zeros(uniqueSortedPositions.size-1, dtype=vals.dtype)
            
            uniqueVals = np.unique(vals)
            uniqueValCounts = np.zeros( uniqueVals.size, dtype='int32' ) # array with the current count for each unique value

            #NumPy record array for converting from category values to corr. indices in the uniqueValCounts array
            recDType = np.dtype({ 'names': [str(x) for x in uniqueVals], 'formats': ['int32']*uniqueVals.size })
            uniqueValCountsIndices = np.array([tuple(range( len(uniqueVals) ))], dtype=recDType)
            
            accStart = 0
            accEnd = 0
            
            for posEventIndex in xrange(len(posEventArray)):
                startEvents, endEvents = posEventArray[posEventIndex]
                numVals = uniqueValCounts.sum()
                if numVals > 0:
                    maxCount = uniqueValCounts.max()
                    newVals[posEventIndex-1] = ';'.join([str(x) for x in uniqueVals[np.where(uniqueValCounts==maxCount)]])+'(%i/%i)' % (maxCount, numVals)
                uniqueEventVals, counts = self._countDuplicates(vals[accStart:accStart+startEvents])
                if uniqueEventVals.size > 0:
                    uniqueValCounts[uniqueValCountsIndices[uniqueEventVals].view('int32')] += counts

                uniqueEventVals, counts = self._countDuplicates(vals[sortedToOriginalEndIndices[accEnd:accEnd+endEvents]])
                if uniqueEventVals.size > 0:
                    uniqueValCounts[uniqueValCountsIndices[uniqueEventVals].view('int32')] -= counts
    
                accStart += startEvents 
                accEnd += endEvents
                
        else:
            newVals = np.array([], dtype=vals.dtype)
            
        segBorders = uniqueSortedPositions + tv.genomeAnchor.start
        return TrackView(genomeAnchor = tv.genomeAnchor, startList=segBorders[:-1], endList=segBorders[1:], valList=newVals, \
                         strandList=None, idList=None, edgesList=None, weightsList=None, borderHandling=tv.borderHandling, allowOverlaps=tv.allowOverlaps)
        
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=True, dense=False, interval=True, val='category')) )

