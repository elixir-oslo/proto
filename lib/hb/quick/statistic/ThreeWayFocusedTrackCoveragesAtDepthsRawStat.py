from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import StatisticDictSumResSplittable
from quick.statistic.ThreeWayBpOverlapStat import ThreeWayBpOverlapStatUnsplittable
import numpy
from collections import OrderedDict

class ThreeWayFocusedTrackCoveragesAtDepthsRawStat(MagicStatFactory):
    pass
 
class ThreeWayFocusedTrackCoveragesAtDepthsRawStatSplittable(StatisticDictSumResSplittable):
    pass
             
class ThreeWayFocusedTrackCoveragesAtDepthsRawStatUnsplittable(ThreeWayBpOverlapStatUnsplittable):
    from gold.util.CommonFunctions import repackageException
    from gold.util.CustomExceptions import ShouldNotOccurError
    @repackageException(Exception, ShouldNotOccurError)
    
    def _compute(self):
        zeroOneTracks = [child.getResult().getBinaryBpLevelArray()+0 for child in self._children] #+0 to get as integer arrays
        binSize = len(zeroOneTracks[0])
        numTracks = len(zeroOneTracks)
        res = OrderedDict()
        res['BinSize'] = binSize
        
        for focusTrackIndex in range(numTracks):
            sumTrack = numpy.zeros(binSize,dtype='int')
            for index, track in enumerate(zeroOneTracks):
                if index != focusTrackIndex:
                    sumTrack += track
            
            splittedSumTrack = {}
            splittedSumTrack[True] = sumTrack[zeroOneTracks[focusTrackIndex]==1] #WhereFocus
            splittedSumTrack[False] = sumTrack[zeroOneTracks[focusTrackIndex]==0] #WhereNotFocus
            depthCounts = {}
            for focus in [False,True]:
                if len(splittedSumTrack[focus]) > 0: #FIXME: Is this needed at all, {} = dict(enumerate(bincount([])))
                    #print 'ST: ', splittedSumTrack[focus][0:20]
                    numpy.bincount(splittedSumTrack[focus]) #Why?
                    #list(enumerate(numpy.bincount(splittedSumTrack[focus])))
                    depthCounts[focus] = dict(enumerate(numpy.bincount(splittedSumTrack[focus])))
                else:
                    depthCounts[focus] = {}
                #FIXME: You could set the minLength in the bincount to numTracks to get zeros for the largest depth levels, when not present
                for depth in range(len(depthCounts[focus]), numTracks):
                    depthCounts[focus][depth] = 0
            for depth in range(numTracks):
                #denom = sum( depthCounts[focus][depth] for focus in [False, True]) 
                #if denom > 0:
                    #res['Prop. cover by T%i where depth %i by other tracks'%(focusTrackIndex+1, depth)] = float(depthCounts[True][depth]) / denom
                #else:
                    #res['Prop. cover by T%i where depth %i by other tracks'%(focusTrackIndex+1, depth)] = None
                res[(True, focusTrackIndex, depth)] = depthCounts[True][depth]
                res[(False, focusTrackIndex, depth)] = depthCounts[False][depth]
#                 res['Coverage by T%i where depth %i by other tracks'%(focusTrackIndex+1, depth)] = depthCounts[True][depth]
#                 res['Not covered by T%i where depth %i by other tracks'%(focusTrackIndex+1, depth)] = depthCounts[False][depth]
#             print '<br><br>Depth counts: ', depthCounts, '<br><br>'
        return res       
