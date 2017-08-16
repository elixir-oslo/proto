from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticDictSumResSplittable
from collections import OrderedDict
from gold.statistic.MultitrackFocusedCoverageDepthStat import MultitrackFocusedCoverageDepthStat

class ThreeWayFocusedTrackCoveragesAtDepthsStat(MagicStatFactory):
    pass

class ThreeWayFocusedTrackCoveragesAtDepthsStatSplittable(StatisticDictSumResSplittable):
    pass
            
class ThreeWayFocusedTrackCoveragesAtDepthsStatUnsplittable(Statistic):
    from gold.util.CommonFunctions import repackageException
    from gold.util.CustomExceptions import ShouldNotOccurError
    @repackageException(Exception, ShouldNotOccurError)
    
    def _compute(self):
        childResults = self._children[0].getResult()
        
        res = OrderedDict()
        res['BinSize'] = childResults['BinSize']
        
        for key in childResults:
            if key != 'BinSize':
                if key[0]:
                    res['Coverage by T%i where depth %i by other tracks'%(key[1]+1, key[2])] = childResults[key]
                else:
                    res['Not covered by T%i where depth %i by other tracks'%(key[1]+1, key[2])] = childResults[key]
        return res
    
    def _createChildren(self):
#         self._addChild( ThreeWayFocusedTrackCoveragesAtDepthsRawStat(self._region, self._track, self._track2, **self._kwArgs))
        self._addChild( MultitrackFocusedCoverageDepthStat(self._region, self._track, self._track2, **self._kwArgs))
        
#     def _compute(self):
#         zeroOneTracks = [child.getResult().getBinaryBpLevelArray()+0 for child in self._children] #+0 to get as integer arrays
#         binSize = len(zeroOneTracks[0])
#         numTracks = len(zeroOneTracks)
#         res = {}
#         res['BinSize'] = binSize
#         
#         for focusTrackIndex in range(numTracks):
#             sumTrack = numpy.zeros(binSize,dtype='int')
#             for index, track in enumerate(zeroOneTracks):
#                 if index != focusTrackIndex:
#                     sumTrack += track
#             
#             splittedSumTrack = {}
#             splittedSumTrack[True] = sumTrack[zeroOneTracks[focusTrackIndex]==1] #WhereFocus
#             splittedSumTrack[False] = sumTrack[zeroOneTracks[focusTrackIndex]==0] #WhereNotFocus
#             depthCounts = {}
#             for focus in [False,True]:
#                 if len(splittedSumTrack[focus]) > 0: #FIXME: Is this needed at all, {} = dict(enumerate(bincount([])))
#                     #print 'ST: ', splittedSumTrack[focus][0:20]
#                     numpy.bincount(splittedSumTrack[focus]) #Why?
#                     #list(enumerate(numpy.bincount(splittedSumTrack[focus])))
#                     depthCounts[focus] = dict(enumerate(numpy.bincount(splittedSumTrack[focus])))
#                 else:
#                     depthCounts[focus] = {}
#                 #FIXME: You could set the minLength in the bincount to numTracks to get zeros for the largest depth levels, when not present
#                 for depth in range(len(depthCounts[focus]), numTracks):
#                     depthCounts[focus][depth] = 0
#             for depth in range(numTracks):
#                 #denom = sum( depthCounts[focus][depth] for focus in [False, True]) 
#                     #res['Prop. cover by T%i where depth %i by other tracks'%(focusTrackIndex+1, depth)] = None
#                 #if denom > 0:
#                     #res['Prop. cover by T%i where depth %i by other tracks'%(focusTrackIndex+1, depth)] = float(depthCounts[True][depth]) / denom
#                 #else:
#                 res['Coverage by T%i where depth %i by other tracks'%(focusTrackIndex+1, depth)] = depthCounts[True][depth]
#                 res['Not covered by T%i where depth %i by other tracks'%(focusTrackIndex+1, depth)] = depthCounts[False][depth]            
#             print '<br><br>Depth counts: ', depthCounts, '<br><br>'
#         return res       
