from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleRawDataStatistic, StatisticSparseDictSumResSplittable
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.BinSizeStat import BinSizeStat
from gold.statistic.RawOverlapCodedEventsStat import RawOverlapCodedEventsStat
from _collections import defaultdict

class MultitrackRawOverlapStat(MagicStatFactory):
    '''
    Counts the overlap for all track combinations.
    The result is a dict that where key is the int version of the binary number that represents the track combination
    E.G. for 3 tracks, the combination of the first and third track is in binary 101 and the key is 5. 
    For the combination of first and second track 011 and the key is 3.
    '''
    pass

class MultitrackRawOverlapStatSplittable(StatisticSparseDictSumResSplittable):
    pass


class MultitrackRawOverlapStatUnsplittable(MultipleRawDataStatistic):
    VERSION = '1.1'

    def _compute(self): #Numpy Version..
        
        binSize = self._binSizeStat.getResult()
        allSortedDecodedEvents, allEventLengths, cumulativeCoverStatus = self._children[0].getResult()

        return self._computeRawOverlap(allSortedDecodedEvents, allEventLengths, cumulativeCoverStatus, binSize)


    @classmethod
    def _computeRawOverlap(cls, allSortedDecodedEvents, allEventLengths, cumulativeCoverStatus, binSize):
        
        resDict = defaultdict(int)
        
        for eventLength, cumCoverStatus in zip(allEventLengths, cumulativeCoverStatus[:-1]):
            resDict[cumCoverStatus] = resDict[cumCoverStatus] + eventLength if cumCoverStatus in resDict else eventLength


        if 0 not in resDict:
            resDict[0] = 0
        if len(allSortedDecodedEvents)>0:
            resDict[0] += allSortedDecodedEvents[0] + (binSize - allSortedDecodedEvents[-1])
        else:
            resDict[0] +=binSize

        return resDict

    def _createChildren(self):
        #TODO: check solution!
        #For the tests to work with multiple tracks we must send Track objects in extraTracks.
        #Because of the Statistic.constructUniqueKey we must send in a tuple which is hashable.
        if 'extraTracks' in self._kwArgs:
            del self._kwArgs['extraTracks']
        self._addChild(RawOverlapCodedEventsStat(self._region, self._track, self._track2, extraTracks = tuple(self._tracks[2:]), **self._kwArgs))
        self._binSizeStat = self._addChild( BinSizeStat(self._region, self._track2))

    def _getTrackFormatReq(self):
        return TrackFormatReq(dense=False)
