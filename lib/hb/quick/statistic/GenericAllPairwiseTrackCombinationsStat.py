from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleRawDataStatistic
#from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class GenericAllPairwiseTrackCombinationsStat(MagicStatFactory):
    pass

#class ThreeWayProportionalBpOverlapStatSplittable(StatisticSumResSplittable):
#    pass
            
class GenericAllPairwiseTrackCombinationsStatUnsplittable(MultipleRawDataStatistic):        
    def _compute(self):
        #rawResults = [child.getResult() for child in self._children]        
        #for res in rawResults:
        
        #return dict([ (resKey, self._childDict[resKey].getResult()) for resKey in self._childDict])
        fullResult = {}        
        for resKey in self._childDict:
            res = self._childDict[resKey].getResult()
            if isinstance(res, dict):
                for subResKey in res:                    
                    fullResult[ '_'.join([resKey,subResKey]) ] = res[subResKey]
            else:
                fullResult[ resKey ] = res
        
        return fullResult
    
    def _getTrackFormatReq(self):
        return TrackFormatReq(dense=False)
        
    def _createChildren(self):
        rawStat = self.getRawStatisticClass( self._kwArgs['rawStatistic'] )
        self._childDict = {}
        
        t = self._tracks
        for i in range(len(t)):
            for j in range(i+1,len(t)):
                from gold.util.CommonFunctions import prettyPrintTrackName                
                resKey = ' vs '.join([prettyPrintTrackName(track.trackName, shortVersion=True) for track in [t[i],t[j]] ])
                self._childDict[resKey] = self._addChild( rawStat(self._region, t[i], t[j], self._getTrackFormatReq() ) )
