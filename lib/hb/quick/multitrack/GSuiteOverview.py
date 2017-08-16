from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from quick.statistic.StatFacades import SegmentTrackOverviewStat
from quick.application.UserBinSource import GlobalBinSource
from gold.track.Track import Track
from collections import OrderedDict
from quick.statistic.RipleysKStat import RipleysKStat
'''
Created on Mar 5, 2015

@author: boris
'''

from numpy import mean, median, float64


class GSuiteOverview(object):
    '''
    Get some overview statistics for a GSuite.
    For each track:
    1. Bp coverage
    2. Avg segment length
    3. Avg gap length
    4,5. Max, min segment length
    6,7.Max. min gap length
    Per GSuite: 
    1,2,3. Max, min, avg bp coverage
    '''

    def __init__(self, gSuite):
        assert gSuite.isPreprocessed(), "Preprocessed GSuite required!"
        self._gSuite = gSuite
        self._genome = gSuite.genome


    def _getTrackStats(self, trackName, analysisBins):
        analysisSpec = AnalysisSpec(SegmentTrackOverviewStat)
#         analysisBins = GlobalBinSource(self._genome)
        track = Track(trackName)
        return doAnalysis(analysisSpec, analysisBins, [track])
        
 
    def _getTrackOverviewData(self, title, trackName, analysisBins):
        trackOverviewData = TrackOverviewData(title)
        results = self._getTrackStats(trackName, analysisBins)
        globalResultDict = results.getGlobalResult()
        if not globalResultDict:#should not happen?
            return None
        trackOverviewData.bpsCoverage = int(globalResultDict['CountStat'])
        trackOverviewData.elementCount = globalResultDict['CountElementStat']
        trackOverviewData.avgSegmentLen = globalResultDict['AvgElementLengthStat']
        trackOverviewData.minSegmentLen = globalResultDict['MinLen']
        trackOverviewData.maxSegmentLen = globalResultDict['MaxLen']
        trackOverviewData.medianSegmentLen = globalResultDict['MedianLen']
        trackOverviewData.avgDistLen = globalResultDict['AvgElementDistStat']
        trackOverviewData.minDistLen = globalResultDict['MinDist']
        trackOverviewData.maxDistLen = globalResultDict['MaxDist']
        trackOverviewData.medianDistLen = globalResultDict['MedianDist']
        trackOverviewData.propCoverage = globalResultDict['ProportionElementCountStat']
        for regionKey in results.getAllRegionKeys():
            trackOverviewData.addLocalResult(regionKey, results[regionKey])

        return trackOverviewData
    
    
    def getGSuiteOverviewData(self, analysisBins=None):
        if not analysisBins:
            analysisBins = GlobalBinSource(self._genome)
        overviewData = GSuiteOverviewData()
        for gSuiteTrack in self._gSuite.allTracks():
            trackOverviewData = self._getTrackOverviewData(gSuiteTrack.title, gSuiteTrack.trackName, analysisBins)
            if trackOverviewData:
                overviewData.addTrackOverviewData(trackOverviewData)
                
        
        return overviewData 
    
    def getGSuiteRipleysKData(self, bpWindow=1000, analysisBins=None):
        resDict = OrderedDict()
        ripleysK = AnalysisSpec(RipleysKStat)
        ripleysK.addParameter('bpWindow', str(bpWindow))
        for track in self._gSuite.allTracks():
            ripleysKResults = doAnalysis(ripleysK, analysisBins, [Track(track.trackName)])
            resDict[track.title] = ripleysKResults.getGlobalResult()['Result']
        return resDict
    
    def getGSuiteRipleysKSummaryStatistics(self, resDict):
        avgRK = mean(resDict.values(), dtype=float64)
        minRK = min(resDict.values())
        maxRK = max(resDict.values())
        weakStrong = ''
        if avgRK < 0.5: 
            weakStrong = "strong tendency for repulsion/dispersion (genomic elements falling seldomly in the proximity of each other)"  
        elif avgRK >= 0.5 and avgRK < 1: 
            weakStrong = "tendency for repulsion/dispersion (genomic elements falling seldomly in the proximity of each other)"
        elif avgRK >= 1 and avgRK < 2: 
            weakStrong = "weak local clustering tendency"
        elif avgRK >= 2 and avgRK < 10: 
            weakStrong = "strong local clustering tendency"
        else:
        #>10: 
            weakStrong = "very strong local clustering tendency"
        return avgRK, minRK, maxRK, weakStrong
    
    
class GSuiteOverviewData(object):
    
    def __init__(self):
        '''
        Constructor
        '''
        self._trackOverviewList = []
    
    @property
    def trackOverviewList(self):
        return self._trackOverviewList
 
    def addTrackOverviewData(self, trackOverviewData):
        self.trackOverviewList.append(trackOverviewData)
        
    @property
    def avgCoverage(self):
        if not self.trackOverviewList:
            return 0.0
        return mean([x.bpsCoverage for x in self.trackOverviewList], dtype=float64)

    @property
    def minBpsCoverage(self):
        if not self.trackOverviewList:
            return 0
        return min([x.bpsCoverage for x in self.trackOverviewList])
    
    @property
    def maxBpsCoverage(self):
        if not self.trackOverviewList:
            return 0
        return max([x.bpsCoverage for x in self.trackOverviewList])
    
    @property
    def medianCoverage(self):
        if not self.trackOverviewList:
            return 0
        return median([x.bpsCoverage for x in self.trackOverviewList])
    
    @property
    def avgElementCount(self):
        if not self.trackOverviewList:
            return 0.0
        return mean([x.elementCount for x in self.trackOverviewList], dtype=float64)

    @property
    def minElementCount(self):
        if not self.trackOverviewList:
            return 0
        return min([x.elementCount for x in self.trackOverviewList])

    @property
    def maxElementCount(self):
        if not self.trackOverviewList:
            return 0
        return max([x.elementCount for x in self.trackOverviewList])

    @property
    def medianElementCount(self):
        if not self.trackOverviewList:
            return 0
        return median([x.elementCount for x in self.trackOverviewList])
    
    @property
    def avgPropCoverage(self):
        if not self.trackOverviewList:
            return 0.0
        return mean([x.propCoverage for x in self.trackOverviewList], dtype=float64)
    
    @property
    def minPropCoverage(self):
        if not self.trackOverviewList:
            return 0.0
        return min([x.propCoverage for x in self.trackOverviewList])
    
    @property
    def maxPropCoverage(self):
        if not self.trackOverviewList:
            return 0.0
        return max([x.propCoverage for x in self.trackOverviewList])
    
    def statResultsPerRegionDict(self, statName):
        if len(self.trackOverviewList) == 0:
            return None
        regionKeys = self.trackOverviewList[0].getLocalResultsDict().keys()
        resDict = OrderedDict()
        for regionKey in regionKeys:
            resDict[regionKey] = [x.getLocalResult(regionKey, statName) for x in self.trackOverviewList]
        return resDict
    
#     def avgCoveragePerChromosome(self):
#         return mean(self.statResultsPerRegionDict('CountStat').values())
#     
#     
#     def avgPropCoveragePerChromosome(self):
#         return mean(self.statResultsPerRegionDict('ProportionElementCountStat').values())
    
#     def minAvgCoveragePerChromosome(self):
#         resDict = self.statResultsPerRegionDict('CountStat')
#         minKey = min(resDict, key= lambda x: mean(resDict[x]))
#         return str(minKey), mean(resDict[minKey])
#     
#     def maxAvgCoveragePerChromosome(self):
#         resDict = self.statResultsPerRegionDict('CountStat')
#         maxKey = max(resDict, key= lambda x: mean(resDict[x]))
#         return str(maxKey), mean(resDict[maxKey])
    
    def minAvgPropCoveragePerRegion(self):
        resDict = self.statResultsPerRegionDict('ProportionElementCountStat')
        minKey = min(resDict, key= lambda x: mean(resDict[x], dtype=float64))
        return str(minKey).split(':')[0], mean(resDict[minKey], dtype=float64)
    
    def maxAvgPropCoveragePerRegion(self):
        resDict = self.statResultsPerRegionDict('ProportionElementCountStat')
        maxKey = max(resDict, key= lambda x: mean(resDict[x], dtype=float64))
        return str(maxKey).split(':')[0], mean(resDict[maxKey], dtype=float64)

    @property
    def avgAvgSegmentLen(self):
        if not self.trackOverviewList:
            return 0.0
        return mean([x.avgSegmentLen for x in self.trackOverviewList], dtype=float64)
    
    @property
    def minAvgSegmentLen(self):
        if not self.trackOverviewList:
            return 0.0
        return min([x.avgSegmentLen for x in self.trackOverviewList])
    
    @property
    def maxAvgSegmentLen(self):
        if not self.trackOverviewList:
            return 0.0
        return max([x.avgSegmentLen for x in self.trackOverviewList])
    
    @property
    def medianAvgSegmentLen(self):
        if not self.trackOverviewList:
            return 0.0
        return median([x.avgSegmentLen for x in self.trackOverviewList])
    
    def getElementCountDataDict(self):
        if not self.trackOverviewList:
            return None
        return OrderedDict([(x.trackName, x.elementCount) for x in self.trackOverviewList])
    
    def getCoverageDataDict(self):
        if not self.trackOverviewList:
            return None
        return OrderedDict([(x.trackName, x.bpsCoverage) for x in self.trackOverviewList])

    def getPropCoverageDataDict(self):
        if not self.trackOverviewList:
            return None
        return OrderedDict([(x.trackName, x.propCoverage) for x in self.trackOverviewList])
    
    def getPropCoveragePerRegionDataDict(self):
        return self._getStatPerRegionDataDict('ProportionElementCountStat')
    
    def getElementCountPerRegionDataDict(self):
        return self._getStatPerRegionDataDict('CountElementStat')
        
    def _getStatPerRegionDataDict(self, statName):
        if not self.trackOverviewList:
            return None
        resDict = OrderedDict()
        regionKeys = self.trackOverviewList[0].regionKeys
        for trackOverview in self.trackOverviewList:
            if trackOverview.trackName not in resDict:
                resDict[trackOverview.trackName] = []
            for regionKey in regionKeys:
                resDict[trackOverview.trackName].append(trackOverview.getLocalResult(regionKey, statName))
        
        return resDict, [str(x).split(':')[0] for x in regionKeys]

    
    def getAvgSegmentLengthDataDict(self):
        if not self.trackOverviewList:
            return None
        return OrderedDict([(x.trackName, x.avgSegmentLen) for x in self.trackOverviewList])
    
    

class TrackOverviewData(object):
    
    def __init__(self, trackName):
        self._trackName = trackName
        self._bpsCoverage = 0
        self._elementCount = 0
        self._avgSegmentLen = 0.0
        self._avgDistLen = 0.0
        self._maxSegmentLen = 0
        self._minSegmentLen = 0
        self._medianSegmentLen = 0.0
        self._maxDistLen = 0
        self._minDistLen = 0
        self._medianDistLen = 0.0
        self._propCoverage = 0.0
        self._localResultsDict = OrderedDict()
        self._regionKeys = []
        
    @property
    def trackName(self):
        return self._trackName
        
    @property
    def bpsCoverage(self):
        return self._bpsCoverage
    
    @bpsCoverage.setter
    def bpsCoverage(self, value):
        self._bpsCoverage = value
    
    @property
    def elementCount(self):
        return self._elementCount
    
    @elementCount.setter
    def elementCount(self, value):
        self._elementCount = value
        
    @property
    def avgSegmentLen(self):
        return self._avgSegmentLen
    
    @avgSegmentLen.setter
    def avgSegmentLen(self, value):
        self._avgSegmentLen = value
    
    @property
    def avgDistLen(self):
        return self._avgDistLen
    
    @avgDistLen.setter    
    def avgDistLen(self, value):
        self._avgDistLen = value
    
    @property
    def maxSegmentLen(self):
        return self._maxSegmentLen
    
    @maxSegmentLen.setter
    def maxSegmentLen(self, value):
        self._maxSegmentLen = value
    
    @property
    def minSegmentLen(self):
        return self._minSegmentLen
    
    @minSegmentLen.setter    
    def minSegmentLen(self, value):
        self._minSegmentLen = value
    
    @property
    def medianSegmentLen(self):
        return self._medianSegmentLen
    
    @medianSegmentLen.setter
    def medianSegmentLen(self, value):
        self._medianSegmentLen = value
    
    @property
    def maxDistLen(self):
        return self._maxDistLen
    
    @maxDistLen.setter
    def maxDistLen(self, value):
        self._maxDistLen = value
    
    @property
    def minDistLen(self):
        return self._minDistLen
        
    @minDistLen.setter
    def minDistLen(self, value):
        self._minDistLen = value
        
    @property
    def medianDistLen(self):
        return self._medianDistLen 
        
    @medianDistLen.setter
    def medianDistLen(self, value):
        self._medianDistLen = value 

    @property
    def propCoverage(self):
        return self._propCoverage
        
    @propCoverage.setter
    def propCoverage(self, value):
        self._propCoverage = value 
        
    @property
    def regionKeys(self):
        if self._localResultsDict:
            return self._localResultsDict.keys()
        
    def addLocalResult(self, regionKey, value):
        self._localResultsDict[regionKey] = value
    
    def getLocalResultsDict(self):
        return self._localResultsDict
    
    def getLocalResults(self, regionKey):
        if regionKey in self.getLocalResultsDict():
            return self.getLocalResultsDict()[regionKey]
    
    def getLocalResult(self, regionKey, statKey):
        if self.getLocalResults(regionKey) and statKey in self.getLocalResults(regionKey):
            return self.getLocalResultsDict()[regionKey][statKey]
