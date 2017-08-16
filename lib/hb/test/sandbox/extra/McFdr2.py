from test.sandbox.extra.McFdr import *
#from McFdr import *
FDR_THRESHOLD = 0.1

class MultipleTestCollection2(MultipleTestCollection):
    #def getRejectedStatusesAsBitstring(self):
    #    'Returns a bitstring of whether of not each sampleCounter is rejected (based on their internal index)'
    #    return 
        
    def getRejectedStatuses(self):        
        return [counter.isFdrRejected() for counter in self._sampleCounters]
    
    def getCorrectStatuses(self):
        'Returns a bitstring of whether of not each sampleCounter is correctly denoted as rejected/accepted for tests from H1/H0, respectively'
        self.ESTIMATE_PI0 = 'Pounds&Cheng'
        r('library(pi0)')
        self.setFdrThresholdAtAllCounters(FDR_THRESHOLD)        
        self.updateFdrValsOfCounters()
        rejected = self.getRejectedStatuses()
        print ''.join([str(int(x)) for x in rejected])
        for i in range(len(rejected)):
            if i<self._numH0Tests:
                rejected[i] = not rejected[i]
        return rejected
        
#def analyzeSampleNumRobustness(numSamples):
#    mtc = MultipleTestCollection2(95,5,None,None,None, 1,5)
#    mtc.addSamples(numSamples)
    
def analyzeSampleNumAccuracy(numSamples):
    mtc = MultipleTestCollection2(95,5,None,None,None, 1,5)
    mtc.addSamples(numSamples)
    return 100-sum(mtc.getCorrectStatuses()) /float(numSamples)
    
analyzeSampleNumAccuracy(1000)