from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleRawDataStatistic,\
    StatisticListSumResSplittable
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.BinSizeStat import BinSizeStat
from gold.statistic.RawOverlapEventsStat import RawOverlapEventsStat

class MultitrackCoverageDepthStat(MagicStatFactory):
    '''
    Returns a list where the index i is the depth level, 
    and the corresponding value is the number of base-pair positions that are covered by exactly i tracks.
    '''
    pass

class MultitrackCoverageDepthStatSplittable(StatisticListSumResSplittable):
    pass

class MultitrackCoverageDepthStatUnsplittable(MultipleRawDataStatistic):

    def _compute(self): 
        
        numTracks = len(self._tracks)
        binSize = self._binSizeStat.getResult()
        allSortedDecodedEvents, allEventLengths, cumulativeCoverStatus = self._children[0].getResult()

        results = [0]*(numTracks+1)

#Old implementation
#         for i, cumCoverStatus in enumerate(cumulativeCoverStatus[:-1]):
#             depth = bin(cumCoverStatus).count("1")
#             results[depth] += allEventLengths[i]

        for i, cumCoverStatus in enumerate(cumulativeCoverStatus[:-1]):
            results[cumCoverStatus] += allEventLengths[i]

        if len(allSortedDecodedEvents)>0:
            results[0] += allSortedDecodedEvents[0] + (binSize - allSortedDecodedEvents[-1])
        else:
            results[0] +=binSize

        return results

    def _createChildren(self):
        #For the tests to work with multiple tracks we must send Track objects in extraTracks.
        #Because of the Statistic.constructUniqueKey we must send in a tuple which is hashable.
        if 'extraTracks' in self._kwArgs:
            del self._kwArgs['extraTracks']
#         self._addChild(RawOverlapCodedEventsStat(self._region, self._track, self._track2, extraTracks = tuple(self._tracks[2:]), **self._kwArgs))
        self._addChild(RawOverlapEventsStat(self._region, self._track, self._track2, extraTracks = tuple(self._tracks[2:]), **self._kwArgs))
        self._binSizeStat = self._addChild( BinSizeStat(self._region, self._track2))
        
    def _getTrackFormatReq(self):
        return TrackFormatReq(dense=False)
