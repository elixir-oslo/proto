'''
Created on Jun 18, 2015
'''
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleRawDataStatistic, StatisticSparseDictSumResSplittable
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.BinSizeStat import BinSizeStat
from gold.statistic.RawOverlapCodedEventsStat import RawOverlapCodedEventsStat
from _collections import defaultdict
from gold.statistic.RawDataStat import RawDataStat
import numpy as np
from quick.util.debug import DebugUtil



class RawDBGStat(MagicStatFactory):
    '''
    Encode start and end events for multiple tracks. Needed to calculate the raw overlap for all combinations of a set of tracks.
    Because of the encoding it is limited to 33 tracks.
    '''
    pass

#class RawOverlapCodedEventsStatSplittable(StatisticSumResSplittable):
#    pass
            
class RawDBGStatUnsplittable(MultipleRawDataStatistic):    
    def _compute(self):
        tvs = []
        for track in [self._track, self._track2]:
            tvs.append(RawDataStat(self._region, track, self._getTrackFormatReq()).getResult())
#        tvs = [x.getResult() for x in self._children]
        print len(self._tracks)
        from numpy import array
#         tvStartsOld = [x.startsAsNumpyArray()for x in tvs]
#         tvEndsOld = [x.endsAsNumpyArray() for x in tvs]
        tvStarts = [array(x.startsAsNumpyArray(), dtype='int64') for x in tvs]
        tvEnds = [array(x.endsAsNumpyArray(), dtype='int64') for x in tvs]
        
        tvStarts = [np.array(x.startsAsNumpyArray(), dtype='int64') for x in tvs]
        tvEnds = [np.array(x.endsAsNumpyArray(), dtype='int64') for x in tvs]        
        print "N Starts: " + str(len(tvStarts[0]))
        for x in tvs:
            print x
            print x.__dict__
        print ".........---------------............"
        for tvs in tvStarts:
            print tvs
            print tvs.__dict__

        binSize = tvEnds[0][-1]*2;
        bins = np.range(0,binSize, localBinSize);
        print "Bins: " + str(len(bins));
        s = [];
        for track in tvStarts:
            s.append(len(track))
        
        E = np.sum(s)/len(bins)        
        print "Expected" + str(E)
        O = np.zeros((1,len(bins)))
        binPositions = [np.floor_divide(t_starts,10000) for t_starts in tvStarts]
        for track in binPositions:
            for binPos in track:
                O[binPos]+=1
        
        T = np.sum(np.power((O-E),2)/E);
        return T


    def _getTrackFormatReq(self):
        return TrackFormatReq(dense=False)



