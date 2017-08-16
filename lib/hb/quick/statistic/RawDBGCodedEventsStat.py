'''
Created on Jun 18, 2015

@author: boris
'''


from numpy import concatenate, add
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleRawDataStatistic
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.BinSizeStat import BinSizeStat
from _collections import defaultdict
import numpy as np

class RawDBGCodedEventsStat(MagicStatFactory):
    '''
    Encode start and end events for multiple tracks. Needed to calculate the raw overlap for all combinations of a set of tracks.
    Because of the encoding it is limited to 33 tracks.
    '''
    pass

#class RawOverlapCodedEventsStatSplittable(StatisticSumResSplittable):
#    pass


def generateValidationTracks():
    array1 = np.array([10, 10010,20010])
    array2 = np.array([11, 10011,20011])
    return [array1, array2]

            
class RawDBGCodedEventsStatUnsplittable(MultipleRawDataStatistic):
    def _init(self, localBinSize='1000000',  **kwArgs):
        self._localBinSize = int(localBinSize)

    def _compute(self):
        tvs = [x.getResult() for x in self._children]
        tvs = tvs[0:-1]
        from numpy import array
 

        tvStarts = [array(x.startsAsNumpyArray(), dtype='int64') for x in tvs]
        tvEnds = [array(x.endsAsNumpyArray(), dtype='int64') for x in tvs]
        
        numTracks = len(tvStarts)
        assert numTracks < 34, 'Maximum supported nr. of tracks for this statistic is 33'

        localBinSize = self._localBinSize
        binSize = self._binSizeStat.getResult()
        bins = np.arange(0,binSize, localBinSize);

        s = []
        for track in tvStarts:
            s.append(len(track))
        
        E = np.sum(s)/float(len(bins))

        O = np.zeros((len(bins),1))
        binPositions = [np.floor_divide(t_starts,localBinSize) for t_starts in tvStarts]

        for track in binPositions:
            for binPos in track:
                O[binPos,0]+=1
        return O,E
        if not E>0:
            T = 0
        else:
            T = np.sum(np.power((O-E),2)/E);
#        print "--------------" + self.__class__.__name__ +  "-----------------------"
#        print self._region, T,E, O

        r = defaultdict(int)
        r[0] = T
        return [T]


    def _createChildren(self):
        #TODO: check solution!
        #For the tests to work with multiple tracks we must send Track objects in extraTracks.
        #Because of the Statistic.constructUniqueKey we must send in a tuple which is hashable.
        MultipleRawDataStatistic._createChildren(self)
        self._binSizeStat = self._addChild(BinSizeStat(self._region, self._track2))


    def _getTrackFormatReq(self):
        return TrackFormatReq(dense=False)
