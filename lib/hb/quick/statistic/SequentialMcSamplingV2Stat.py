from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.util.McEvaluators import computeNumMoreExtreme, computePurePseudoPvalue
from quick.statistic.StatisticV2 import StatisticV2
from quick.statistic.GenericMCSamplesV2Stat import GenericMCSamplesV2Stat
from quick.util.debug import DebugUtil

class SequentialMcSamplingV2Stat(MagicStatFactory):
    '''
    Samples according to the sequential MC scheme,
    relying on validateAndPossiblyResetLocalResults to continue sampling until enough has been sampled
    '''
    pass

class SequentialMcSamplingV2StatUnsplittable(StatisticV2):
    def _init(self, rawStatistic, tail, mThreshold, maxSamples, numSamplesPerChunk, **kwArgs):
        self._rawStatistic = self.getRawStatisticClass(rawStatistic)
        self._tail = tail
        self._mThreshold = int(mThreshold)

        if kwArgs.get('minimal') == True:
            self._maxSamples = 1
            self._numSamplesPerChunk = 1
        else:
            if maxSamples=='unlimited':
                self._maxSamples = None
            else:
                self._maxSamples = int(maxSamples)
            self._numSamplesPerChunk = int(numSamplesPerChunk)
        
        self._realSample = None
        self._mcSamples = []
    
    def _compute(self):
        if self._realSample is None:
            self._realSample = self._realTestStatistic.getResult()
        #draw further mcSamples, get a new object each time as GenericMCSamplesStat is not IS_MEMOIZABLE.
        mcTestStatistics = GenericMCSamplesV2Stat(self._region, self._trackStructure, numMcSamples = self._numSamplesPerChunk, **self._kwArgs)
        self._mcSamples.extend( mcTestStatistics.getResult() )
        
        return (self._realSample, self._mcSamples)
        
    def _createChildren(self):
        self._realTestStatistic = self._addChild(self._rawStatistic(self._region, self._trackStructure, **self._kwArgs) )

    def isIndividuallyMcDetermined(self):
        numSamples = len(self._mcSamples)
        if numSamples >= self._maxSamples:
            #print 'TEMP6', (numSamples, self._maxSamples)
            return True
                
        numNonExtreme = numSamples - computeNumMoreExtreme(self._realSample, self._mcSamples, self._tail)
        if numNonExtreme >= self._mThreshold:
            #print 'TEMP5', (numNonExtreme, self._mThreshold)
            return True
        return False
    
    def isMcDetermined(self):
        return self.isIndividuallyMcDetermined() #no distinction for sequential MC
        
    def _getPval(self):
        return computePurePseudoPvalue(self._realSample, self._mcSamples, self._tail)
    
    @classmethod
    def validateAndPossiblyResetLocalResults(cls, localSamplingObjects):
        numNonDetermined = 0
        for i in range(len(localSamplingObjects)):
            if not localSamplingObjects[i].isMcDetermined():
                numNonDetermined +=1
                del localSamplingObjects[i]._result                                
        return numNonDetermined
        
    def validateAndPossiblyResetGlobalResult(self, dummy):
        determined = self.isMcDetermined()
        if not determined:
            del self._result
        
        numSamples = len(self._mcSamples)
        numNonExtreme = numSamples - computeNumMoreExtreme(self._realSample, self._mcSamples, self._tail)
        #print 'TEMP1: ', self._region, [0 if determined else 1, numNonExtreme, self._mThreshold]
        return [0 if determined else 1, numNonExtreme, self._mThreshold, 'N/A', 'N/A']
