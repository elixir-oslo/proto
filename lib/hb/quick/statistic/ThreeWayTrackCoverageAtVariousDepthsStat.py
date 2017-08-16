from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.ThreeWayBpOverlapStat import ThreeWayBpOverlapStat
from quick.statistic.BinSizeStat import BinSizeStat
from quick.util.CommonFunctions import numAsPaddedBinary

class ThreeWayTrackCoverageAtVariousDepthsStat(MagicStatFactory):
    pass

#class ThreeWayProportionalBpOverlapStatSplittable(StatisticSumResSplittable):
#    pass
            
class ThreeWayTrackCoverageAtVariousDepthsStatUnsplittable(Statistic):        
    def _compute(self):
        t = self._children[0].getResult()
        binSize = self._children[1].getResult()
        
        numTracks = len(t.keys()[0])
        from collections import Counter
        countPerDepth = {0:{False:Counter(), True:Counter()}}

        focusTrackIndex = 0
        for combA in range(1,2**numTracks): #enumerate with binary number corresponding to all subsets
            binaryA = list(numAsPaddedBinary(combA,numTracks))
            focusTrackIncluded = (binaryA[focusTrackIndex] == '1')
            binaryA[focusTrackIndex] = '0'
            binaryA = ''.join(binaryA)
            #tracksInA = set([i for i,x in enumerate(binaryA) if x=='1'])
            depth = binaryA.count('1')
            
            bpCount = binSize if depth == 0 else t[binaryA]
            countPerDepth[focusTrackIndex][focusTrackIncluded][0] += bpCount
            
        countPerDepth[focusTrackIndex][False][0] = binSize# - sum(sum(countPerDepth[focusTrackIndex][included].values()) for included in [False,True])
        
        res = {}
        for key in countPerDepth[focusTrackIndex][False]:
            res[key] = float(countPerDepth[focusTrackIndex][False][key]) / sum(countPerDepth[focusTrackIndex][included][key] for included in [False,True])
        res['BinSize'] = binSize
        return res
        
    
    def _createChildren(self):
        self._addChild( ThreeWayBpOverlapStat(self._region, self._track, self._track2, **self._kwArgs) )
        self._addChild( BinSizeStat(self._region, self._track) )
        
