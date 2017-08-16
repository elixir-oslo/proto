from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticDynamicDictSumResSplittable, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import IncompatibleTracksError
from collections import OrderedDict
import numpy

class CategoryPointCountNoOverlapsStat(MagicStatFactory):
    pass

class CategoryPointCountNoOverlapsStatSplittable(StatisticDynamicDictSumResSplittable, OnlyGloballySplittable):
    pass
            
class CategoryPointCountNoOverlapsStatUnsplittable(Statistic):
    VERSION = '1.1'
    # Different from FreqPerCatStat in that two overlapping points of the same category are only counted once.
    # Can also be used for segments, but then only counts starting points (ignoring strand)
    def _compute(self):
        rawData = self._children[0].getResult()
        starts = rawData.startsAsNumpyArray()
        catSequence = rawData.valsAsNumpyArray()
        if catSequence is None:
            raise IncompatibleTracksError()
        
        catSet = numpy.unique(catSequence)
        res = OrderedDict()
        for cat in catSet:
            filter = (catSequence==cat)
            res[cat] = len(numpy.unique(starts[filter]))
        return res
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, val='category', allowOverlaps=True)) )
