'''
Created on Jul 2, 2015

@author: boris
'''

from collections import OrderedDict
from numpy import zeros
from urllib import unquote

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleRawDataStatistic, StatisticNumpyMatrixSplittable
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CommonConstants import TRACK_TITLES_SEPARATOR


class CollectionVsCollectionStat(MagicStatFactory):
    '''
    For two track collections and a given raw statistic that returns a single value
    it creates a numpy matrix from the results of each pair of tracks (t1, t2) where t1 is a track from
    the first collection and t2 is a track from the second collection.
    '''
    pass

class CollectionVsCollectionStatSplittable(StatisticNumpyMatrixSplittable):
    pass
            
class CollectionVsCollectionStatUnsplittable(MultipleRawDataStatistic):    
    
    def _init(self, trackTitles = '', rawStatistic=None, firstCollectionTrackNr = 0, **kwArgs):
        self._firstCollectionTrackNr = int(firstCollectionTrackNr)
        self._rawStatistic = self.getRawStatisticClass(rawStatistic)
        
        self._trackTitles = [unquote(t) for t in trackTitles.split(TRACK_TITLES_SEPARATOR)]
    
    def _compute(self):
        firstCollection = self._tracks[:self._firstCollectionTrackNr]
        secondCollection = self._tracks[self._firstCollectionTrackNr:]
        rows = self._trackTitles[:self._firstCollectionTrackNr]
        cols = self._trackTitles[self._firstCollectionTrackNr:]
        
        res = zeros((len(firstCollection), len(secondCollection)))
        
        for i, track1 in enumerate(firstCollection):
            for j, track2 in enumerate(secondCollection):
                if track1 == track2:
                    pass
                else:
                    singleResult = self._rawStatistic(self._region, track1, track2, **self._kwArgs).getResult()
                    res[i][j] = singleResult
        
        return {'Result': OrderedDict([('Matrix', res), ('Rows', rows), ('Cols', cols)])}
        
    def _getTrackFormatReq(self):
        return TrackFormatReq(dense=False)         
