from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import StatisticDictSumResSplittable, Statistic
from gold.statistic.MultitrackCoverageDepthStat import MultitrackCoverageDepthStat
from quick.statistic.BinSizeStat import BinSizeStat
from collections import OrderedDict


class ThreeWayCoverageDepthStat(MagicStatFactory):
    pass

class ThreeWayCoverageDepthStatSplittable(StatisticDictSumResSplittable):
    pass

##TEMPORARY FOR CONSTRUCT FUNCTION DEF:
#from gold.statistic.Statistic import StatisticSumResSplittable, StatisticSplittable
#class ThreeWayCoverageDepthStatSplittable(StatisticSplittable):
#    def _combineResults(self):
#        if len(self._childResults)>1:
#            #self._result = self._childResults[0] + self._childResults[1]
#            self._result = reduce(lambda x,y:x+y, self._childResults)
#        else:
#            self._result = 'Empty'


class ThreeWayCoverageDepthStatUnsplittable(Statistic):
    
    def _compute(self):
        depths = self._children[0].getResult()
        res = OrderedDict()
        res['BinSize'] = self._binSizeStat.getResult()
        for key, val in enumerate(depths):
            res['Depth %i'%key] = val
        return res               
    
    def _createChildren(self):
        self._addChild(MultitrackCoverageDepthStat(self._region, self._track, self._track2, **self._kwArgs))
        self._binSizeStat = self._addChild( BinSizeStat(self._region, self._track))
# class ThreeWayCoverageDepthStatUnsplittable(MultipleRawDataStatistic):
#     #from gold.util.CommonFunctions import repackageException
#     #from gold.util.CustomExceptions import ShouldNotOccurError
#     #@repackageException(Exception, ShouldNotOccurError)
#     
#     def _compute(self):
#         zeroOneTracks = [child.getResult().getBinaryBpLevelArray()+0 for child in self._children] #+0 to get as integer arrays
#         binSize = len(zeroOneTracks[0])
#         numTracks = len(zeroOneTracks)
#         
#         sumTrack = numpy.zeros(binSize,dtype='int')
#         for track in zeroOneTracks:
#             sumTrack += track
#         depthCount = dict(enumerate(numpy.bincount(sumTrack)))
#         for depth in range(len(depthCount), numTracks+1):
#             depthCount[depth] = 0
#             
#         res = {}
#         for key,val in depthCount.items():
#             res['Depth %i'%key] = val
#         res['BinSize'] = binSize
#         return res       
#         
#         ##To construct code and tests for external development
#         #from test.sandbox.div.constructFunctionDefs import constructFunctionDefWithTest
#         #startNames = ['starts' + str(i) for i in range(len(self._children))]
#         #endNames = ['ends' + str(i) for i in range(len(self._children))]
#         #starts = [list(child.getResult().startsAsNumpyArray()) for child in self._children]
#         #ends = [list(child.getResult().endsAsNumpyArray()) for child in self._children]        
#         #return constructFunctionDefWithTest('computeCoverageDepth', ['binSize']+startNames+endNames , [binSize]+starts+ends, res)
#     
#         
#     def _getTrackFormatReq(self):
#         return TrackFormatReq(dense=False)
        
    #_createChildren = ThreeWayBpOverlapStatUnsplittable._createChildren    
    
    #def _compute(self):
    #    t = self._children[0].getResult()
    #    binSize = self._children[1].getResult()
    #    
    #    numTracks = len(t.keys()[0])
    #    from collections import Counter
    #    countPerDepth = Counter()
    #    for combA in range(1,2**numTracks): #enumerate with binary number corresponding to all subsets
    #        binaryA = numAsPaddedBinary(combA,numTracks)
    #        #tracksInA = set([i for i,x in enumerate(binaryA) if x=='1'])
    #        depth = binaryA.count('1')
    #        countPerDepth[depth] += t[binaryA]
    #        
    #    countPerDepth[0] = binSize
    #    
    #    distinctCountPerDepth = {}
    #    for depth in range(numTracks):
    #        distinctCountPerDepth[depth] = countPerDepth[depth] - countPerDepth[depth+1]
    #    distinctCountPerDepth[numTracks] = countPerDepth[numTracks]
    #    print 'DICTS: ',countPerDepth, distinctCountPerDepth
    #    assert binSize == sum(distinctCountPerDepth.values())
    #
    #    chanceOfExtraPerDepth = {}        
    #    for depth in range(numTracks):
    #        chanceOfExtraPerDepth[depth] = countPerDepth[depth+1] / float(countPerDepth[depth])
    #        
    #    #countPerDepth['Depth 0'] = binSize - 
    #    res = {}
    #    for key,val in distinctCountPerDepth.items():
    #        res['Depth '+str(key)] = val
    #    for key,val in chanceOfExtraPerDepth.items():
    #        res['Proportion of extra coverage given depth '+str(key)] = val
    #    res['BinSize'] = binSize
    #    #print res
    #    return res       
    #    
    #
    #def _createChildren(self):
    #    self._addChild( ThreeWayBpOverlapStat(self._region, self._track, self._track2, **self._kwArgs) )
    #    self._addChild( BinSizeStat(self._region, self._track) )
    #    
