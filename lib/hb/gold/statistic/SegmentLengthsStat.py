from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticConcatDictOfNumpyArrayResSplittable, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from collections import OrderedDict

class SegmentLengthsStat(MagicStatFactory):
    pass

class SegmentLengthsStatSplittable(StatisticConcatDictOfNumpyArrayResSplittable, OnlyGloballySplittable):
    IS_MEMOIZABLE = False

class SegmentLengthsStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    def _init(self, withOverlaps='no', **kwArgs):
        assert( withOverlaps in ['no','yes'] )
        self._withOverlaps = withOverlaps

    def _compute(self):
        tv = self._children[0].getResult()
        nameArray = tv.extrasAsNumpyArray('name') if tv.hasExtra('name') else \
                    tv.idsAsNumpyArray()
        
        return OrderedDict([('Result', tv.endsAsNumpyArray()-tv.startsAsNumpyArray())] + \
                           ([('Names' if tv.hasExtra('name') else 'Ids', nameArray)] if nameArray is not None else []))
        #return [(seg.end()-seg.start()) for seg in self._children[0].getResult()]
            
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(interval=True, \
                                                                              allowOverlaps = (self._withOverlaps == 'yes') ) ) )
