from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from collections import OrderedDict
from gold.statistic.MultitrackFocusedCoverageDepthStat import MultitrackFocusedCoverageDepthStat

class ThreeWayFocusedTrackProportionCoveragesAtDepthsRawStat(MagicStatFactory):
    pass

#class ThreeWayFocusedTrackProportionCoveragesAtDepthsRawStatSplittable(StatisticDictSumResSplittable):
#    pass

class ThreeWayFocusedTrackProportionCoveragesAtDepthsRawStatUnsplittable(Statistic):    
    def _compute(self):
        coverages = self._children[0].getResult()
        binSize = coverages['BinSize']
        
        #del coverages['BinSize']
        
#         import math
#         numTracks = int(math.sqrt((len(coverages[True])))) #T[1..N] at depth [0..N-1], with and without focus
#         assert numTracks**2 == (len(coverages[True])), (numTracks, len(coverages[True]), coverages[True].keys()) #should be no rounding..
        
        import math
        numTracks = int(math.sqrt((len(coverages)-1)/2.0)) #T[1..N] at depth [0..N-1], with and without focus
        assert numTracks**2 == (len(coverages)-1)/2.0, (numTracks, len(coverages), coverages.keys()) #should be no rounding..
   
        res = OrderedDict()
        res['BinSize'] = binSize
        
        for focusTrackIndex in range(numTracks):    
            for depth in range(numTracks):
#                 focusKey = 'Coverage by T%i where depth %i by other tracks'%(focusTrackIndex+1, depth)
#                 nonFocusKey = 'Not covered by T%i where depth %i by other tracks'%(focusTrackIndex+1, depth)
#                 denom = sum( coverages[key] for key in [focusKey, nonFocusKey]) 
                focusKey = (True, focusTrackIndex, depth)
                nonFocusKey = (False, focusTrackIndex, depth)
                denom = coverages[focusKey] + coverages[nonFocusKey]
                res[focusKey] = (float(coverages[focusKey]) / denom) if denom > 0 else None
                res[nonFocusKey] = (float(coverages[nonFocusKey]) / denom) if denom > 0 else None
#                 if denom > 0:
#                     res['Prop. cover by T%i where depth %i by other tracks'%(focusTrackIndex+1, depth)] = float(coverages[focusKey]) / denom
#                 else:
#                     res['Prop. cover by T%i where depth %i by other tracks'%(focusTrackIndex+1, depth)] = None
                #res['Coverage by T%i where depth %i by other tracks'%(focusTrackIndex+1, depth)] = depthCounts[True][depth]
                #res['Not covered by T%i where depth %i by other tracks'%(focusTrackIndex+1, depth)] = depthCounts[False][depth]
                    
        return res       

    def _createChildren(self):
        self._addChild( MultitrackFocusedCoverageDepthStat(self._region, self._track, self._track2, **self._kwArgs) )
#         self._addChild( ThreeWayFocusedTrackCoveragesAtDepthsRawStat(self._region, self._track, self._track2, **self._kwArgs) )
