from gold.util.CommonFunctions import smartMeanWithNones
from quick.statistic.StatisticV2 import StatisticV2
from gold.track.TrackStructure import TrackStructure
from quick.util.debug import DebugUtil
from quick.statistic.RawDBGCodedEventsStat import RawDBGCodedEventsStat
import numpy as np
from _collections import defaultdict
from quick.statistic.BinSizeStat import BinSizeStat
from gold.statistic.RawOverlapCodedEventsStat import RawOverlapCodedEventsStat
from gold.track.Track import Track
'''
Created on Nov 3, 2015

@author: boris
'''


from gold.util.CustomExceptions import ShouldNotOccurError
from numpy import mean
from gold.statistic.MagicStatFactory import MagicStatFactory


class MultitrackRawBinnedOverlapV2Stat(MagicStatFactory):
    '''
    '''
    pass

#class SummarizedInteractionWithOtherTracksStatSplittable(StatisticSumResSplittable):
#    pass
            
class MultitrackRawBinnedOverlapV2StatUnsplittable(StatisticV2):
    

    functionDict = {
                    'sum': sum,
                    'avg': smartMeanWithNones,
                    'max': max,
                    'min': min
                    }

    def _init(self, localBinSize='1000000',summaryFunc=None,  **kwArgs):
        self._localBinSize = int(localBinSize)
        self._summaryFunction = self._resolveFunction(summaryFunc)

    def chiSquare(self, O,E):
        if not E>0:
            T = 0
        else:
            T = np.sum(np.power((O-E),2)/E);
        return T

    def question7stat(self,O,E):
        if E==0:
            return 0 
        T = np.max(O)/E
        return T

    def question8stat(self,starts,lengths,codes):
        region_size = self._binSizeStat.getResult()
        starts = starts[:-1]
        codes = codes[:-1]

        bin_size = self._localBinSize
        num_bins = region_size/bin_size+1
        overlap_counter = np.zeros((num_bins,1))
        num_tracks = len(self._trackStructure.getQueryTrackList())#TODO

        bin_starts = np.arange(0,region_size,bin_size)
        bin_ends   = bin_starts+bin_size
        powers = 2**np.arange(num_tracks,dtype='int32')
        j=0
        k = 0
        for i in xrange(num_bins):
            bin_end = bin_ends[i]
            bin_start = bin_starts[i]
            union = np.zeros((num_tracks,num_tracks))
            intersection = np.zeros((num_tracks,num_tracks))
            while j<len(starts) and starts[j]<bin_end:
                code_vector = (codes[j]/powers)%2
                s = max(starts[j], bin_start)
                e = min(starts[j]+lengths[j], bin_end)
                l = e-s

                a = np.matrix(code_vector)
                intersection += l*a.transpose()*a
                b = np.logical_not(a)
                union += l*np.logical_not(b.transpose()*b)
                if starts[j]+lengths[j] >= bin_end:
                    break
                j=j+1

            ratio = intersection/union
            ratio[np.isnan(ratio) ] = 0            
            overlap_counter[i] = (np.sum(ratio)-np.trace(ratio))/2#Remove diagonal scores(=1) and lower triangle
        O = overlap_counter/bin_size
        E = np.mean(O)
        return (O,E)

    def _resolveFunction(self, summaryFunc):
        if summaryFunc not in self.functionDict:
            raise ShouldNotOccurError(str(summaryFunc) + 
                                      ' not in list, must be one of ' + 
                                      str(sorted(self.functionDict.keys())))
        else: 
            return self.functionDict[summaryFunc]
        
    def _compute(self):
        allSortedDecodedEvents, allEventLengths, cumulativeCoverStatus = self._children[0].getResult()
        O,E = self.question8stat(allSortedDecodedEvents, allEventLengths, cumulativeCoverStatus)
        return [self.chiSquare(O,E)]

    def _createChildren(self):
        tracks = self._trackStructure.getQueryTrackList()
        t1 = tracks[0]
        t2 = tracks[1]
        self._addChild(RawOverlapCodedEventsStat(self._region, t1, t2, extraTracks = tuple(tracks[2:]), **self._kwArgs))
        self._binSizeStat = self._addChild(BinSizeStat(self._region,t1))

#        self._binSizeStat = self._addChild( BinSizeStat(self._region, t1))
