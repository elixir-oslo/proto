
import numpy
from numpy import memmap

#inputs are filenames for memmap-files with starts/ends for track1/2    
def computeOverlap(t1s,t1e,t2s,t2e):    
    t1CodedStarts = memmap(t1s,dtype='int32')  * 8 +5
    t1CodedEnds= memmap(t1e,dtype='int32')  * 8 +3
    t2CodedStarts = memmap(t2s,dtype='int32')  * 8 +6
    t2CodedEnds= memmap(t2e,dtype='int32')  * 8 +2
    
    allSortedCodedEvents = numpy.concatenate( (t1CodedStarts,t1CodedEnds,t2CodedStarts,t2CodedEnds) )
    allSortedCodedEvents.sort()
    
    allEventCodes = (allSortedCodedEvents % 8) -4
    
    allSortedDecodedEvents = allSortedCodedEvents / 8
    allEventLengths = allSortedDecodedEvents[1:] - allSortedDecodedEvents[:-1]
    
    #due to the coding, the last bit now has status of track1, and the second last bit status of track2
    #thus, 3 is cover by both, 2 is cover by only track2, 1 is cover by only track1, 0 is no cover
    #this works as there are no overlaps, and bits will thus not "spill over"..
    cumulativeCoverStatus = numpy.add.accumulate(allEventCodes)
    
    print 'Overlap: ',  (allEventLengths[ cumulativeCoverStatus[:-1] ==3]).sum()


#just for some hardcoded paths...
def findOverlap():
    #11 reelle linjer, siden filnavn kunne vore direkte i memmap-funk
    t1s = '/Users/sandve/Desktop/progTask/track1/start.int32'
    t1e = '/Users/sandve/Desktop/progTask/track1/end.int32'
    t2s = '/Users/sandve/Desktop/progTask/track2/start.int32'
    t2e = '/Users/sandve/Desktop/progTask/track2/end.int32'
    computeOverlap(t1s,t1e,t2s,t2e)

#def findOverlap():
    #your code with hardcoded params...
    #pass

import time
def printTiming(func):
    befTime = time.time()
    print 'Answer: ', func()    
    afTime = time.time()
    print 'Execution time: ', afTime-befTime

printTiming(findOverlap)