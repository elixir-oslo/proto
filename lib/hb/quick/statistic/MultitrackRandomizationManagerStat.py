'''
Created on May 7, 2015

@author: boris
'''


from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.StatisticV2 import StatisticV2
from quick.util.McEvaluators import *
from quick.statistic.McFdrSamplingStat import *
from quick.util.debug import DebugUtil


class MultitrackRandomizationManagerStat(MagicStatFactory):
    '''
    V2
    Handles randomization of multiple tracks. Radnomization strategies for ALL tracks are passed in the argument 
    randomizationStrategies which is a '_' separated string.
    '''
    pass

#class MultitrackRandomizationManagerStatSplittable(StatisticSumResSplittable):
#    pass
            
class MultitrackRandomizationManagerStatUnsplittable(StatisticV2):    
    IS_MEMOIZABLE = False

    def _init(self, evaluatorFunc, mcSamplerClass, tail, rawStatistic, **kwArgs):

        if type(evaluatorFunc) is str:
            evaluatorFunc = globals()[evaluatorFunc]
        self._evaluatorFunc = evaluatorFunc

        if type(mcSamplerClass) is str:
            mcSamplerClass = globals()[mcSamplerClass]
        self._mcSamplerClass = mcSamplerClass
        
        self._tail = tail
        self._rawStatistic = self.getRawStatisticClass(rawStatistic) #just to extract name

    def _compute(self):
        #if not self._children[0].isMcDetermined():
            #return "Undetermined"
        #else:
        return self._evaluatorFunc( self._children[0].getResult(), self._tail, self.getRawStatisticMainClassName() )
    
    def _createChildren(self):
        self._addChild(self._mcSamplerClass(self._region, self._trackStructure, **self._kwArgs) )
        #allUserBins = ...
        #self._globalLevelSampler = self._addChild(self._mcSamplerClass(allUserBins, self._track, self._track2 if hasattr(self, '_track2') else None, **self._kwArgs) )

    def getRawStatisticMainClassName(self):
        return self._rawStatistic.__name__.replace('Splittable', '').replace('Unsplittable', '')
        
    @classmethod
    def validateAndPossiblyResetLocalResults(cls, localManagerObjects):
        localSamplingObjects = [x._children[0] for x in localManagerObjects]
        numNonDetermined = localManagerObjects[0]._children[0].validateAndPossiblyResetLocalResults(localSamplingObjects)
        for i in range(len(localSamplingObjects)):
            if not localSamplingObjects[i].hasResult():
                del localManagerObjects[i]._result
        return numNonDetermined

    def validateAndPossiblyResetGlobalResult(self, dummy):
        res = self._children[0].validateAndPossiblyResetGlobalResult(dummy)
        if res[0]==1:
            #print 'TEMP3'
            del self._result
        return res

    
    
    
    
#     IS_MEMOIZABLE = False
#     PVAL_KEY = 'P-value'
#     M_KEY = 'NumMoreExtremeThanObs'
#     NUM_SAMPLES_KEY = 'NumResamplings'
#     #NUM_SAMPLES_PER_CHUNK = 100
#     NUM_SAMPLES_PER_CHUNK_KEY = 'numSamplesPerChunk'
#     
#     def __init__(self, region, trackStructure, rawStatistic, randTrackClassStructure=None, assumptions=None, tails=None, numResamplings=2000, randomSeed=None, **kwArgs):
#         '''
#         @randTrackClassStructure is a dict that has keys same as track structure. 
#         Each randomization strategy is per track list.
#         @assumtions is a string of '_'-separated randomization strategy class names (which can be the empty string).
#         Exactly one of the two arguments must be passed to the init method.  
#         '''
#         
#         #print 'TEMP RM:',kwArgs
#         if tails==None:
#             if 'tail' in kwArgs:
#                 tailTranslator = {'more':'right-tail', 'less':'left-tail', 'different':'two-tail'}
#                 tails = tailTranslator[kwArgs['tail']]
#                 if DebugConfig.VERBOSE:
#                     logMessage('Argument tail provided instead of tails to RandomizationManagerStatUnsplittable', level=logging.DEBUG)
#             else:
#                 tails = 'right-tail' # or 'two-tail'?
#                 logMessage('No tails argument provided to RandomizationManagerStatUnsplittable', level=logging.DEBUG)
#         
#         from gold.util.RandomUtil import getManualSeed, setManualSeed
#         if randomSeed is not None and randomSeed != 'Random' and getManualSeed() is None:
#             setManualSeed(int(randomSeed))
#         
#         if 'mcSetupScheme' in kwArgs:
#             kwArgs = copy(kwArgs) #to not edit original dict..
#             if kwArgs['mcSetupScheme'] != 'custom':
#                 assert not 'maxSamples' in kwArgs #check that specific values are not redundantly set
#             #
#         StatisticV2.__init__(self, region, trackStructure, rawStatistic=rawStatistic, 
#                              randTrackClassStructure=randTrackClassStructure, assumptions=assumptions, tails=tails, 
#                              numResamplings=numResamplings, randomSeed=randomSeed, **kwArgs)
#         assert (randTrackClassStructure is None) ^ (assumptions is None) # xor
#         if assumptions is not None:
#             '''
#             When assumptions is not None, it means that the randomization classes for the collections in the track structure
#             are sent in as '_' separated string. At least one of the collections needs to be randomized.
#             '''
#             assert len(assumptions.split('_')) > 0, assumptions
#             assert any(assumptions.split('_')), assumptions
#             self._randTrackClassStructure = dict()
#             for i, randTrackClass in enumerate(assumptions.split('_')):
#                 self._randTrackClassStructure[TrackStructure.ALLOWED_KEYS[i]] =\
#                  globals()[randTrackClass] if randTrackClass not in ['None', ''] else None
#         else:
#             self._randTrackClassStructure = randTrackClassStructure
#         
#         for cls in self._randTrackClassStructure.values():
#             assert cls in [None, PermutedSegsAndSampledIntersegsTrack, \
#                            PermutedSegsAndIntersegsTrack, RandomGenomeLocationTrack, SegsSampledByIntensityTrack, ShuffledMarksTrack, SegsSampledByDistanceToReferenceTrack]
#             
#         #print self._randTrackClass1, self._randTrackClass2
#         self._rawStatistic = self.getRawStatisticClass(rawStatistic)
#         
#         #self._randTrackList = []
#         self._tails = tails
#         if kwArgs.get('minimal') == True:
#             self._numResamplings = 1
#             self._kwArgs['maxSamples'] = 1
#         else:
#             self._numResamplings = int(numResamplings)
#         CompBinManager.ALLOW_COMP_BIN_SPLITTING = False
#         self._randResults = []
#         self._observation = None
#         #to load r libraries for McFdr:
#         McFdr._initMcFdr()    
# 
# 
#     def _createRandomizedStat(self, i):
#         randomizedTrackStructure = TrackStructure()
#         for key in self._trackStructure:
#             if key in self._randTrackClassStructure and self._randTrackClassStructure[key]:
#                 randomizedTrackStructure[key] = self._randTrackClassStructure[key](self._trackStructure[key], self._region, i, **self._kwArgs)
#             else:
#                 randomizedTrackStructure[key] = self._trackStructure[key]
#         return self._rawStatistic(self._region, randomizedTrackStructure, **self._kwArgs)
#     
#     def _createChildren(self):
#         self._realChild = self._addChild(self._rawStatistic(self._region, self._trackStructure, **self._kwArgs))
#         self._pointCounts = dict([(key, [OverlapAgnosticCountElementStat(self._region, t) for t in self._trackStructure[key]]) for key in self._trackStructure])
# 
#     @property
#     def _pointCount1(self):
#         if self._pointCounts:
#             return self._pointCounts[TrackStructure.QUERY_KEY][0]
#     
#     @property
#     def _pointCount2(self):
#         if self._pointCounts and TrackStructure.REF_KEY in self._pointCounts:
#             return self._pointCounts[TrackStructure.REF_KEY][0]
#         
#     def _compute(self):
#         if self._kwArgs.get('minimal') != True and (self._realChild.getResult() is None or isnan(self._realChild.getResult())):
#             return None
#         
#         #TODO: change this to a "is this a parallel run?" check
#         #if not USE_PARALLEL or ('minimal' in self._kwArgs and self._kwArgs['minimal']):
#         for i in xrange( len(self._randResults), self._numResamplings):
#             #print 'computing randChild..'
#             #print ',',
#             randChild = self._createRandomizedStat(i)
#             self._randResults.append( randChild.getResult() ) #only to ensure result is created, will be accessed afterwards..
#         #else:
#         #    jobWrapper = RandomizationManagerStatJobWrapper(self, seed=self._kwArgs["uniqueId"])
#         #    jobHandler = JobHandler(self._kwArgs["uniqueId"], True)
#         #    self._randResults = jobHandler.run(jobWrapper)
# 
#         #logMessage(','.join([str(x) for x in randResults]))       
#         numpyRandResults = array(self._randResults)
# 
#         if self._observation is None:
#             self._observation = self._realChild.getResult()
#             
#         if self._kwArgs.get('minimal') == True and (self._observation is None or isnan(self._observation)):
#             return None
#         
#         
#         #meanOfNullDistr = 1.0 * sum( randResults ) / \
#                              #self._numResamplings
#         nonNanNumpyRandResults = numpyRandResults[~isnan(numpyRandResults)]
#         assert len(numpyRandResults) == self._numResamplings
#         numberOfNonNanRandResults = len(nonNanNumpyRandResults)
#         
#         meanOfNullDistr = nonNanNumpyRandResults.mean(dtype='float64')
#         medianOfNullDistr = median(nonNanNumpyRandResults)
#         sdOfNullDistr = nonNanNumpyRandResults.std(dtype='float64')
#         #sdCountFromNullOfObs = (observation - meanOfNullDistr) / sdOfNullDistr
#         diffObsMean = (self._observation - meanOfNullDistr)
#         numMoreExtreme = sum(1 for res in self._randResults \
#                          if res >= self._observation )
# 
#         #pvalEqual = 1.0 * sum(1 for res in self._randResults \
#         #                 if res == self._observation ) / self._numResamplings
#         #pvalStrictLeft = 1.0 * sum(1 for res in self._randResults \
#         #                 if res < self._observation ) / self._numResamplings
#         
#         numMoreExtremeRight = sum(1 for res in self._randResults \
#                          if res >= self._observation ) 
#         numMoreExtremeLeft = sum(1 for res in self._randResults \
#                          if res <= self._observation ) 
#         if self._tails == 'right-tail':
#             numMoreExtreme = numMoreExtremeRight
#             tailFactor = 1.0
#         elif self._tails == 'left-tail':
#             numMoreExtreme = numMoreExtremeLeft
#             tailFactor = 1.0
#         elif self._tails == 'two-tail':
#             numMoreExtreme = min(numMoreExtremeLeft, numMoreExtremeRight)
#             tailFactor = 2.0
#         else:
#             raise ArgumentValueError('Invalid value for tails argument:', self._tails)
#         
#         # For more info on the formula for calculating p-values:
#         # "Permutation P-values should never be zero: calculating exact P-values
#         #  when permutations are randomly drawn" (http://www.ncbi.nlm.nih.gov/pubmed/21044043)
# 
#         pval = tailFactor * (numMoreExtreme+1) / (self._numResamplings+1)
#         pval = min(1.0, pval)
#         
#         #pvalEqual = 1.0 * sum(1 for res in self._randResults \
#         #                 if res == self._observation ) / self._numResamplings
#         #pvalStrictRight = 1.0 * sum(1 for res in self._randResults \
#         #                 if res > self._observation ) / self._numResamplings
#         #pvalStrictLeft = 1.0 * sum(1 for res in self._randResults \
#         #                 if res < self._observation ) / self._numResamplings
#         #
#         #if self._tails == 'right-tail':
#         #    pval = pvalStrictRight + pvalEqual
#         #elif self._tails == 'left-tail':
#         #    pval = pvalStrictLeft + pvalEqual
#         #elif self._tails == 'two-tail':
#         #    #pval = 2 * min(pvalStrictLeft, pvalStrictRight) + pvalEqual
#         #    pval = min(1, 2 * min(pvalStrictLeft+ pvalEqual, pvalStrictRight+ pvalEqual))
#         #else:
#         #    raise RuntimeError()
#         
#         #if pval == 0:
#             #pval = 1.0 / self._numResamplings
#         
#         resDict = OrderedDict([(self.PVAL_KEY, pval), ('TSMC_'+self.getRawStatisticMainClassName(), self._observation), ('MeanOfNullDistr', meanOfNullDistr), \
#                               ('MedianOfNullDistr', medianOfNullDistr), ('SdNullDistr', sdOfNullDistr), ('DiffFromMean', diffObsMean), (self.NUM_SAMPLES_KEY, self._numResamplings), \
#                                 ('NumSamplesNotNan', numberOfNonNanRandResults), (self.M_KEY,numMoreExtreme) ])
#         
#         #if self._pointCount1.getResult() is not None:
#         #if self._track._trackFormatReq is not None and not self._track._trackFormatReq.isDense() and not self._track._trackFormatReq.allowOverlaps():
#         if hasattr(self, '_pointCount1'):
#             numElTr1 = self._pointCount1.getResult()
#             if numElTr1<1:
#                 resDict[self.PVAL_KEY] = None
#             resDict.update({'NumPointsTr1':numElTr1})
#         #if self._pointCount2.getResult() is not None:
#         #if self._track2._trackFormatReq is not None and not self._track2._trackFormatReq.isDense() and not self._track2._trackFormatReq.allowOverlaps():
#         if hasattr(self, '_pointCount2'):    
#             numElTr2 = self._pointCount2.getResult()
#             if numElTr2<1:
#                 resDict['P-value'] = None
#             resDict.update({'NumPointsTr2':numElTr2})
#         
#         if self._kwArgs.get('includeFullNullDistribution')=='yes':
#             resDict['fullNullDistribution'] = ','.join([str(x) for x in nonNanNumpyRandResults])
#         assert len(self._randResults) == self._numResamplings
#         return resDict
# 
#     def validateAndPossiblyResetLocalResults(cls, stats):
#         if len(stats)==0:
#             return 0
# 
#         mt = stats[0]._kwArgs.get('mThreshold')
#         ft = stats[0]._kwArgs.get('fdrThreshold')
#         ms = stats[0]._kwArgs.get('maxSamples')
#         fc = stats[0]._kwArgs.get('fdrCriterion')
#         npc = stats[0]._kwArgs.get(cls.NUM_SAMPLES_PER_CHUNK_KEY)
#         
#         M_THRESHOLD = int(mt) if mt is not None else 20
#         FDR_THRESHOLD = float(ft) if ft is not None else 0.1
#         if ms is None:
#             MAX_SAMPLES = 50000
#         elif type(ms) is int:
#             MAX_SAMPLES = ms
#         elif ms.lower() == 'unlimited':
#             MAX_SAMPLES = None
#         else:
#             MAX_SAMPLES = int(ms)
#         cls.NUM_SAMPLES_PER_CHUNK = int(npc) if npc is not None else 100
#                 
#         assert fc in [None, 'individual','simultaneous'], 'fdrCriterion:'+str(fc)
#         individualFdr = (fc == 'individual')
#         if fc is None:
#             logMessage('Warning: empty fdrCriterion, using simultaneous')
#         
#         import numpy
#         
#         pvals = range(len(stats))
#         allMs = range(len(stats))
#         allNumSamples = range(len(stats))
#         isInValid = range(len(stats))
#         for i,x in enumerate(stats):
#             try:
#                 pvals[i] = x.getResult()[RandomizationManagerStatUnsplittable.PVAL_KEY]
#                 allMs[i] = x.getResult()[RandomizationManagerStatUnsplittable.M_KEY]
#                 allNumSamples[i] = x.getResult()[RandomizationManagerStatUnsplittable.NUM_SAMPLES_KEY]
#                 isInValid[i] = False
#             except:
#                 pvals[i] = None
#                 allMs[i] = None
#                 allNumSamples[i] = None
#                 isInValid[i] = True
#         
#         
#         fdrVals = McFdr.adjustPvalues(pvals, verbose=False)
#         
#         determinedByM = [M_THRESHOLD is not None and m>=M_THRESHOLD for m in allMs]
#         determinedByFdr = [FDR_THRESHOLD is not None and not numpy.isnan(f) and f<FDR_THRESHOLD for f in fdrVals]
#         isNanValued = [f is not None and numpy.isnan(f) for f in fdrVals]
#         determinedByMaxSamples = [MAX_SAMPLES is not None and n>=MAX_SAMPLES for n in allNumSamples]
#         statIndividuallyDetermined = list(any(x) for x in zip(determinedByM,determinedByMaxSamples,isInValid, isNanValued)) #determined by anything except FDR, as the latter is not necessarily handled on a per test level..
#         statDeterminedByAnyMeans = list(any(x) for x in zip(statIndividuallyDetermined, determinedByFdr)) #determined individually or by FDR
#         assert len(stats) == len(pvals) == len(fdrVals) == len(allMs) == len(determinedByM) == len(determinedByFdr) == len(statIndividuallyDetermined)
#         
# 
#         for i in range(len(statIndividuallyDetermined)):
#             determined = statIndividuallyDetermined[i] or (individualFdr and determinedByFdr[i])
#             if not determined:
#                 if hasattr(stats[i], '_result'):
#                     del stats[i]._result
#                 else:
#                     print 'no _result to delete at index %i in stats: '%i #, stats
#                     print 'obj details: ',stats[i]._region
#                 stats[i]._numResamplings += cls.NUM_SAMPLES_PER_CHUNK #get number from mcFdr..
# 
#         return sum((1 if not determined else 0) for determined in statDeterminedByAnyMeans)
# 
# 
#     def validateAndPossiblyResetGlobalResult(cls, stat):
#         mt = stat._kwArgs.get('mThreshold')
#         gt = stat._kwArgs.get('globalPvalThreshold')
#         ms = stat._kwArgs.get('maxSamples')
#         fc = stat._kwArgs.get('fdrCriterion')
#         npc = stat._kwArgs.get(cls.NUM_SAMPLES_PER_CHUNK_KEY)
#         
#         M_THRESHOLD = int(mt) if mt is not None else 20
#         GLOBAL_PVAL_THRESHOLD = float(gt) if gt is not None else 0.1
#         if ms is None:
#             MAX_SAMPLES = 50000
#         elif type(ms) is int:
#             MAX_SAMPLES = ms
#         elif ms.lower() == 'unlimited':
#             MAX_SAMPLES = None
#         else:
#             MAX_SAMPLES = int(ms)
#         
#         #print 'M_THRESHOLD:%i, FDR_THRESHOLD:%.2f, MAX_SAMPLES:%s' % (M_THRESHOLD,FDR_THRESHOLD,str(MAX_SAMPLES))
#         
#         
#         #print 'min samples:%i, samples per chunk:%i' % (stats[0]._numResamplings, NUM_SAMPLES_PER_CHUNK)
#         
#         assert fc in [None, 'individual','simultaneous'], 'fdrCriterion:'+str(fc)
#         individualFdr = (fc == 'individual')
#         #print 'FDR criterion: %s' % fc
#         if fc is None:
#             logMessage('Warning: empty fdrCriterion, using simultaneous')
#         #USE_MC_FDR = True #if false, use only standard sequential MC, without checking q-values
#         cls.NUM_SAMPLES_PER_CHUNK = int(npc) if npc is not None else 100
#         
#         import numpy
#         
#         #print '<pre>'
#         #pvals = [x.getResult()[RandomizationManagerStatUnsplittable.PVAL_KEY] for x in stats]
#         #pvals = range(len(stats))
#         #allMs = range(len(stats))
#         #allNumSamples = range(len(stats))
#         #isInValid = range(len(stats))
#         #for i,x in enumerate(stats):
#         try:
#             pval = stat.getResult()[RandomizationManagerStatUnsplittable.PVAL_KEY]
#             mVal = stat.getResult()[RandomizationManagerStatUnsplittable.M_KEY]
#             numSamples = stat.getResult()[RandomizationManagerStatUnsplittable.NUM_SAMPLES_KEY]
#             isInValid = False
#         except:
#             pval= None
#             mVal = None
#             numSamples = None
#             isInValid = True
#             #raise
#     
#         #print type(pval)
#         determinedByM = M_THRESHOLD is not None and mVal>=M_THRESHOLD
#         determinedByPval = GLOBAL_PVAL_THRESHOLD is not None and pval is not None and not numpy.isnan(pval) and pval<GLOBAL_PVAL_THRESHOLD
#         determinedByMaxSamples = MAX_SAMPLES is not None and numSamples>=MAX_SAMPLES
#         isNanValued = pval is not None and numpy.isnan(pval)
#         #print 'TEMP statdet1: ',determinedByM, determinedByFdr, determinedByMaxSamples
#         statDetermined = any([determinedByM, determinedByPval, determinedByMaxSamples,isInValid, isNanValued])
#         #determined by anything except FDR, as the latter is not necessarily handled on a per test level..
#         #statDeterminedByAnyMeans = list(any(x) for x in zip(statIndividuallyDetermined, determinedByFdr)) #determined individually or by FDR
#         #assert len(stats) == len(pvals) == len(fdrVals) == len(allMs) == len(determinedByM) == len(determinedByFdr) == len(statIndividuallyDetermined)
# 
#         if not statDetermined:
#             if hasattr(stat, '_result'):
#                 del stat._result
#             else:
#                 print 'no _result to delete at global level'
#                 #print 'obj details: ',stats._region
#             stat._numResamplings += cls.NUM_SAMPLES_PER_CHUNK #get number from mcFdr..
#         #return all(statDeterminedByAnyMeans)
#         #returns number of not determined stats..
#         #print 'TEMP statdet: ',statDetermined
#         return [(1 if not statDetermined else 0), mVal, M_THRESHOLD, pval, GLOBAL_PVAL_THRESHOLD]
        


#     def __init__(self, region, track, track2, rawStatistic, randTrackClass=None, assumptions=None, tails=None, numResamplings=2000, randomSeed=None, randomizationStrategies=None, **kwArgs):
#         #TODO: MUST REFACTOR! This is only temporary because we are using RandomizationManagerStatUnsplittable and we need to pass in an arbitrary 
#         #randomization strategy class name to pass the original assertions
#         if randTrackClass == None:
#             randTrackClass = 'PermutedSegsAndIntersegsTrack'
#         ####################
#         
#         RandomizationManagerStatUnsplittable.__init__(region, track, track2, rawStatistic, randTrackClass=randTrackClass, assumptions=assumptions, 
#                                                       tails=tails, numResamplings=numResamplings, randomSeed=randomSeed, **kwArgs)
#         self._tracks = self._collectTracks()
#         if not randomizationStrategies or len(self._tracks) > (randomizationStrategies.count('_') +1):
#             raise ArgumentValueError('randomizationStrategies argument is missing or has the wrong format')
#         self._randomizationStrategies = randomizationStrategies.split('_')
# 
#     def _createRandomizedStat(self, i):
#         from quick.util.RandomizationUtils import createRandomizedStat
#         return createRandomizedStat(self._tracks, self._randomizationStrategies, self._rawStatistic, self._region, self._kwArgs, i)
