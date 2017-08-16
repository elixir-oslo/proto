from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSplittable
from gold.track.TrackFormat import TrackFormatReq
#from gold.util.CustomExceptions import SplittableStatNotAvailableError
from gold.statistic.RawDataStat import RawDataStat
from quick.result.model.ResultTypes import RawVisualizationResultType

class RawVisualizationDataStat(MagicStatFactory):
    pass

class RawVisualizationDataStatSplittable(StatisticSplittable):
    def _combineResults(self):
        self._result = RawVisualizationResultType(self._childResults)
        
    
class RawVisualizationDataStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
        
    def _compute(self):
        tv = self._children[0].getResult()
        tv.normalizeRows = True if hasattr(self, '_kwArgs') and self._kwArgs.has_key('normalizeRows') and self._kwArgs['normalizeRows'] in ['True', True] else False
        tv.centerRows = True if hasattr(self, '_kwArgs') and self._kwArgs.has_key('centerRows') and self._kwArgs['centerRows'] in ['True', True] else False

        return tv

    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False), **self._kwArgs) )
