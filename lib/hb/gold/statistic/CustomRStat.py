from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.BasicCustomRStat import BasicCustomRStat
from gold.statistic.RandomizationManagerStat import RandomizationManagerStat
from gold.track.PermutedSegsAndSampledIntersegsTrack import PermutedSegsAndSampledIntersegsTrack

class CustomRStat(MagicStatFactory):
    pass

#class CustomRStatSplittable(StatisticSumResSplittable):
#    pass

class CustomRStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    def _init(self, scriptFn='', **kwArgs):
        self._scriptFn = scriptFn
        if self._scriptFn != '':
            self._useMC = any(["#Use in Monte Carlo" in line for line in open(scriptFn.decode('hex_codec'))])
            
    def _compute(self):
        return self._children[0].getResult()
        
    def _createChildren(self):
        if self._useMC:
            #rawStat = wrapClass(BasicCustomRStat, {'scriptFn':self._scriptFn})
            #self._addChild( RandomizationManagerStat(self._region, self._track, self._track2, rawStat, \
            #                                         ReshuffledRandomizedTrack, numResamplings=20 ) )
            self._addChild( RandomizationManagerStat(self._region, self._track, self._track2, BasicCustomRStat, \
                                                         PermutedSegsAndSampledIntersegsTrack, numResamplings=20, **self._kwArgs) )
        else:
            self._addChild(BasicCustomRStat(self._region, self._track, self._track2, **self._kwArgs))
