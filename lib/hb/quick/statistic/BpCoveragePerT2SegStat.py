from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import numpy

class BpCoveragePerT2SegStat(MagicStatFactory):
    pass

class BpCoveragePerT2SegStatSplittable(StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable):
    IS_MEMOIZABLE = False
            
class BpCoveragePerT2SegStatUnsplittable(Statistic):    
    IS_MEMOIZABLE = False

    def _compute(self):
        tv1, tv2 = self._children[0].getResult(), self._children[1].getResult()
        t1BpArray = tv1.getBinaryBpLevelArray()
        return numpy.array([t1BpArray[el.start():el.end()].sum() for el in tv2])
            

    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=True)) ) #interval=False is supported through the faster PointCountPerSegStat..
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True)) )
        #fixme: Track 2 should have borderhandling='include', but this is not supported yet. This to support correct splitting'
