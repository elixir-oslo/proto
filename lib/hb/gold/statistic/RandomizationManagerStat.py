from quick.statistic.McFdr import McFdr
from numpy import isnan,array, median
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from config.Config import DebugConfig
from gold.track.PermutedSegsAndIntersegsTrack import PermutedSegsAndIntersegsTrack
from gold.track.PermutedSegsAndSampledIntersegsTrack import PermutedSegsAndSampledIntersegsTrack
from gold.track.ShuffledMarksTrack import ShuffledMarksTrack
from gold.track.SegsSampledByIntensityTrack import SegsSampledByIntensityTrack
from gold.track.RandomGenomeLocationTrack import RandomGenomeLocationTrack
#from quick.track.SegsSampledByDistanceToReferenceTrack import SegsSampledByDistanceToReferenceTrack
from quick.track.SegsSampledByDistanceToReferenceTrack import SegsSampledByDistanceToReferenceTrack
from gold.util.CompBinManager import CompBinManager
from gold.util.CustomExceptions import ArgumentValueError
from gold.application.LogSetup import logMessage
import logging
from gold.statistic.OverlapAgnosticCountElementStat import OverlapAgnosticCountElementStat
from collections import OrderedDict
from copy import copy
#from quick.application.parallel.JobWrapper import RandomizationManagerStatJobWrapper
#from quick.application.parallel.JobHandler import JobHandler

class RandomizationManagerStat(MagicStatFactory):
    pass        
    @classmethod
    def getDescription(cls):
        return '''
        P-value is obtained by Monte Carlo testing, based on parameters giving the minimum number of samples (minSamples), 
        the maximum number of samples (maxSamples), a <a href=''>sequential MC<\a> threshold (m),
        and a <a href=''>MCFDR<\a> threshold on false discovery rate (fdrTreshold).
        At default settings, the MCFDR scheme (see paper linked to above) is used to automatically tune the number of samples
        (when minSamples < maxSamples and fdrTreshold > 0).
        If minSamples < maxSamples, but fdrTreshold is set to zero, this amounts to basic sequential MC.
        Finally, if minSamples is set equal to maxSamples, this amounts to standard Monte Carlo testing (with fixed number of samples), regardless of other parameters.
        '''

    @staticmethod    
    def getMcSamplingScheme(kwArgs):
        'Determines the MC sampling scheme used, based on keyword arguments to a statistic function, i.e. those set in an analysisList-entry'
        if not 'numResamplings' in kwArgs:
            return None #no MC
        elif not 'maxSamples' in kwArgs or kwArgs['numResamplings']==kwArgs['maxSamples']:
            return 'Standard MC'
        elif not 'fdrThreshold' in kwArgs or kwArgs['fdrThreshold'] == 0:
            return 'Sequential MC'
        else:
            return 'MCFDR'
        
            
#class RandomizationManagerStatSplittable(Statistic, OnlyGloballySplittable):
#    IS_MEMOIZABLE = False
#    
#    def _createChildren(self):                
#        raise SplittableStatNotAvailableError
#
#    def _compute(self):
#        raise SplittableStatNotAvailableError

class RandomizationManagerStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    PVAL_KEY = 'P-value'
    M_KEY = 'NumMoreExtremeThanObs'
    NUM_SAMPLES_KEY = 'NumResamplings'
    #NUM_SAMPLES_PER_CHUNK = 100
    NUM_SAMPLES_PER_CHUNK_KEY = 'numSamplesPerChunk'
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@classmethod
    #@repackageException(Exception, ShouldNotOccurError)        
    def validateAndPossiblyResetLocalResults(cls, stats):
        if len(stats)==0:
            return 0

        mt = stats[0]._kwArgs.get('mThreshold')
        ft = stats[0]._kwArgs.get('fdrThreshold')
        ms = stats[0]._kwArgs.get('maxSamples')
        fc = stats[0]._kwArgs.get('fdrCriterion')
        npc = stats[0]._kwArgs.get(cls.NUM_SAMPLES_PER_CHUNK_KEY)
        
        M_THRESHOLD = int(mt) if mt is not None else 20
        FDR_THRESHOLD = float(ft) if ft is not None else 0.1
        if ms is None:
            MAX_SAMPLES = 50000
        elif type(ms) is int:
            MAX_SAMPLES = ms
        elif ms.lower() == 'unlimited':
            MAX_SAMPLES = None
        else:
            MAX_SAMPLES = int(ms)
        cls.NUM_SAMPLES_PER_CHUNK = int(npc) if npc is not None else 100
                
        assert fc in [None, 'individual','simultaneous'], 'fdrCriterion:'+str(fc)
        individualFdr = (fc == 'individual')
        if fc is None:
            logMessage('Warning: empty fdrCriterion, using simultaneous')
        
        import numpy
        
        pvals = range(len(stats))
        allMs = range(len(stats))
        allNumSamples = range(len(stats))
        isInValid = range(len(stats))
        for i,x in enumerate(stats):
            try:
                pvals[i] = x.getResult()[RandomizationManagerStatUnsplittable.PVAL_KEY]
                allMs[i] = x.getResult()[RandomizationManagerStatUnsplittable.M_KEY]
                allNumSamples[i] = x.getResult()[RandomizationManagerStatUnsplittable.NUM_SAMPLES_KEY]
                isInValid[i] = False
            except:
                pvals[i] = None
                allMs[i] = None
                allNumSamples[i] = None
                isInValid[i] = True
        
        
        fdrVals = McFdr.adjustPvalues(pvals, verbose=False)
        
        determinedByM = [M_THRESHOLD is not None and m>=M_THRESHOLD for m in allMs]
        determinedByFdr = [FDR_THRESHOLD is not None and not numpy.isnan(f) and f<FDR_THRESHOLD for f in fdrVals]
        isNanValued = [f is not None and numpy.isnan(f) for f in fdrVals]
        determinedByMaxSamples = [MAX_SAMPLES is not None and n>=MAX_SAMPLES for n in allNumSamples]
        statIndividuallyDetermined = list(any(x) for x in zip(determinedByM,determinedByMaxSamples,isInValid, isNanValued)) #determined by anything except FDR, as the latter is not necessarily handled on a per test level..
        statDeterminedByAnyMeans = list(any(x) for x in zip(statIndividuallyDetermined, determinedByFdr)) #determined individually or by FDR
        assert len(stats) == len(pvals) == len(fdrVals) == len(allMs) == len(determinedByM) == len(determinedByFdr) == len(statIndividuallyDetermined)
        

        for i in range(len(statIndividuallyDetermined)):
            determined = statIndividuallyDetermined[i] or (individualFdr and determinedByFdr[i])
            if not determined:
                if hasattr(stats[i], '_result'):
                    del stats[i]._result
                else:
                    print 'no _result to delete at index %i in stats: '%i #, stats
                    print 'obj details: ',stats[i]._region
                stats[i]._numResamplings += cls.NUM_SAMPLES_PER_CHUNK #get number from mcFdr..

        return sum((1 if not determined else 0) for determined in statDeterminedByAnyMeans)


    def validateAndPossiblyResetGlobalResult(cls, stat):
        mt = stat._kwArgs.get('mThreshold')
        gt = stat._kwArgs.get('globalPvalThreshold')
        ms = stat._kwArgs.get('maxSamples')
        fc = stat._kwArgs.get('fdrCriterion')
        npc = stat._kwArgs.get(cls.NUM_SAMPLES_PER_CHUNK_KEY)
        
        M_THRESHOLD = int(mt) if mt is not None else 20
        GLOBAL_PVAL_THRESHOLD = float(gt) if gt is not None else 0.1
        if ms is None:
            MAX_SAMPLES = 50000
        elif type(ms) is int:
            MAX_SAMPLES = ms
        elif ms.lower() == 'unlimited':
            MAX_SAMPLES = None
        else:
            MAX_SAMPLES = int(ms)
        
        #print 'M_THRESHOLD:%i, FDR_THRESHOLD:%.2f, MAX_SAMPLES:%s' % (M_THRESHOLD,FDR_THRESHOLD,str(MAX_SAMPLES))
        
        
        #print 'min samples:%i, samples per chunk:%i' % (stats[0]._numResamplings, NUM_SAMPLES_PER_CHUNK)
        
        assert fc in [None, 'individual','simultaneous'], 'fdrCriterion:'+str(fc)
        individualFdr = (fc == 'individual')
        #print 'FDR criterion: %s' % fc
        if fc is None:
            logMessage('Warning: empty fdrCriterion, using simultaneous')
        #USE_MC_FDR = True #if false, use only standard sequential MC, without checking q-values
        cls.NUM_SAMPLES_PER_CHUNK = int(npc) if npc is not None else 100
        
        import numpy
        
        #print '<pre>'
        #pvals = [x.getResult()[RandomizationManagerStatUnsplittable.PVAL_KEY] for x in stats]
        #pvals = range(len(stats))
        #allMs = range(len(stats))
        #allNumSamples = range(len(stats))
        #isInValid = range(len(stats))
        #for i,x in enumerate(stats):
        try:
            pval = stat.getResult()[RandomizationManagerStatUnsplittable.PVAL_KEY]
            mVal = stat.getResult()[RandomizationManagerStatUnsplittable.M_KEY]
            numSamples = stat.getResult()[RandomizationManagerStatUnsplittable.NUM_SAMPLES_KEY]
            isInValid = False
        except:
            pval= None
            mVal = None
            numSamples = None
            isInValid = True
            #raise
    
        #print type(pval)
        determinedByM = M_THRESHOLD is not None and mVal>=M_THRESHOLD
        determinedByPval = GLOBAL_PVAL_THRESHOLD is not None and pval is not None and not numpy.isnan(pval) and pval<GLOBAL_PVAL_THRESHOLD
        determinedByMaxSamples = MAX_SAMPLES is not None and numSamples>=MAX_SAMPLES
        isNanValued = pval is not None and numpy.isnan(pval)
        #print 'TEMP statdet1: ',determinedByM, determinedByFdr, determinedByMaxSamples
        statDetermined = any([determinedByM, determinedByPval, determinedByMaxSamples,isInValid, isNanValued])
        #determined by anything except FDR, as the latter is not necessarily handled on a per test level..
        #statDeterminedByAnyMeans = list(any(x) for x in zip(statIndividuallyDetermined, determinedByFdr)) #determined individually or by FDR
        #assert len(stats) == len(pvals) == len(fdrVals) == len(allMs) == len(determinedByM) == len(determinedByFdr) == len(statIndividuallyDetermined)

        if not statDetermined:
            if hasattr(stat, '_result'):
                del stat._result
            else:
                print 'no _result to delete at global level'
                #print 'obj details: ',stats._region
            stat._numResamplings += cls.NUM_SAMPLES_PER_CHUNK #get number from mcFdr..
        #return all(statDeterminedByAnyMeans)
        #returns number of not determined stats..
        #print 'TEMP statdet: ',statDetermined
        return [(1 if not statDetermined else 0), mVal, M_THRESHOLD, pval, GLOBAL_PVAL_THRESHOLD]
        
    def __init__(self, region, track, track2, rawStatistic, randTrackClass=None, assumptions=None, tails=None, numResamplings=2000, randomSeed=None, **kwArgs):
        #print 'TEMP RM:',kwArgs
        if tails==None:
            if 'tail' in kwArgs:
                tailTranslator = {'more':'right-tail', 'less':'left-tail', 'different':'two-tail'}
                tails = tailTranslator[kwArgs['tail']]
                if DebugConfig.VERBOSE:
                    logMessage('Argument tail provided instead of tails to RandomizationManagerStatUnsplittable', level=logging.DEBUG)
            else:
                tails = 'right-tail' # or 'two-tail'?
                logMessage('No tails argument provided to RandomizationManagerStatUnsplittable', level=logging.DEBUG)
        
        if track2 is None:
            self._track2 = None #to allow track2 to be passed on as None to rawStatistics without error. For use by single-track MC-tests..
            
        from gold.util.RandomUtil import getManualSeed, setManualSeed
        if randomSeed is not None and randomSeed != 'Random' and getManualSeed() is None:
            setManualSeed(int(randomSeed))
        
        if 'mcSetupScheme' in kwArgs:
            kwArgs = copy(kwArgs) #to not edit original dict..
            if kwArgs['mcSetupScheme'] != 'custom':
                assert not 'maxSamples' in kwArgs #check that specific values are not redundantly set
            #
        Statistic.__init__(self, region, track, track2, rawStatistic=rawStatistic, randTrackClass=randTrackClass, assumptions=assumptions, tails=tails, numResamplings=numResamplings, randomSeed=randomSeed, **kwArgs)
        #if type(rawStatistic) is str:
        #    from gold.statistic.AllStatistics import STAT_CLASS_DICT
        #    rawStatistic = STAT_CLASS_DICT[rawStatistic]
        
        assert (randTrackClass is None) ^ (assumptions is None) # xor
        if assumptions is not None:
            assert assumptions.count('_') == 1, assumptions
            randTrackClass1, randTrackClass2 = assumptions.split('_')
        else:
            randTrackClass1 = None
            randTrackClass2 = randTrackClass
        
        self._randTrackClass1, self._randTrackClass2 = \
            [ ( globals()[clsDef] if clsDef not in ['None',''] else None ) \
                if isinstance(clsDef, basestring) else clsDef for clsDef in [randTrackClass1, randTrackClass2]]
        
        assert not (randTrackClass1 is None and randTrackClass2 is None)
        for cls in [self._randTrackClass1, self._randTrackClass2]:
            assert cls in [None, PermutedSegsAndSampledIntersegsTrack, \
                           PermutedSegsAndIntersegsTrack, RandomGenomeLocationTrack, SegsSampledByIntensityTrack, ShuffledMarksTrack, SegsSampledByDistanceToReferenceTrack]
            
        #print self._randTrackClass1, self._randTrackClass2
        self._rawStatistic = self.getRawStatisticClass(rawStatistic)
        
        #self._randTrackList = []
        self._tails = tails
        if kwArgs.get('minimal') == True:
            self._numResamplings = 1
            self._kwArgs['maxSamples'] = 1
        else:
            self._numResamplings = int(numResamplings)
        CompBinManager.ALLOW_COMP_BIN_SPLITTING = False
        self._randResults = []
        self._observation = None
        #to load r libraries for McFdr:
        McFdr._initMcFdr()
        
    def _createRandomizedStat(self, i):
        "Creates a randChild where certain tracks are randomized"
        tr1 = self._track if self._randTrackClass1 is None else \
              self._randTrackClass1(self._track, self._region, i, **self._kwArgs)
        
        tr2 = self._track2 if self._randTrackClass2 is None else \
              self._randTrackClass2(self._track2, self._region, i, **self._kwArgs)

        return self._rawStatistic(self._region, tr1, tr2, **self._kwArgs)

    #def createChildren(self):
    #    Statistic.createChildren(self)
    #
    #    if self._track._trackFormatReq is not None and not self._track._trackFormatReq.isDense() and not self._track._trackFormatReq.allowOverlaps():
    #        #self._pointCount1 = CountElementStat(self._region, self._track)
    #        #self._children.append( self._pointCount1 )
    #        #self._pointCount1.createChildren()
    #        self._pointCount1 = self._addChild( CountElementStat(self._region, self._track) )
    #
    #    if self._track2 is not None and self._track2._trackFormatReq is not None and not self._track2._trackFormatReq.isDense() and not self._track2._trackFormatReq.allowOverlaps():
    #        self._pointCount2 = self._addChild( CountElementStat(self._region, self._track2) )
    #    for child in self._children:
    #        child.createChildren()

    def _createChildren(self):                
        self._realChild = self._addChild( self._rawStatistic(self._region, self._track, self._track2, **self._kwArgs) )        
        #logMessage(str(self._track._trackFormatReq)+ ' AND '+str(self._track2._trackFormatReq))
        #if self._track._trackFormatReq is not None and not self._track._trackFormatReq.isDense():
        #if self._track._trackFormatReq is not None and not self._track._trackFormatReq.isDense() and not self._track._trackFormatReq.allowOverlaps():
            #self._pointCount1 = self._addChild( CountElementStat(self._region, self._track) )
        self._pointCount1 = self._addChild( OverlapAgnosticCountElementStat(self._region, self._track) )
        #else:
            #self._pointCount1 = None
        
        #if self._track2._trackFormatReq is not None and not self._track2._trackFormatReq.isDense():
        #if self._track2 is not None and self._track2._trackFormatReq is not None and not self._track2._trackFormatReq.isDense() and not self._track2._trackFormatReq.allowOverlaps():
        #    self._pointCount2 = self._addChild( CountElementStat(self._region, self._track2) )
        if self._track2 is not None:
            self._pointCount2 = self._addChild( OverlapAgnosticCountElementStat(self._region, self._track2) )
        #else:
            #self._pointCount2 = None
        #logMessage('AFTER: '+str(self._track._trackFormatReq)+ ' AND '+str(self._track2._trackFormatReq))

    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)
    def _compute(self):
        #if any([randTrackClass==SegsSampledByIntensityTrack for randTrackClass in [self._randTrackClass1, self._randTrackClass2]]) \
        #    and self._kwArgs.get('trackNameIntensity') in [None,'']:
        #    return None
            
        #from dbgp.client import brk
        #brk(host='localhost', port=9000, idekey='galaxy')

        #print 'computing for reg: ',self._region
        #if VERBOSE:
        #    print [randChild.getResult() for randChild in self._children]
        #try:
        if self._kwArgs.get('minimal') != True and (self._realChild.getResult() is None or isnan(self._realChild.getResult())):
            return None
        
        #TODO: change this to a "is this a parallel run?" check
        #if not USE_PARALLEL or ('minimal' in self._kwArgs and self._kwArgs['minimal']):
        for i in xrange( len(self._randResults), self._numResamplings):
            #print 'computing randChild..'
            #print ',',
            randChild = self._createRandomizedStat(i)
            self._randResults.append( randChild.getResult() ) #only to ensure result is created, will be accessed afterwards..
        #else:
        #    jobWrapper = RandomizationManagerStatJobWrapper(self, seed=self._kwArgs["uniqueId"])
        #    jobHandler = JobHandler(self._kwArgs["uniqueId"], True)
        #    self._randResults = jobHandler.run(jobWrapper)

        #logMessage(','.join([str(x) for x in randResults]))       
        numpyRandResults = array(self._randResults)

        if self._observation is None:
            self._observation = self._realChild.getResult()
            
        if self._kwArgs.get('minimal') == True and (self._observation is None or isnan(self._observation)):
            return None
        
        
        #meanOfNullDistr = 1.0 * sum( randResults ) / \
                             #self._numResamplings
        nonNanNumpyRandResults = numpyRandResults[~isnan(numpyRandResults)]
        assert len(numpyRandResults) == self._numResamplings
        numberOfNonNanRandResults = len(nonNanNumpyRandResults)
        
        meanOfNullDistr = nonNanNumpyRandResults.mean(dtype='float64')
        medianOfNullDistr = median(nonNanNumpyRandResults)
        sdOfNullDistr = nonNanNumpyRandResults.std(dtype='float64')
        #sdCountFromNullOfObs = (observation - meanOfNullDistr) / sdOfNullDistr
        diffObsMean = (self._observation - meanOfNullDistr)
        numMoreExtreme = sum(1 for res in self._randResults \
                         if res >= self._observation )

        #pvalEqual = 1.0 * sum(1 for res in self._randResults \
        #                 if res == self._observation ) / self._numResamplings
        #pvalStrictLeft = 1.0 * sum(1 for res in self._randResults \
        #                 if res < self._observation ) / self._numResamplings
        
        numMoreExtremeRight = sum(1 for res in self._randResults \
                         if res >= self._observation ) 
        numMoreExtremeLeft = sum(1 for res in self._randResults \
                         if res <= self._observation ) 
        if self._tails == 'right-tail':
            numMoreExtreme = numMoreExtremeRight
            tailFactor = 1.0
        elif self._tails == 'left-tail':
            numMoreExtreme = numMoreExtremeLeft
            tailFactor = 1.0
        elif self._tails == 'two-tail':
            numMoreExtreme = min(numMoreExtremeLeft, numMoreExtremeRight)
            tailFactor = 2.0
        else:
            raise ArgumentValueError('Invalid value for tails argument:', self._tails)
        
        # For more info on the formula for calculating p-values:
        # "Permutation P-values should never be zero: calculating exact P-values
        #  when permutations are randomly drawn" (http://www.ncbi.nlm.nih.gov/pubmed/21044043)

        pval = tailFactor * (numMoreExtreme+1) / (self._numResamplings+1)
        pval = min(1.0, pval)
        
        #pvalEqual = 1.0 * sum(1 for res in self._randResults \
        #                 if res == self._observation ) / self._numResamplings
        #pvalStrictRight = 1.0 * sum(1 for res in self._randResults \
        #                 if res > self._observation ) / self._numResamplings
        #pvalStrictLeft = 1.0 * sum(1 for res in self._randResults \
        #                 if res < self._observation ) / self._numResamplings
        #
        #if self._tails == 'right-tail':
        #    pval = pvalStrictRight + pvalEqual
        #elif self._tails == 'left-tail':
        #    pval = pvalStrictLeft + pvalEqual
        #elif self._tails == 'two-tail':
        #    #pval = 2 * min(pvalStrictLeft, pvalStrictRight) + pvalEqual
        #    pval = min(1, 2 * min(pvalStrictLeft+ pvalEqual, pvalStrictRight+ pvalEqual))
        #else:
        #    raise RuntimeError()
        
        #if pval == 0:
            #pval = 1.0 / self._numResamplings
        
        resDict = OrderedDict([(self.PVAL_KEY, pval), ('TSMC_'+self.getRawStatisticMainClassName(), self._observation), ('MeanOfNullDistr', meanOfNullDistr), \
                              ('MedianOfNullDistr', medianOfNullDistr), ('SdNullDistr', sdOfNullDistr), ('DiffFromMean', diffObsMean), (self.NUM_SAMPLES_KEY, self._numResamplings), \
                                ('NumSamplesNotNan', numberOfNonNanRandResults), (self.M_KEY,numMoreExtreme) ])
        
        #if self._pointCount1.getResult() is not None:
        #if self._track._trackFormatReq is not None and not self._track._trackFormatReq.isDense() and not self._track._trackFormatReq.allowOverlaps():
        if hasattr(self, '_pointCount1'):
            numElTr1 = self._pointCount1.getResult()
            if numElTr1<1:
                resDict[self.PVAL_KEY] = None
            resDict.update({'NumPointsTr1':numElTr1})
        #if self._pointCount2.getResult() is not None:
        #if self._track2._trackFormatReq is not None and not self._track2._trackFormatReq.isDense() and not self._track2._trackFormatReq.allowOverlaps():
        if hasattr(self, '_pointCount2'):    
            numElTr2 = self._pointCount2.getResult()
            if numElTr2<1:
                resDict['P-value'] = None
            resDict.update({'NumPointsTr2':numElTr2})
        
        if self._kwArgs.get('includeFullNullDistribution')=='yes':
            resDict['fullNullDistribution'] = ','.join([str(x) for x in nonNanNumpyRandResults])
        assert len(self._randResults) == self._numResamplings
        return resDict
        #except Exception,e:
            #logException(e)
            
    def getRawStatisticMainClassName(self):
        return self._rawStatistic.__name__.replace('Splittable', '').replace('Unsplittable', '')
