#from itertools import chain
import numpy
from numpy import *
from random import *
from time import time

#not completely finished, as it ignores offsets..
def directImpl(points, segments, offsets, N):
    #points=[10*i+5 for i in range(10)]
    #segments=[[10,12],[44,66],[50,77],[99,100]]
    count=0
    #N=100
    step={}
    for z in points:
      for x,y in segments:
        if (x<=z<=y):
          count+=1
        if not (x-z)%N in step:
            step[(x-z)%N]=0
        step[(x-z)%N]+=1
        if not (y+1-z)%N in step:
            step[(y+1-z)%N]=0
        step[(y+1-z)%N]-=1
    stair={}
    for x in sorted(step.keys()):
      count+=step[x]
      stair[x]=count
    print "0 " + str(count)
    
    return stair
    #for x in sorted(stair.keys()):
    #  print str(x) + " " + str(stair[x])
      
def rotate(points, segStarts, segEnds, offsets, bpSize):
    #assumes points, segStarts, segEnds are given as numpy int-arrays
    #offsets is an iterator of offsets for which to return number of points inside segments
    
    #find number of points at original posision (is used later).
    insideCount = 0
    segIndex=0
    for point in points:
        #pass over segments that are fully to the left of point
        while segIndex<len(segEnds)-1 and segEnds[segIndex] <= point:
            segIndex+=1
        if segStarts[segIndex] <= point < segEnds[segIndex]:
            insideCount += 1    
        
    #mult by two, and add 1 to all starts,
    #so that starts come after ends in the sorting, and starts and ends can be easily distinguished
    segStarts*=2
    segEnds*=2
    segStarts+=1
    
    #use simple sorting, although merging would be more efficient..
    #Get relative position of segments in reference to each of the points.
    
    ##iterators
    #allRelStarts = chain( *(segStarts-p for p in points) )
    #allRelEnds = chain( *(segEnds-p for p in points) )
    #allEvents = chain(allRelStarts, allRelEnds)
    
    #sorting large numarray
    allEvents = numpy.concatenate( [(segStarts-2*p)%(2*bpSize) for p in points] + [(segEnds-2*p)%(2*bpSize) for p in points] )
    allEvents.sort()

    #alternative, with python 2.6:
    #allSubLists = [(segStarts-2*p)%(2*bpSize) for p in points] + [(segEnds-2*p)%(2*bpSize) for p in points]
    #allEvents = numpy.array( heapq.merge(*allSubLists)
    
        
    allDiffs = (allEvents%2)*2 -1#odd numbers (starts) are +1, even numbers -1
    
    allDiffs[0] += insideCount
    
    allCumulative = add.accumulate(allDiffs)
    
    #take segments back to real indexes
    allEvents /= 2
    #segStarts /= 2
    #segEnds /= 2
        
    index=0
    
    #not to be used, only for timing purposes..
    #yield 1
    #return
    
    for offset in offsets:
        #handle offsets before any event has taken place..
        if offset < allEvents[0]:
            yield insideCount
            continue
        
        while allEvents[index+1] < offset:
            index+=1
            #instead of lines below we assume offsets are always within bounds..
            #if index+1 >= len(allEvents):
            #    return
        yield allCumulative[index]
        
def unitTest():           
    points = array([15, 25, 35, 45, 55])
    segStarts = array([10, 100, 300, 400])
    segEnds = array([20, 130, 320, 460])
    offsets = concatenate( [array([0,1,2]), arange(1,50)*10] )

    print list(rotate(points, segStarts, segEnds, offsets, 1000))
    
def timeTest():
    bpSize = 1000000 #1e6
    seed(0)
    points = array([int(random()*bpSize) for i in xrange(500)])
    points.sort()
    starts, ends = [], []
    curr = 0
    for i in xrange(10000):
        curr+= int(random()*80)
        starts.append(curr)
        curr+= int(random()*80)
        ends.append(curr)
        
    segStarts = array(starts)
    segEnds = array(ends)
    offsets = arange(bpSize/10000)*10000
    
    #for directImpl..:
    segments = zip(segStarts, segEnds)
    
    print 'size of problem - points: ', len(points), ' segs: ',len(segStarts)
    
    print 'Running rotate..'
    before = time()
    print list(rotate(points, segStarts, segEnds, offsets, bpSize))
    print 'Finished rotate in ', time()-before, 'seconds..'
    
    print 'Running directImpl..'
    before = time()
    #print len( directImpl(points, segments, offsets, bpSize))
    print 'Finished directImpl in ', time()-before, 'seconds..'
    
unitTest()
#timeTest()


#[1, 1, 1, 0, 0, 0, 0, 1, 2, 3, 3, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 1, 0, 0, 0, 0, 1, 2, 3, 4, 5, 5, 4, 3, 2, 1, 0, 0, 0, 0, 0]
#size of problem - points:  5000  segs:  10000
#Running rotate..
#[1938, 1947, 1999, 1981, 1973, 1905, 1993, 1894, 2005, 1999, 1971, 1944, 1990, 1946, 1987, 1982, 1989, 1930, 1910, 1960, 1951, 1975, 1963, 1992, 1989, 2020, 1909, 1973, 1934, 1952, 1988, 1925, 1952, 1942, 1975, 1909, 1976, 1961, 1995, 1951, 1940, 1889, 1875, 1916, 1961, 1938, 1929, 2011, 1971, 1947, 1937, 1964, 2006, 2020, 1985, 1962, 1922, 1973, 1966, 1967, 1946, 2008, 2007, 2040, 1945, 1954, 1974, 2041, 2060, 1961, 2016, 2006, 2014, 2005, 2043, 1975, 1944, 1965, 1945, 1946, 1980, 1933, 1964, 1993, 2021, 1947, 1934, 1925, 1913, 1953, 1988, 2000, 1922, 1931, 1967, 1957, 1948, 1943, 1921, 1957]
#Finished rotate in  76.9009211063 seconds..
# NOTE: 18 seconds if skipping last step iterating through offsets, which the method below does not use..
#Running directImpl..
#0 1986
#1000000
#Finished directImpl in  519.124060869 seconds..
