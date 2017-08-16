from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import StatisticConcatNumpyArrayResSplittable, Statistic, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class ExtractMarksStat(MagicStatFactory):
    pass

class ExtractMarksStatSplittable(StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable):
    IS_MEMOIZABLE = False
            
class ExtractMarksStatUnsplittable(Statistic):    
    IS_MEMOIZABLE = False

    def _compute(self):
        vals = self._children[0].getResult().valsAsNumpyArray()
        rawData2 = self._children[1].getResult()
        
        if rawData2.trackFormat.isInterval():
            return vals[ rawData2.getBinaryBpLevelArray() ]
        else:
            points = rawData2.startsAsNumpyArray()
            return vals[points]
    
    #def _getCoverageVec(self, rawData):
    #    tempVec = numpy.zeros(len(rawData), dtype='i')
    #    tempVec[ rawData.startsAsNumpyArray() ] = 1
    #    tempVec[ rawData.endsAsNumpyArray() ] = -1
    #    coverageVec = numpy.add.accumulate(tempVec)
    #    return (coverageVec != 0)
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=True, interval=False, val='number')) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False)) ) 
