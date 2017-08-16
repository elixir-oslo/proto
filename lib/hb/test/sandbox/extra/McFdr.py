import os
import random
import time

from proto.RSetup import r, rpy1
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.statistic.McFdr import McFdr


#from gold.util.CommonFunctions import smartSum

#class PvalDistribution(object):
#    def __init__(self, pi0, a=0.5, b=2.5):
#        self._pi0 = pi0
#        self._a = a
#        self._b = b
#        
#    def __iter__(self):
        #while True:
    #        if r.runif(1) < self._pi0:
    #            yield r.runif(1)
    #        else:
    #            yield r.rbeta(1, self._a, self._b)
#            
    
def dictAvg(dictList):
    #allKeys = reduce(lambda l1,l2:l1+l2, [childDict.keys() for childDict in dictList])
    #uniqueKeys = set(allKeys)
    uniqueKeys = dictList[0].keys() #assume same keys present in all..
    return dict([ (key, sum([res.get(key) for res in dictList])/float(len(dictList))) for key in uniqueKeys ])
    


class ExtremeOrNotSampleGenerator(object):
    'The only thing of interest when doing MC-sampling to estimate a p-value, is to whether a sampled value is more extreme than observation or not.'
    'The probabilty of being more extreme is given by the underlying p-value'
    'This class provides an iterator of True/False to simulate whether a sample was more extreme than observed, initialized with an underlying p-value based on supplied parameters'
    def __init__(self, fromH1, a, b): #a=0.5, b=25): 
        self._fromH1 = fromH1
        self._a = a
        self._b = b
        
        if self._fromH1:
            self._underlyingPval = r.rbeta(1, self._a, self._b)#[0]
        else:
            self._underlyingPval = r.runif(1)#[0]
        #print fromH1, self._underlyingPval   
        
    def __iter__(self):
        'Provides a generator giving True if sample was simulated to be more extreme than observation, else False'
        while True:
            #sample = r.runif(1)#[0]
            sample = random.random()
            extreme = (sample < self._underlyingPval)
            #print extreme, sample , self._underlyingPval
            yield extreme
        
class ExtremeSampleCounter(object):
    def __init__(self, extremeOrNotSampleGenerator, maxNumSamples = 1000, h=20, fdrThreshold=0.1):
        'h is here how many extreme samples before stopping sampling according to sequential MC'
        self._extremeOrNotSampleGenerator = extremeOrNotSampleGenerator
        self._h = h
        self._maxNumSamples = maxNumSamples
        self._fdrThreshold = fdrThreshold
        self._extremeCount = 0
        self._notExtremeCount = 0
        self.fdrVal = None
        
    def setFdrThreshold(self, fdrThreshold):
        self._fdrThreshold = fdrThreshold
        
    def getPandQvalsTriple(self):
        return self._extremeOrNotSampleGenerator._underlyingPval, self.getPvalEstimate(), self.fdrVal
    
    def addSamples(self,n):
        count = 0
        for extreme in self._extremeOrNotSampleGenerator:
            #print extreme,
            if extreme:
                self._extremeCount+=1
            else:
                self._notExtremeCount+=1
            count+=1
            if count>=n:
                break
        self.fdrVal = None
        
    def getPvalEstimate(self):
        if self.getTotalNumSamples() == 0:
            return 1.0
        
        #return max(self._extremeCount,1) *1.0 / self.getTotalNumSamples()
        return float(self._extremeCount+1) / (self.getTotalNumSamples()+1)
    
    def enoughExtremeValues(self):
        return self._extremeCount >= self._h
        
    def getClassificationType(self):
        assert self._fdrThreshold is not None and self.fdrVal is not None
        reject = self.fdrVal<=self._fdrThreshold
        truth = self._extremeOrNotSampleGenerator._fromH1
        if truth and reject:
            return 'tp'
        elif truth and not reject:
            return 'fn'
        elif not truth and reject:
            return 'fp'
        elif not truth and not reject:
            return 'tn'
        
    def getTotalNumSamples(self):
        return self._extremeCount + self._notExtremeCount
    
    def isFdrRejected(self):
        return self._fdrThreshold is not None and self.fdrVal is not None and self.fdrVal<=self._fdrThreshold
    
    def isDetermined(self, useH=True, useFdr=True, useMaxNumSamples=True):
        return (useH and self._h is not None and self.enoughExtremeValues() \
            or (useFdr and self.isFdrRejected()) \
            or (useMaxNumSamples and self._maxNumSamples is not None and self.getTotalNumSamples() >= self._maxNumSamples) )
    
    def __cmp__(self, other):
        return cmp(self._extremeOrNotSampleGenerator._underlyingPval, other._extremeOrNotSampleGenerator._underlyingPval)
    
class MultipleTestCollection(object):
    ESTIMATE_PI0 = False
    SIMULTANOUS_FDR_STOPPING_CRITERION = True
    
    def __init__(self, numH0Tests, numH1Tests,maxNumSamples, h, fdrThreshold,a,b ):#, fdrThreshold=0.2):
        self._numH0Tests = numH0Tests
        self._numH1Tests = numH1Tests
        #self._fdrThreshold = fdrThreshold
        self._sampleCounters = []
        for i in range(numH0Tests):
            self._sampleCounters.append( ExtremeSampleCounter(ExtremeOrNotSampleGenerator(False,a,b), maxNumSamples, h, fdrThreshold ) )
        for i in range(numH1Tests):
            self._sampleCounters.append( ExtremeSampleCounter(ExtremeOrNotSampleGenerator(True,a,b) , maxNumSamples, h, fdrThreshold ) )
        
    def setFdrThresholdAtAllCounters(self, fdrThreshold):
        for counter in self._sampleCounters:
            counter.setFdrThreshold(fdrThreshold)
            
    def addSamples(self,n):
        for counter in self._sampleCounters:
            if not counter.isDetermined(useFdr=(not self.SIMULTANOUS_FDR_STOPPING_CRITERION)): #don't stop sampling those under fdr threshold individually (until all are ready..)
                counter.addSamples(n)
                
    def getTotalNumRejected(self):
        return sum(1 if counter.isFdrRejected() else 0 for counter in self._sampleCounters)
        
    def getClassificationSummaries(self):
        summary = {'tp':0, 'fp':0, 'tn':0, 'fn':0}
        for counter in self._sampleCounters:
            summary[ counter.getClassificationType() ] +=1
        return summary
            
        
    def getTotalNumSamples(self):
        return sum(counter.getTotalNumSamples() for counter in self._sampleCounters)
    
    def allTestsAreDetermined(self):
        #fdrVals = self.getFdrVals()
        #stoppedByH = [counter.enoughExtremeValues() for counter in self._sampleCounters]

        #assert len(stoppedByH) == len(fdrVals) 
        #return all( (fdrVals[i]<self._fdrThreshold or stoppedByH[i]) for i in range(len(fdrVals)) )
        self.updateFdrValsOfCounters()
        return all( counter.isDetermined() for counter in self._sampleCounters)
    
    def writeAllPandQVals(self, outF):
        outF.write('#'+'\t'.join(['Underlying p','Estimated p','Estimated q','Num samples','NumExtremeSamples'])+ os.linesep )
        for test in sorted(self._sampleCounters):
            outF.write( '\t'.join(['%.5f'%num for num in test.getPandQvalsTriple()] + [str(test.getTotalNumSamples()), str(test._extremeCount)]) + os.linesep )

    def makeAllPandQValsFigure(self):
        underlyingP, estimatedP, estimatedQ = zip(*[test.getPandQvalsTriple() for test in sorted(self._sampleCounters)])
        #print 'underlyingP: ',underlyingP
        rpy1.plot(rpy1.unlist(underlyingP), ylim=r.unlist([0,1]), type='l', xlab='Tests', ylab='P/Q-value',col='black' )
        rpy1.lines(rpy1.unlist(estimatedP), col='red' )
        rpy1.lines(rpy1.unlist(estimatedQ), col='green' )
        rpy1.legend('topleft',['underlyingP','estimatedP','estimatedQ'],col=['black','red','green'],lty=1)

    def makeNumSamplesFigure(self):
        numSamples = [test.getTotalNumSamples() for test in sorted(self._sampleCounters)]
        numExtremes= [test._extremeCount for test in sorted(self._sampleCounters)]
        r.plot(r.unlist(numSamples), type='l', xlab='Tests', ylab='Num samples', col='black' )
        r.lines(r.unlist(numExtremes), col='green')
        rpy1.legend('topleft',['numSamples','numExtremeSamples'],col=['black','green'],lty=1)
                                                            
    def getFdrVals(self):
        adjustMethod = 'fdr'
        pvals = [counter.getPvalEstimate() for counter in self._sampleCounters]
        #r('library(pi0)') #assumed that this has been done before..
        #if self.ESTIMATE_PI0:
        #    if self.ESTIMATE_PI0 == 'Convest':
        #        pi0 = r.convest(pvals)
        #    elif self.ESTIMATE_PI0 == 'Histf1':
        #        pi0 = r.histf1(pvals)
        #    elif self.ESTIMATE_PI0 == 'Pounds&Cheng':
        #        pi0 = min(1.0, mean( [p for p in pvals if not numpy.isnan(p)] )*2.0)                
        #        #r('histf1SeqPerm <- function(p) {histf1(p,seq.perm=TRUE)}')
        #        #pi0 = r.histf1SeqPerm(pvals)
        #    else:
        #        raise Exception('Unvalid self.ESTIMATE_PI0: ' + str(self.ESTIMATE_PI0))
        #else:
        #    pi0 = 1
        #fdrVals = r.fdr(pvals, pi0)
        fdrVals = McFdr.adjustPvalues(pvals, self.ESTIMATE_PI0, False)
        #fdrVals = r('p.adjust')(r.unlist(pvals), adjustMethod)
        if type(fdrVals) in [float,int]:
            fdrVals = [fdrVals]
        return fdrVals
    
    def updateFdrValsOfCounters(self):
        fdrVals = self.getFdrVals()
        for i in range(len(self._sampleCounters)):
            self._sampleCounters[i].fdrVal = fdrVals[i]
            
            
class Simulator(object):
    NUM_SAMPLES_PER_CHUNK = 1
    NUM_SAMPLES_INITIALLY = 100 #minimum number of samples. Does not need to check anything before this..
    
    def __init__(self, maxNumSamples, h, fdrThreshold,a,b, postFdrThreshold, galaxyFn=None):
        self._h = h
        self._maxNumSamples = maxNumSamples
        self._fdrThreshold = fdrThreshold
        self._postFdrThreshold = postFdrThreshold
        self._a = a
        self._b = b
        self._galaxyFn = galaxyFn
        
    def singleSimulation(self, numH0, numH1, replicateIndex, verbose=False):
        tests = MultipleTestCollection(numH0, numH1, self._maxNumSamples, self._h, self._fdrThreshold,self._a,self._b)
        tests.addSamples(self.NUM_SAMPLES_INITIALLY)
        while not tests.allTestsAreDetermined():            
            tests.addSamples(self.NUM_SAMPLES_PER_CHUNK)
            #if verbose:
                #print tests.getTotalNumSamples()
        #As sampling is now anyway over, we set fdrThreshold to a threshold used after computations are finished (i.e. affects final rejection/acception, but not stopping of samples)
        tests.setFdrThresholdAtAllCounters(self._postFdrThreshold)
        
        #print 'FINALLY, #samples: ',
        if self._galaxyFn is not None:
            if self._h is None:
                scheme = 'Basic'
            elif self._fdrThreshold is None:
                scheme = 'Sequential'
            else:
                scheme = 'McFdr'
            staticFile = GalaxyRunSpecificFile([scheme,str(numH1),str(replicateIndex),'PandQvals.txt'], self._galaxyFn)              
            tests.writeAllPandQVals(staticFile.getFile() )                        
            linkToRaw = staticFile.getLink('Raw p and q-vals') + ' under %s scheme with %i true H1, (replication %i)' % (scheme, numH1, replicateIndex)
            
            figStaticFile = GalaxyRunSpecificFile([scheme,str(numH1),str(replicateIndex),'PandQvals.png'], self._galaxyFn)
            figStaticFile.openRFigure()
            tests.makeAllPandQValsFigure()
            figStaticFile.closeRFigure()
            linkToFig = figStaticFile.getLink(' (p/q-figure) ') + '<br>'

            figNumSamplesStaticFile = GalaxyRunSpecificFile([scheme,str(numH1),str(replicateIndex),'NumSamples.png'], self._galaxyFn)
            figNumSamplesStaticFile.openRFigure()
            tests.makeNumSamplesFigure()
            figNumSamplesStaticFile.closeRFigure()
            linkToNumSamplesFig = figNumSamplesStaticFile.getLink(' (numSamples-figure) ') + '<br>'

            catalogStaticFile = GalaxyRunSpecificFile([str(numH1),'cat.html'], self._galaxyFn)
            catalogStaticFile.writeTextToFile(linkToRaw + linkToFig + linkToNumSamplesFig, mode='a')

                        
        #if verbose:
            #print sorted(tests.getFdrVals())
            #print 'NumS ign Below 0.2: ', sum([1 if t<0.2 else 0 for t in tests.getFdrVals()])
        #return tests.getTotalNumSamples(), tests.getTotalNumRejected()
        return tests.getTotalNumSamples(), tests.getTotalNumRejected(), tests.getClassificationSummaries()
    
    def replicatedSimulations(self, numH0, numH1, numReplications=10):
        numSamples = []
        numRejected = []
        classificationSummaries = []
        for i in range(numReplications):
            samples, rejected, classificationSummary = self.singleSimulation(numH0, numH1, i)
            numSamples.append( samples )
            numRejected.append(rejected)
            classificationSummaries.append(classificationSummary)
            
        return sum(numSamples)*1.0/numReplications, sum(numRejected)*1.0/numReplications, dictAvg(classificationSummaries)
            
    def numSamplesAsFunctionOfNumH1(self, totalNumTests, stepSize=1, numReplications=10):
        samplesForNumH1 = {}
        numRejectedForNumH1 = {}
        classificationSummariesForNumH1 = {}
        if type(stepSize) is int:
            allNumH1s = range(0,totalNumTests+1,stepSize)
        elif type(stepSize) is list:
            allNumH1s = stepSize
        for numH1 in allNumH1s:
            numH0 = totalNumTests - numH1
            samplesForNumH1[numH1], numRejectedForNumH1[numH1], classificationSummariesForNumH1[numH1] = self.replicatedSimulations(numH0, numH1, numReplications) #FUNKER DETTE?

            #if self._galaxyFn is not None:
            #    catalogStaticFile = GalaxyRunSpecificFile([str(numH1),'cat.html'], self._galaxyFn)
            #    print catalogStaticFile.getLink( 'Tests with #True H1s=%i' % numH1 ), '<br>'
                
                #catalogStaticFile.writeTextToFile(link, mode='a')            

        sortedKeys = sorted(samplesForNumH1.keys()) 
        print 'numH1s: ', ','.join([str(key) for key in sortedKeys])
        print 'numSamples: ', ','.join([str(samplesForNumH1[key]) for key in sortedKeys])
        #r.plot(r.unlist(sortedKeys), r.unlist([samplesForNumH1[key] for key in sortedKeys]))
        #return sortedKeys, [samplesForNumH1[key] for key in sortedKeys], [numRejectedForNumH1[key] for key in sortedKeys]
        #returns keys, samples, numRejected, numType1Errors, numType2Errors        
        return sortedKeys, [samplesForNumH1[key] for key in sortedKeys], [numRejectedForNumH1[key] for key in sortedKeys], [classificationSummariesForNumH1[key]['fp'] for key in sortedKeys], [classificationSummariesForNumH1[key]['fn'] for key in sortedKeys]
        
class Experiment:
    @staticmethod
    def analyzeNumRejectedDistribution(maxNumSamples,h, fdrThreshold, totalNumTests, totalNumH1Tests, numReplications,a,b, galaxyFn=None):
        numRej = []
        texts = []

        #estimate time use:
        print '(estimating run time..)'
        prevTime= time.time()
        #Experiment._analyzeNumRejectedDistribution(maxNumSamples, None, None, fdrThreshold, totalNumTests, totalNumH1Tests, 1,a,b, galaxyFn)
        Experiment._analyzeNumRejectedDistribution(maxNumSamples, None, None, fdrThreshold, 1, 1, 1,a,b, galaxyFn)
        baseMeasure = time.time() - prevTime
        withOnlyMaxNumEstimate = baseMeasure * totalNumTests * numReplications
        #print 'Estimated running time: between %i and %i seconds.' % (withOnlyMaxNumEstimate, withOnlyMaxNumEstimate*3)
        print 'Estimated running time: around %i seconds. (%.1f hours)' % (withOnlyMaxNumEstimate, withOnlyMaxNumEstimate/3600.0)


        for x,y,z,simult,text in [ [maxNumSamples, None, None,True,'Basic'], [maxNumSamples, h, None,True,'Sequential'], [maxNumSamples, h, fdrThreshold,True,'McFdr Simultanous'], [maxNumSamples, h, fdrThreshold,False,'McFdr Individual']]:
            print text, ':'
            MultipleTestCollection.SIMULTANOUS_FDR_STOPPING_CRITERION = simult
            numRej.append( Experiment._analyzeNumRejectedDistribution(x,y,z, fdrThreshold, totalNumTests, totalNumH1Tests, numReplications,a,b, galaxyFn) )
            texts.append(text)
        plotStaticFile = GalaxyRunSpecificFile(['numRej.png'],galaxyFn)
        plotStaticFile.plotRLines(range(len(numRej[0])), numRej, xlab='Sorted simulations', ylab='num Rejected', legend=texts)
        print plotStaticFile.getLink('Cumulative distribution')
        
    @staticmethod
    def _analyzeNumRejectedDistribution(maxNumSamples,h, fdrThreshold, postFdrThreshold, totalNumTests, totalNumH1Tests, numReplications,a,b, galaxyFn=None):
        numRejected = []
        for replicateIndex in range(numReplications):
            #classificationSummaries = Simulator(maxNumSamples, h, fdrThreshold, a,b,postFdrThreshold).replicatedSimulations(totalNumTests-totalNumH1Tests, totalNumH1Tests, numReplications)[-1]
            classificationSummaries = Simulator(maxNumSamples, h, fdrThreshold, a,b,postFdrThreshold).singleSimulation(totalNumTests-totalNumH1Tests, totalNumH1Tests,replicateIndex)[-1]
            
            cs = classificationSummaries
            numRejected.append(cs['tp']+cs['fp'])
        numRejected = sorted(numRejected)
        print numRejected
        return numRejected
        #sortedKeys, mcFdrCutoff, mcFdrNumRejected, mcFdrType1Errors, mcFdrType2Errors  = Simulator(maxNumSamples, h, fdrThreshold,a,b,fdrThreshold, galaxyFn).numSamplesAsFunctionOfNumH1(totalNumTests, [totalNumH1Tests], numReplications)
        
    @staticmethod
    def compareCutoffSchemes(maxNumSamples, h, fdrThreshold, totalNumTests, stepSize, numReplications,a,b, galaxyFn=None):
        print '<PRE>'
        print 'Comparing cutoff schemes with parameters: maxNumSamples=%i, h=%i, fdrThreshold=%.2f, totalNumTests=%i, numReplications=%i' % (maxNumSamples, h, fdrThreshold, totalNumTests, numReplications)
        print 'stepSize: ',stepSize
        print 'H1 p-values drawn from beta with a=%.3f and b=%.3f' % (a,b)
        print 'Minimum achieveable p-value is %.5f, which gives minimum Bonferroni-corrected p-value of %.5f (compares to a fdr threshold of %.2f)' % (1.0/maxNumSamples, (1.0/maxNumSamples)*totalNumTests, fdrThreshold)
        
        #estimate time use:
        prevTime= time.time()
        Simulator(maxNumSamples, None, None,a,b,fdrThreshold).numSamplesAsFunctionOfNumH1( 1, 1, 1)
        baseMeasure = time.time() - prevTime
        if type(stepSize)==int:
            numSteps = len(range(0,totalNumTests+1,stepSize))
        elif type(stepSize)==list:
            numSteps = len(stepSize)
        withOnlyMaxNumEstimate = baseMeasure * totalNumTests * numSteps * numReplications
        #print 'Estimated running time: between %i and %i seconds.' % (withOnlyMaxNumEstimate, withOnlyMaxNumEstimate*3)
        print 'Estimated running time: around %i seconds. (%.1f hours)' % (withOnlyMaxNumEstimate, withOnlyMaxNumEstimate/3600.0)
        
        sortedKeys, onlyMaxCutoff, onlyMaxNumRejected, onlyMaxType1Errors, onlyMaxType2Errors = Simulator(maxNumSamples, None, None,a,b,fdrThreshold, galaxyFn).numSamplesAsFunctionOfNumH1( totalNumTests, stepSize, numReplications)
        sortedKeys, seqMcCutoff, seqMcNumRejected, seqMcType1Errors, seqMcType2Errors  = Simulator(maxNumSamples, h, None,a,b,fdrThreshold, galaxyFn).numSamplesAsFunctionOfNumH1(totalNumTests, stepSize, numReplications)
        sortedKeys, mcFdrCutoff, mcFdrNumRejected, mcFdrType1Errors, mcFdrType2Errors  = Simulator(None, h, fdrThreshold,a,b,fdrThreshold, galaxyFn).numSamplesAsFunctionOfNumH1(totalNumTests, stepSize, numReplications)
        maxY = max( max(s) for s in [onlyMaxCutoff, seqMcCutoff, mcFdrCutoff])
        #minY = min( min(s) for s in [onlyMaxCutoff, seqMcCutoff, McFdrCutoff])
        minY=0

        print 'Time spent: ',time.time() - prevTime, ' secs'
        print '</PRE>'
        
        #plotStaticFile.getDiskPath(True)
        if galaxyFn is not None:
            #print 'Generating aggregate McFdr simulation figures'
            plotStaticFile = GalaxyRunSpecificFile(['mainPlot.png'],galaxyFn)
            if type(stepSize) is int:
                allNumH1s = range(0,totalNumTests+1,stepSize)
            elif type(stepSize) is list:
                allNumH1s = stepSize
            for numH1 in allNumH1s:
                catalogStaticFile = GalaxyRunSpecificFile([str(numH1),'cat.html'], galaxyFn)
                print catalogStaticFile.getLink( 'Tests with #True H1s=%i' % numH1 ), '<br>'

            #plotStaticFile.openRFigure()
            #r.png(filename=plotFn, height=600, width=800, units='px', pointsize=12, res=72)
            #r.plot(r.unlist(sortedKeys), r.unlist(onlyMaxCutoff), ylim=r.unlist([minY,maxY]), type='l', xlab='Number of true H1s', ylab='Total MC samples' , col='black')
            #r.lines(r.unlist(sortedKeys), r.unlist(seqMcCutoff), col='red' )
            #r.lines(r.unlist(sortedKeys), r.unlist(mcFdrCutoff), col='green' )
            #r.legend('topleft',['BasicMc','SeqMc','McFdr'],col=['black','red','green'],lty=1)
            plotStaticFile.plotRLines(sortedKeys, [onlyMaxCutoff,seqMcCutoff,mcFdrCutoff], xlab='Number of true H1s', ylab='Total MC samples', legend=['BasicMc','SeqMc','McFdr'])
            #r('dev.off()')
            #plotStaticFile.closeRFigure()

            print plotStaticFile.getLink('View main plot') + ' of sumSamples as function of #H1s.', '<br>'

            numRejectedPlotStaticFile = GalaxyRunSpecificFile(['secondaryPlot.png'],galaxyFn)
            numRejectedPlotStaticFile.plotRLines(sortedKeys, [onlyMaxNumRejected,seqMcNumRejected,mcFdrNumRejected],xlab='Number of true H1s', ylab='Num rejected tests',legend=['BasicMc','SeqMc','McFdr'])
            #numRejectedPlotStaticFile.openRFigure()
            #r.png(filename=plotFn, height=600, width=800, units='px', pointsize=12, res=72)
            #r.plot(r.unlist(sortedKeys), r.unlist(onlyMaxNumRejected), ylim=r.unlist([0,totalNumTests]), type='l', xlab='Number of true H1s', ylab='Num rejected tests',col='black' )
            #r.lines(r.unlist(sortedKeys), r.unlist(seqMcNumRejected), col='red' )
            #r.lines(r.unlist(sortedKeys), r.unlist(mcFdrNumRejected), col='green' )
            #r.lines(r.unlist(sortedKeys), r.unlist(sortedKeys), col='black', lty='dotted' ) #As this corresponds to perfect estimation..
            #r.legend('topleft',['BasicMc','SeqMc','McFdr','NumFromH1'],col=['black','red','green','black'],lty=[1,1,1,2])
            #r('dev.off()')
            #numRejectedPlotStaticFile.closeRFigure()
            print numRejectedPlotStaticFile.getLink('View secondary plot') + ' of #true H1s vs #tests rejected.', '<br>'

            #Classification errors
            classificationErrorPlotStaticFile = GalaxyRunSpecificFile(['errors.png'],galaxyFn)
            classificationErrorPlotStaticFile.openRFigure()
            yMax = max( max(x) for x in [mcFdrType2Errors,mcFdrType1Errors,seqMcType2Errors,seqMcType1Errors,onlyMaxType2Errors,onlyMaxType1Errors ])
            #r.png(filename=plotFn, height=600, width=800, units='px', pointsize=12, res=72)
            r.plot(r.unlist(sortedKeys), r.unlist(onlyMaxType1Errors), ylim=r.unlist([0,yMax]), type='l', xlab='Number of true H1s', ylab='Type 1/2 errors',col='black' )
            r.lines(r.unlist(sortedKeys), r.unlist(onlyMaxType2Errors), col='black', lty='dotted' )
            r.lines(r.unlist(sortedKeys), r.unlist(seqMcType1Errors), col='red' )
            r.lines(r.unlist(sortedKeys), r.unlist(seqMcType2Errors), col='red', lty='dotted' )
            r.lines(r.unlist(sortedKeys), r.unlist(mcFdrType1Errors), col='green' )
            r.lines(r.unlist(sortedKeys), r.unlist(mcFdrType2Errors), col='green', lty='dotted' )
            rpy1.legend('topleft',['BasicMcType1','SeqMcType1','McFdrType1','BasicMcType2','SeqMcType2','McFdrType2'],col=['black','red','green','black','red','green'],lty=[1,1,1,2,2,2])
            #r('dev.off()')
            classificationErrorPlotStaticFile.closeRFigure()
            print classificationErrorPlotStaticFile.getLink('View Type 1/2 error plot') + ' as function of number of true H1.', '<br>'

            #Classification errors
            onlyMaxAccuracy = [ sum(errors)*1.0/totalNumTests for errors in zip(onlyMaxType1Errors, onlyMaxType2Errors)]
            seqMcAccuracy = [ sum(errors)*1.0/totalNumTests for errors in zip(seqMcType1Errors, seqMcType2Errors)]
            mcFdrAccuracy = [ sum(errors)*1.0/totalNumTests for errors in zip(mcFdrType1Errors, mcFdrType2Errors)]
            
            accuracyPlotStaticFile = GalaxyRunSpecificFile(['accuracy.png'],galaxyFn)
            accuracyPlotStaticFile.openRFigure()
            yMax = 0.2 #just set ad hoc here..
            #r.png(filename=plotFn, height=600, width=800, units='px', pointsize=12, res=72)
            r.plot(r.unlist(sortedKeys), r.unlist(onlyMaxAccuracy), ylim=r.unlist([0,yMax]), type='l', xlab='Number of true H1s', ylab='Accuracy',col='black' )
            r.lines(r.unlist(sortedKeys), r.unlist(seqMcAccuracy), col='red' )
            r.lines(r.unlist(sortedKeys), r.unlist(mcFdrAccuracy), col='green' )
            rpy1.legend('topleft',['BasicMc','SeqMc','McFdr','NumFromH1'],col=['black','red','green'],lty=[1,1,1])
            #r('dev.off()')
            accuracyPlotStaticFile.closeRFigure()
            print accuracyPlotStaticFile.getLink('View accuracy plot') + ' as function of number of true H1.', '<br>'
                        
            #False positive rates
            onlyMaxFpr= [ float(fp)/pos if pos!=0 else 0 for fp,pos in zip(onlyMaxType1Errors, onlyMaxNumRejected)]
            seqMcFpr= [ float(fp)/pos if pos!=0 else 0 for fp,pos in zip(seqMcType1Errors, seqMcNumRejected)]
            mcFdrFpr= [ float(fp)/pos if pos!=0 else 0 for fp,pos in zip(mcFdrType1Errors, mcFdrNumRejected)]
            
            fprPlotStaticFile = GalaxyRunSpecificFile(['fpr.png'],galaxyFn)
            fprPlotStaticFile.plotRLines(sortedKeys, [onlyMaxFpr, seqMcFpr, mcFdrFpr], legend=['BasicMc','SeqMc','McFdr'])
            print fprPlotStaticFile.getLink('View FPR plot') + ' as function of number of true H1.', '<br>'
             
        #r.show()
        
#Experiment.compareCutoffSchemes(1000,20,0.1,100,5,5,0.5,25)
#Experiment.compareCutoffSchemes(100,20,0.1,100,5,5,0.5,25)
#Experiment.compareCutoffSchemes(1000,20,0.1,100,5,1)
#Experiment.compareCutoffSchemes(1000,20,0.1,10,5,10)
#Experiment.compareCutoffSchemes(1000,20,0.1,1,1,1,0.5,25, False)
#1+''
#Simulator.numSamplesAsFunctionOfNumH1(10,1,1)
#print '95,5: ',Simulator.replicatedSimulations(95,5,10)
#print '5,95: ',Simulator.replicatedSimulations(5,95,10)
#simulate(1,0)

#print 'simulate(95,5)'
#simulate(95,5)
#
#print 'simulate(50,50)'
#simulate(50,50)
#
#print 'simulate(5,95)'
#simulate(5,95)
        
