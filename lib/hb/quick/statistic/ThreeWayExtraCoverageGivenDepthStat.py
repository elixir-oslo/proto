from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.ThreeWayCoverageDepthStat import ThreeWayCoverageDepthStat
from quick.statistic.BinSizeStat import BinSizeStat

class ThreeWayExtraCoverageGivenDepthStat(MagicStatFactory):
    pass
            
class ThreeWayExtraCoverageGivenDepthStatUnsplittable(Statistic):
    def _compute(self):
        depthCount = self._children[0].getResult()
        binSize = self._children[1].getResult()
        numTracks = len(depthCount)-2 #since covered by 0..N, and also binSize as key
        
        chanceOfExtraPerDepth = {}        
        for depth in range(numTracks):
            denom = sum(depthCount['Depth %i'%d] for d in range(depth,numTracks+1))
            if denom > 0:
                chanceOfExtraPerDepth[depth] = float(sum(depthCount['Depth %i'%d] for d in range(depth+1,numTracks+1))) \
                                                   / denom
            else:
                chanceOfExtraPerDepth[depth] = None

        res = {}
        for key,val in chanceOfExtraPerDepth.items():
            res['Proportion of extra coverage given depth '+str(key)] = val
        res['BinSize'] = binSize
        #print res
        return res       
        
    def _createChildren(self):
        self._addChild( ThreeWayCoverageDepthStat(self._region, self._track, self._track2, **self._kwArgs) )
        self._addChild( BinSizeStat(self._region, self._track) )
        
