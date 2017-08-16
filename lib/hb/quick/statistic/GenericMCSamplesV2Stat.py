from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.util.RandomizationUtils import getRandTrackClassList, createRandomizedTrackStructureStat,\
    getRandTrackClass
from quick.statistic.StatisticV2 import StatisticV2
from collections import OrderedDict
from gold.track.TrackStructure import TrackStructure
from quick.util.debug import DebugUtil
from __builtin__ import str

class GenericMCSamplesV2Stat(MagicStatFactory):
    '''
    Takes in a null model (randomization class), a test statistic (rawStatistic) and a desired number of MC samples (numMcSamples),
    then applies the test statistic (rawStatistic) on data from the null model (randomized by the provided randomization class)
    a pre-specified number of times (numMcSamples)
    Returns a list of MC samples (the resulting test statistic/rawStatistic value per randomized sample)
    '''
    pass

#class GenericMCSamplesStatSplittable(StatisticSumResSplittable):
#    pass
            
class GenericMCSamplesV2StatUnsplittable(StatisticV2):    
    IS_MEMOIZABLE = False #as it should return new random samples each time it is called

    def _init(self, rawStatistic, randTrackStructureClassDict=None, assumptions=None, numMcSamples=1, **kwArgs):
    #def _init(self, rawStatistic, randTrackClassList, numMcSamples, **kwArgs):
        '''
            Randomization strategies are specified per track list in the track structure.
            When set through the assumptions parameter, randomization classes are separate by '_'.
            They correspond to the same order as in @TrackStructure.ALLOWED_KEYS.
            
            E.G. For a track structure with query and reference track lists RandTrackClass1_RandTrackClass2, 
            _RandTrackClass2 and RandTrackClass1_ are all acceptable values of the assumption parameter.
            For a track structure with one (query) track list, only RandTrackClass1_ is an acceptable value.
            
        '''
        self._rawStatistic = self.getRawStatisticClass(rawStatistic)
        self._numMcSamples = int(numMcSamples)
        
        assert (randTrackStructureClassDict is None) ^ (assumptions is None) # xor, corresponding to two alternative specs of the same
        self._randTrackStructureClassDict = OrderedDict()
        if assumptions is not None:
            randTrackClassList = assumptions.split('_')
            for i, randTrackStructureClass in enumerate(getRandTrackClassList(randTrackClassList)):
                self._randTrackStructureClassDict[TrackStructure.ALLOWED_KEYS[i]] = randTrackStructureClass
        else: 
            for key, val in randTrackStructureClassDict.iteritems():
                self._randTrackStructureClassDict[key] = getRandTrackClass(val)
                
        origTSLen = len(self._trackStructure)
        randClassListLen = len(self._randTrackStructureClassDict)
        assert origTSLen >= randClassListLen , 'There are %i randomization classes specified, and only %i track collections in the original track structure' % (randClassListLen, origTSLen)

    
    def _createRandomizedStat(self, i):
        #Refactor the first argument after a better track input handling is in place..
        return createRandomizedTrackStructureStat(self._trackStructure, self._randTrackStructureClassDict, self._rawStatistic, self._region, self._kwArgs, i)
        
    def _compute(self):
        #print 'TEMP1: computing %i samples' % self._numMcSamples
        return [self._createRandomizedStat(i).getResult() for i in range(self._numMcSamples)]                    
    
    def _createChildren(self):
        #Actually just ignored the way it is now. Also consider future simplification.
        #pass
        self._addChild( self._createRandomizedStat(0) )
