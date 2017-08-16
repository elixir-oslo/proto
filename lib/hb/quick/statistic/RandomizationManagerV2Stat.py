from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.util.McEvaluators import *
from quick.statistic.McFdrSamplingStat import *

class RandomizationManagerV2Stat(MagicStatFactory):
    '''
    Does the overall orchestration of Monte Carlo evaluation,
    calling a MCSamplingStat to get a observed test statistic and MC samples,
    then calls an evaluator on them
    '''
    @classmethod
    def getDescription(cls):
        return '''
        P-value is obtained by Monte Carlo testing, based on parameters giving a sampling scheme (naive or McFdr),
        along with parameters related to the selected sampling scheme.
        For naive MC sampling, only a fixed number of samples is specified.
        For McFdr a maximum number of samples (maxSamples), a <a href=''>sequential MC<\a> threshold (m),
        and a <a href=''>MCFDR<\a> threshold on false discovery rate (fdrTreshold).
        (note that if fdrTreshold is set to zero, McFdr amounts to basic sequential MC.
        '''

class RandomizationManagerV2StatUnsplittable(Statistic):
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
        self._addChild(self._mcSamplerClass(self._region, self._track, self._track2 if hasattr(self, '_track2') else None, **self._kwArgs) )
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


            
'''
class ScrapMetalRandomizationManagerStatUnsplittable(Statistic):
    PVAL_KEY = 'P-value'
    M_KEY = 'NumMoreExtremeThanObs'
    NUM_SAMPLES_KEY = 'NumResamplings'
    NUM_SAMPLES_PER_CHUNK_KEY = 'numSamplesPerChunk'

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
        
        from gold.util.RandomUtil import getManualSeed, setManualSeed
        if randomSeed is not None and randomSeed != 'Random' and getManualSeed() is None:
            setManualSeed(int(randomSeed))
        
        if 'mcSetupScheme' in kwArgs:
            kwArgs = copy(kwArgs) #to not edit original dict..
            if kwArgs['mcSetupScheme'] != 'custom':
                assert not 'maxSamples' in kwArgs #check that specific values are not redundantly set
        
    
        CompBinManager.ALLOW_COMP_BIN_SPLITTING = False

    def _createChildren(self):                
        self._pointCount1 = self._addChild( OverlapAgnosticCountElementStat(self._region, self._track) )
        if self._track2 is not None:
            self._pointCount2 = self._addChild( OverlapAgnosticCountElementStat(self._region, self._track2) )

    def _compute(self):
        if self._kwArgs.get('minimal') != True and (self._realChild.getResult() is None or isnan(self._realChild.getResult())):
            return None
        
        #TODO: change this to a "is this a parallel run?" check
        #if not USE_PARALLEL or ('minimal' in self._kwArgs and self._kwArgs['minimal']):
        
        if hasattr(self, '_pointCount1'):
            numElTr1 = self._pointCount1.getResult()
            if numElTr1<1:
                resDict[self.PVAL_KEY] = None
            resDict.update({'NumPointsTr1':numElTr1})

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
'''
