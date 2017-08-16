from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.ThreeWayBpOverlapVegardKaiVersionStat import ThreeWayBpOverlapVegardKaiVersionStat
from quick.util.CommonFunctions import numAsPaddedBinary

class ThreeWayBpOverlapVegardAndKaiVersionWrapperStat(MagicStatFactory):
    pass

#class ThreeWayProportionalBpOverlapStatSplittable(StatisticSumResSplittable):
#    pass
            
        
class ThreeWayBpOverlapVegardAndKaiVersionWrapperStatUnsplittable(Statistic):
    from gold.util.CommonFunctions import repackageException
    from gold.util.CustomExceptions import ShouldNotOccurError
    @repackageException(Exception, ShouldNotOccurError)


    def _convertVennResultToCumulative(self, vennResult, numTracks):
        ourMapping = {}
        cumulativeResult = {}
        from quick.webtools.plot.CreateBpsVennDIagram import CreateBpsVennDIagram #primes = [x for x,dummy in CreateBpsVennDIagram.getPrimeList().values()]
        primes = CreateBpsVennDIagram.getPrimeList().values()
        #         from gold.application.LogSetup import logMessage
        #logMessage('RESULT!!!: ' + str(vennResult))
    #We must iterate the reversed list of combinations to make sure we include all supersets before including a set
        for comb in reversed(range(1, 2 ** numTracks)): #enumerate with binary number corresponding to all subsets
            #print 'COMB ',comb, 2**len(t)
            binary = numAsPaddedBinary(comb, numTracks) #e.g.
            primeIndex = 1
            for tIndex, doInclude in enumerate(binary):
                if doInclude == '1':
                    primeIndex *= primes[tIndex]
            
            ourMapping[binary] = vennResult.get(primeIndex) if vennResult.get(primeIndex) else 0
                
            #update the value by adding all supersets of binary
            cumulativeResult[binary] = ourMapping[binary]
            from quick.util.CommonFunctions import allSupersets
            print 'binary: ', binary
            for superSet in allSupersets(binary):
                print 'superSet: ', superSet
                cumulativeResult[binary] += ourMapping[superSet]
            
        return cumulativeResult
    
    def _compute(self):
        vennResult = self._children[0].getResult()
        from config.Config import MULTIPLE_EXTRA_TRACKS_SEPARATOR
        numTracks = len(self._kwArgs['extraTracks'].split(MULTIPLE_EXTRA_TRACKS_SEPARATOR))+2        
        

        if type(vennResult)==list:
            vennResult = vennResult[0]
        elif type(vennResult)==dict:
            vennResult = vennResult['stateBPCounter']
        else:
            raise
        
        #convert venn result to cumulative results, which is what we need in this stat
        ourMapping = self._convertVennResultToCumulative(vennResult, numTracks)
        return ourMapping
    
    def _createChildren(self):
        self._addChild( ThreeWayBpOverlapVegardKaiVersionStat(self._region, self._track, self._track2, **self._kwArgs) )
        
