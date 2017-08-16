from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.track.TrackView import TrackView
from gold.util.CustomExceptions import AbstractClassError
import numpy as np
from gold.application.LogSetup import logMessage
import time
from collections import defaultdict
from itertools import *

class ConvertToNonOverlappingCategorySegmentsPythonStat(MagicStatFactory):
    pass

#class ConvertToNonOverlappingCategorySegmentsPythonStat(StatisticSumResSplittable):
#    pass
            
class ConvertToNonOverlappingCategorySegmentsPythonStatUnsplittable(Statistic):
    def _init(self, combineMethod='mostCommonCat', category='', numSamples='1', **kwArgs):
        self._combineMethod = combineMethod
        self._category = category
        self._numSamples = float(numSamples)
        
    def _compute(self):
        start = time.time()
        tv = self._children[0].getResult()
        starts, ends, vals = tv.startsAsNumpyArray(), tv.endsAsNumpyArray(), tv.valsAsNumpyArray()
        endVals = vals[np.argsort(ends)]
        
        borderDict = dict()
        for index, val in enumerate(starts):
            if val in borderDict:
                borderDict[val][0]+=1
            else:
                borderDict[val] = [1,0]
            if ends[index] in borderDict:
                borderDict[ends[index]][1]+=1
            else:
                borderDict[ends[index]] = [0,1]
        uniquePoints = sorted(borderDict.keys())
        borderArray = [borderDict[v] for v in uniquePoints]
        del starts, ends # delete unneccessary memory
        
        if self._combineMethod == 'mostCommonCat':
            combineMethod = MostCommonCategory()
        elif self._combineMethod == 'freqOfCat':
            combineMethod = FrequencyOfCategory(self._category, self._numSamples)
            
        if len(uniquePoints) > 0:
            newVals =[combineMethod.getEmptyElement() for v in xrange(len(uniquePoints))]# np.zeros(len(uniquePoints), dtype=vals.dtype)#FIXME lager arrayen som skal holde resultatene
            
            accStart = numVals = accEnd = 0
            #print 'before for-loop:  ', time.time()-start
            countAddition =0
            for uniqueIndex, uniqueRow in enumerate(borderArray):
                newVals[uniqueIndex] = combineMethod.getCombinedValueForRegion(numVals)
                
                newAccStart = accStart+uniqueRow[0]
                newAccEnd = accEnd + uniqueRow[1]
                
                while accStart<newAccStart:
                    combineMethod.updateForRegionStart(vals[accStart])
                    accStart+=1
                    
                while accEnd<newAccEnd:
                    combineMethod.updateForRegionEnd(endVals[accEnd])
                    accEnd+=1
                
                accEnd, accStart = newAccEnd, newAccStart
                numVals += uniqueRow[0] - uniqueRow[1]
            #print 'after for-loop:  ', time.time()-start
            #logMessage('Iterated through %i Subtractions' % countAddition)
            #logMessage(repr(combineMethod.valueDict.keys()))
        else:
            newVals = [combineMethod.getEmptyElement()]
         
        segBorders = np.array(uniquePoints) + tv.genomeAnchor.start
        return TrackView(genomeAnchor = tv.genomeAnchor, startList=segBorders[:-1], endList=segBorders[1:], valList=np.array(newVals[1:], dtype=combineMethod.getDataType()), \
                         strandList=None, idList=None, edgesList=None, weightsList=None, borderHandling=tv.borderHandling, allowOverlaps=tv.allowOverlaps)
        
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=True, dense=False, interval=True, val='category')) )

class CombineMethod(object):
    def __init__(self):
        raise AbstractClassError
    
    def updateForRegionStart(self, value):
        raise AbstractClassError
    
    def updateForRegionEnd(self, value):
        raise AbstractClassError

    def getCombinedValueForRegion(self, numVals):
        raise AbstractClassError
    
    def getEmptyElement(self):
        raise AbstractClassError
    
    def getDataType(self):
        raise AbstractClassError

class MostCommonCategory(CombineMethod):
    def __init__(self):
        self._contentSnapshot = defaultdict(int)# dict([(v,0) for v in np.unique(vals)])# contentsnapshot inneholder antall av hver kategori for aktuell region
    
    def updateForRegionStart(self, value):
        self._contentSnapshot[value]+=1
    
    def updateForRegionEnd(self, value):
        self._contentSnapshot[value]-=1

    def getCombinedValueForRegion(self, numVals):
        if numVals > 0:
            maxVal = max(self._contentSnapshot.itervalues())
            uniqueVals = sum(1 for v in self._contentSnapshot.iterkeys() if self._contentSnapshot[v]>0)
            maxValCandidates = [key for key in self._contentSnapshot.iterkeys() if self._contentSnapshot[key]==maxVal]
            return ';'.join(maxValCandidates)+'(%i/%i, %i)' % (maxVal, numVals, uniqueVals)
        return ''
    
    def getEmptyElement(self):
        return ''
    
    def getDataType(self):
        return 'S'

class FrequencyOfCategory(CombineMethod):
    def __init__(self, category, numSamples):
        self._count = 0
        self._category = category
        self._numSamples = numSamples
        logMessage('kategori = %s' % self._category)
        self.valueDict = dict()
        
    def updateForRegionStart(self, value):
        if value == str(self._category):
            self._count += 1
        if not value in self.valueDict.keys():
            self.valueDict[value] = None
        
    
    def updateForRegionEnd(self, value):
        if value == str(self._category):
            self._count -= 1

    def getCombinedValueForRegion(self, numVals):
        if numVals > 0:
            return float(self._count)/self._numSamples
        return 0.0
    
    def getEmptyElement(self):
        return 0.0
    
    def getDataType(self):
        return 'float64'
