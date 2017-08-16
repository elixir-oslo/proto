from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSplittable
from quick.statistic.GenericRelativeToGlobalStat import GenericRelativeToGlobalStatUnsplittable
from quick.statistic.ListOfPresentCategoriesStat import ListOfPresentCategoriesStat
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from collections import defaultdict
from collections import OrderedDict
from gold.util.CommonFunctions import smartSum
from quick.webtools.plot.CreateBpsVennDIagram import CreateBpsVennDIagram

class VennDataStat(MagicStatFactory):
    pass

class VennDataStatSplittable(StatisticSplittable):
    def _combineResults(self):
        allKeys = reduce(lambda l1,l2:l1+l2, [childDict['stateBPCounter'].keys() for childDict in self._childResults])
        uniqueKeys = set(allKeys)
        #print 'uniqueKeys: ', uniqueKeys
        tmp = dict([ (key, smartSum([res['stateBPCounter'].get(key) for res in self._childResults])) for key in uniqueKeys ])
        res = {'catInfo':self._childResults[0]['catInfo']}
        res['stateBPCounter'] = tmp
        res['genome'] = self.getGenome()
        self._result = res
        #self._result = {'result':res}
        #print 'self._result: ', self._result
        
        return self._result
            
class VennDataStatUnsplittable(Statistic):
    
    def _init(self, minimal=False, **kwArgs):
        self._minimal = minimal 

    
    def _compute(self):
        
        #categoryBedList, categoryNames = CreateBpsVennDIagram.getCategoryBedList(geSourceList[0])
        
        categoryNames = self._children[1].getResult()
        rawData = self._children[0].getResult()
        chr = rawData.genomeAnchor.chr
        ends = list(rawData.endsAsNumpyArray())
        starts = list(rawData.startsAsNumpyArray())
        catList = list(rawData.valsAsNumpyArray())
        categoryBedList = defaultdict(list)
        for i in range(len(starts)):
            categoryBedList[chr].append((starts[i], ends[i], catList[i]))
        return self._calculateIntersections(categoryBedList, categoryNames, ':'.join(self._track.trackName))
        
    @staticmethod
    def _calculateIntersections(categoryBedList, categoryNames, thisTrackName):
        
        #thisTrackName = ':'.join(self._track.trackName)
        # make cat selection list, all are considerd in the from this tool. To be used in subsequent methoods that also can be called from other tools where this come into play.
        labelToPrime = CreateBpsVennDIagram.getPrimeList()
        counter =0
        catInfo = OrderedDict()
        for c in categoryNames:
            catInfo[c] = {'label':labelToPrime.keys()[counter], 'prime':labelToPrime.values()[counter], 'selection':'in', 'fullTrackName':thisTrackName}
            counter = counter+1
        
        # collapse to startorstop and state lists
        posDict, catDict = CreateBpsVennDIagram.getPosCatDictsFromCategoryBedList(categoryBedList, catInfo)
        
        # iterate list and get stateBPCounter and stateRegions
        stateBPCounter, stateRegions, thisdebugstring = CreateBpsVennDIagram.getStateCount(posDict, catDict)
        
        
        thisresults = {'stateBPCounter':stateBPCounter, 'catInfo':catInfo}
        #print 'thisresults: ', thisresults
        ret = thisresults
        
        return ret
        
        #utfil = open(galaxyFn, 'w')
        #utfil.write(CreateBpsVennDIagram.getHtmlString(catInfo, stateBPCounter, genome))
        #utfil.close()
    
        #return ''
        
    
    #def old_compute(self):
    #    primeList = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    #    primeConvertDict = dict()
    #    
    #    catSet = self._children[1].getResult()
    #    rawData = self._children[0].getResult()
    #    ends = list(rawData.endsAsNumpyArray())
    #    starts = list(rawData.startsAsNumpyArray())
    #    catList = list(rawData.valsAsNumpyArray())
    #    #catSet = set(catList)
    #    
    #    for indx, i in enumerate(catSet):
    #        primeConvertDict[i] = primeList[indx]
    #    
    #    catStart = [primeConvertDict[v] for v in catList]
    #    catEnd = [-v for v in catStart]
    #    catList = catStart+catEnd
    #    posList = starts + ends
    #    
    #    
    #    
    #    resultCounter = defaultdict(int)
    #    indxSortedList = sorted(range(len(posList)), key=posList.__getitem__)
    #
    #    currentState = 1
    #    currentPos = 0
    #    for indx in indxSortedList:
    #        pos = posList[indx]
    #        primeVal = catList[indx]
    #        if currentPos != pos:
    #            resultCounter[str(abs(currentState))] += pos-currentPos
    #            currentPos=pos
    #            
    #        if primeVal<0:
    #            currentState/=primeVal
    #        else:
    #            currentState*=primeVal
    #                
    #    return resultCounter
    
        #if catSequence is None:
        #    raise IncompatibleTracksError()
        #
        #catSet = numpy.unique(catSequence)
        #res = {}
        #for cat in catSet:
        #    filter = (catSequence==cat)
        #    if rawData.trackFormat.reprIsDense():
        #        res[cat] = filter.sum()
        #    else:
        #        #print 'BpCoverage..: ',ends, starts, catSequence, catSet, type(catSequence), filter
        #        #res[cat] = ends[filter].sum() - starts[filter].sum()
        #        catStarts = starts[filter]
        #        catEnds = ends[filter]
        #        
        #        totCoverage = catEnds.sum() - catStarts.sum()
        #        
        #        runningMaxEnds = numpy.maximum.accumulate(catEnds)
        #        tempArray1 = runningMaxEnds[:-1] - catStarts[1:]
        #        tempArray2 = runningMaxEnds[:-1] - catEnds[1:]
        #        totOverlap = tempArray1[tempArray1 > 0].sum() - tempArray2[tempArray2 > 0].sum()
        #        
        #        res[cat] = totCoverage - totOverlap
        #
        #return res
        
    def _createChildren(self):
        # ,
        self._track._trackFormatReq._allowOverlaps = True
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='category', allowOverlaps=True)) )
        #self._addChild( CountPointStat(self._region, self._track, TrackFormatReq(val='category', allowOverlaps=False)) )
        self._addChild(ListOfPresentCategoriesStat(GenericRelativeToGlobalStatUnsplittable.getGlobalSource('chrs', self.getGenome(), self._minimal), self._track))
