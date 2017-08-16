from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticDynamicDictSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import IncompatibleTracksError
import numpy

class BpCoverageByCatStat(MagicStatFactory):
    pass

class BpCoverageByCatStatSplittable(StatisticDynamicDictSumResSplittable):
    pass
            
class BpCoverageByCatStatUnsplittable(Statistic):
    def _compute(self):
        rawData = self._children[0].getResult()
        ends = rawData.endsAsNumpyArray()
        starts = rawData.startsAsNumpyArray()
        catSequence = rawData.valsAsNumpyArray()
        if catSequence is None:
            raise IncompatibleTracksError()
        
        catSet = numpy.unique(catSequence)
        res = {}
        for cat in catSet:
            filter = (catSequence==cat)
            if rawData.trackFormat.reprIsDense():
                res[cat] = filter.sum()
            else:
                #print 'BpCoverage..: ',ends, starts, catSequence, catSet, type(catSequence), filter
                #res[cat] = ends[filter].sum() - starts[filter].sum()
                catStarts = starts[filter]
                catEnds = ends[filter]
                
                totCoverage = catEnds.sum() - catStarts.sum()
                
                runningMaxEnds = numpy.maximum.accumulate(catEnds)
                tempArray1 = runningMaxEnds[:-1] - catStarts[1:]
                tempArray2 = runningMaxEnds[:-1] - catEnds[1:]
                totOverlap = tempArray1[tempArray1 > 0].sum() - tempArray2[tempArray2 > 0].sum()
                
                res[cat] = totCoverage - totOverlap
        
        return res
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='category', allowOverlaps=True)) )
        
