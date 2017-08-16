from math import floor, ceil
from gold.track.TrackView import TrackView
from gold.formatconversion.FormatConverter import FormatConverter
from gold.track.VirtualNumpyArray import VirtualNumpyArray
import numpy

class VirtualStartFromInterval(VirtualNumpyArray):
    def __init__(self, startArray, endArray, strandArray):
        VirtualNumpyArray.__init__(self)
        self._startArray = startArray
        self._endArray = endArray
        self._strandArray = strandArray
            
    #def __getslice__(self, i, j):
    #    if self._strandArray != None:
    #        return self.__class__(self._startArray[i:j], self._endArray[i:j], self._strandArray[i:j])
    #    else:
    #        return self.__class__(self._startArray[i:j], self._endArray[i:j], None)
    
    #To support lazy loading, i.e. to not load the modified array in the __init__ method of TrackView
    def __len__(self):
        return len(self._startArray)
    
class VirtualStartFromIntervalStart(VirtualStartFromInterval):
    #def __getitem__(self, key):
    #    if self._strandArray == None or self._strandArray[key]:
    #        return self._startArray[key]
    #    else:
    #        return self._endArray[key] - 1
        
    def _asNumpyArray(self):
        if self._strandArray is None:
            return self._startArray
        else:
            return numpy.where(self._strandArray, self._startArray, self._endArray-1)
            #return self._startArray * self._strandArray + (self._endArray-1) * (1-self._strandArray)
            #return numpy.array([ (self._startArray[i] if self._strandArray[i] else self._endArray[i]-1) \
                                 #for i in xrange(len(self._startArray))])
        
class VirtualStartFromIntervalMid(VirtualStartFromInterval):
    #def __getitem__(self, key):
    #    return (self._endArray[key] + self._startArray[key]) / 2
    #    #if self._strandArray == None or self._strandArray[key]:
    #    #    return (self._endArray[key]-1 + self._startArray[key]) / 2
    #    #else:
    #    #    return (self._endArray[key] + self._startArray[key]) / 2

    def _asNumpyArray(self):
        return (self._endArray + self._startArray) / 2

#class VirtualStartFromIntervalMidCeil(VirtualStartFromInterval):
#    def __getitem__(self, key):
#        if self._strandArray == None or self._strandArray[key]:
#            return int(ceil((self._endArray[key]-1 + self._startArray[key]) / 2.0))
#        else:
#            return int(floor((self._endArray[key]-1 + self._startArray[key]) / 2.0))

class VirtualStartFromIntervalEnd(VirtualStartFromInterval):
    #def __getitem__(self, key):
    #    if self._strandArray == None or self._strandArray[key]:
    #        return self._endArray[key] - 1
    #    else:
    #        return self._startArray[key]

    def _asNumpyArray(self):
        if self._strandArray is None:
            return self._endArray - 1
        else:
            return numpy.where(self._strandArray, self._endArray-1, self._startArray)
            #return (self._endArray-1) * self._strandArray + self._startArray * (1-self._strandArray)
            
            #return numpy.array([ (self._endArray[i]-1 if self._strandArray[i] else self._startArray[i]) \
            #                     for i in xrange(len(self._startArray))])


class SegmentToPointFormatConverter(FormatConverter):
    @classmethod
    def convert(cls, tv):
        startList = cls._virtualListClass(tv._startList, tv._endList, tv._strandList)
        valList = tv._valList
        strandList = tv._strandList
        idList = tv._idList
        edgesList = tv._edgesList
        weigthsList = tv._weightsList
        extraLists = tv._extraLists
        
        if len(startList) > 0:
            sortIndexes = numpy.argsort(startList)
            startList = startList[sortIndexes]
            if valList is not None:
                valList = valList[sortIndexes]
            if strandList is not None:
                strandList = strandList[sortIndexes]
            if idList is not None:
                idList = idList[sortIndexes]
            if edgesList is not None:
                edgesList = edgesList[sortIndexes]
            if weigthsList is not None:
                weigthsList = weigthsList[sortIndexes]
            for key in extraLists:
                if extraLists[key] is not None:
                    extraLists[key] = extraLists[key][sortIndexes]

        #if tv.allowOverlaps and len(startList) >= 2:
        #    #What we really want to do is:
        #    #sortedZippedList = sorted(zip(startList, valList, strandList) ))
        #    #startList, valList, strandList = zip(*sortedZippedList)
        #    #But, since valList or strandList may be None:
        #
        #    sortedZippedList = sorted(zip(*( [startList] + \
        #                                     [x for x in [valList, strandList, idList, \
        #                                                  edgesList, weigthsList] + \
        #                                                  extraLists.values() if x is not None] )))
        #    x = zip(*sortedZippedList)
        #    startList = x.pop(0)
        #    if valList is not None:
        #        valList = x.pop(0)
        #    if strandList is not None:
        #        strandList = x.pop(0)
        #    if idList is not None:
        #        idList = x.pop(0)
        #    if edgesList is not None:
        #        edgesList = x.pop(0)
        #    if weigthsList is not None:
        #        weigthsList = x.pop(0)
        #    for key in extraLists:
        #        if extraLists[key] is not None:
        #            extraLists[key] = x.pop(0)
        #    assert(x == [])
            
        newTv = TrackView(tv.genomeAnchor, startList, None, valList, strandList, idList, edgesList, weigthsList, tv.borderHandling, tv.allowOverlaps, extraLists=extraLists)
        newTv = newTv[:]
        return newTv
    
    @classmethod
    def _canHandle(cls, sourceFormat, reqFormat):
        isSegmentToPoint = sourceFormat.isInterval() and not sourceFormat.isDense() and not reqFormat.isInterval() and not reqFormat.isDense()
        return isSegmentToPoint
    
    @classmethod
    def _getTrackFormatExceptionList(cls):
        return ['interval','dense']
    
class SegmentToStartPointFormatConverter(SegmentToPointFormatConverter):
    _virtualListClass = VirtualStartFromIntervalStart
    def getOutputDescription(self, sourceFormatName):
        return "The upstream end point of every segment (converted from '" + sourceFormatName + "')"
    
class SegmentToMidPointFormatConverter(SegmentToPointFormatConverter):
    _virtualListClass = VirtualStartFromIntervalMid
    def getOutputDescription(self, sourceFormatName):
        return "The middle point of every segment (converted from '" + sourceFormatName + "')"

class SegmentToEndPointFormatConverter(SegmentToPointFormatConverter):
    _virtualListClass = VirtualStartFromIntervalEnd
    def getOutputDescription(self, sourceFormatName):
        return "The downstream end point of every segment (converted from '" + sourceFormatName + "')"
