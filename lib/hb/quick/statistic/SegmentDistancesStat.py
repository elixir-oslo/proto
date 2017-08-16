from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticConcatDictOfNumpyArrayResSplittable, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from collections import OrderedDict

class SegmentDistancesStat(MagicStatFactory):
    pass

class SegmentDistancesStatSplittable(StatisticConcatDictOfNumpyArrayResSplittable, OnlyGloballySplittable):
    IS_MEMOIZABLE = False

class SegmentDistancesStatUnsplittable(Statistic):
    INTERVALS = True
    IS_MEMOIZABLE = False

    def _init(self, withOverlaps='no', **kwArgs):
        assert( withOverlaps in ['no','yes'] )
        self._withOverlaps = withOverlaps
    
    def _compute(self):
        tv = self._children[0].getResult()
        nameArray = tv.extrasAsNumpyArray('name') if tv.hasExtra('name') else \
                    tv.idsAsNumpyArray()
        dists = tv.startsAsNumpyArray()[1:]-tv.endsAsNumpyArray()[:-1]
        dists[dists<0] = 0
        
        return OrderedDict([('Result', dists)] + \
                           ([('LeftNames' if tv.hasExtra('name') else 'LeftIds', nameArray[:-1]), \
                             ('RightNames' if tv.hasExtra('name') else 'RightIds', nameArray[1:])] if nameArray is not None else []))
            
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=self.INTERVALS, \
                                                                              allowOverlaps = (self._withOverlaps == 'yes') ) ) )
