from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.ProportionCountStat import ProportionCountStat
from gold.statistic.Statistic import Statistic, StatisticSplittable
from quick.result.model.ResultTypes import GlobalVisualizationResultType
from quick.statistic.MeanInsideOutsideStat import MeanInsideOutsideStat


#from gold.statistic.RawDataStat import RawDataStat
#from gold.track.TrackFormat import TrackFormatReq

class ValuesInsideVsOutsideVisualizationStat(MagicStatFactory):
    pass

class ValuesInsideVsOutsideVisualizationStatSplittable(StatisticSplittable):
    def _combineResults(self):
        self._result = GlobalVisualizationResultType(self._childResults)
        return self._result
            
class ValuesInsideVsOutsideVisualizationStatUnsplittable(Statistic):    
    def _compute(self):
        insideOutsideDict = self._children[0].getResult()
        inside = insideOutsideDict['MeanInsideSegments']
        outside =insideOutsideDict['MeanOutsideSegments']
        coverage = self._children[1].getResult()
        
        return (self._region, inside, outside,coverage)
        #use GlobalVisualizationResult also here..
        
        
    def _createChildren(self):
        #self._track: defines inside vs outside
        #self._track2: provides values        
        self._addChild( MeanInsideOutsideStat(self._region, self._track, self._track2) )
        self._addChild( ProportionCountStat(self._region, self._track) )
