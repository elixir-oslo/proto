from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleRawDataStatistic, StatisticDictSumResSplittable
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.BinSizeStat import BinSizeStat
from gold.statistic.RawOverlapCodedEventsStat import RawOverlapCodedEventsStat
from numpy import binary_repr, where, array

class MultitrackFocusedCoverageDepthStat(MagicStatFactory):
    '''

    '''
    pass

class MultitrackFocusedCoverageDepthStatSplittable(StatisticDictSumResSplittable):
    pass

class MultitrackFocusedCoverageDepthStatUnsplittable(MultipleRawDataStatistic):

    def _compute(self): 
        
        numTracks = len(self._tracks)
        binSize = self._binSizeStat.getResult()
        allSortedDecodedEvents, allEventLengths, cumulativeCoverStatus = self._children[0].getResult()

#         print '<br><br>', allSortedDecodedEvents, '<br><br>', allEventLengths, '<br><br>', cumulativeCoverStatus
        resDict = {}
        
        resDict['BinSize'] = binSize
        
        for i in xrange(numTracks):
            for j in xrange(numTracks):
                resDict[(False, i, j)] = 0
                resDict[(True, i, j)] = 0

        for i, cumCoverStatus in enumerate(cumulativeCoverStatus[:-1]):
#             print '<br><br>', i,'<br>',cumCoverStatus  
            binaryCumCoverStatus = binary_repr(cumCoverStatus, numTracks)
            rvrsdBinCCS = binaryCumCoverStatus[::-1]
#             print '<br>',binaryCumCoverStatus, '<br>', rvrsdBinCCS
            nonFocusedDepth = binaryCumCoverStatus.count('1')
#             print '<br>',nonFocusedDepth
            focusedDepth = nonFocusedDepth - 1
            if nonFocusedDepth > 0:
                indcsFocused = where(array(list(rvrsdBinCCS)) == '1')[0]
#                 print '<br>Indices focused: ',indcsFocused
                for trackIndex in indcsFocused:
                    resDict[(True, trackIndex, focusedDepth)] += allEventLengths[i]
            indcsNonFocused = where(array(list(rvrsdBinCCS)) == '0')[0]
#             print '<br>Indices non-focused: ', indcsNonFocused
            for trackIndex in indcsNonFocused:
                resDict[(False, trackIndex, nonFocusedDepth)] += allEventLengths[i]
#             print '<br>Event length: ',allEventLengths[i]
        
        if len(allSortedDecodedEvents)>0:
            for i in xrange(numTracks):
                resDict[(False, i, 0)] += allSortedDecodedEvents[0] + (binSize - allSortedDecodedEvents[-1])
        else:
            for i in xrange(numTracks):
                resDict[(False, i, 0)]+=binSize
                
        return resDict

    def _createChildren(self):
        #TODO: check solution!
        #For the tests to work with multiple tracks we must send SampleTrack objects in extraTracks.
        #Because of the Statistic.constructUniqueKey we must send in a tuple which is hashable.
        if 'extraTracks' in self._kwArgs:
            del self._kwArgs['extraTracks']
        self._addChild(RawOverlapCodedEventsStat(self._region, self._track, self._track2, extraTracks = tuple(self._tracks[2:]), **self._kwArgs))
        self._binSizeStat = self._addChild( BinSizeStat(self._region, self._track2))
        
    def _getTrackFormatReq(self):
        return TrackFormatReq(dense=False)
