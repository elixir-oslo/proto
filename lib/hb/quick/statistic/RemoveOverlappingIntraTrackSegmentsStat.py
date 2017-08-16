from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.track.TrackView import TrackView
import numpy as np
#from gold.application.LogSetup import logMessage

class RemoveOverlappingIntraTrackSegmentsStat(MagicStatFactory):
    pass

#class RemoveOverlappingIntraTrackSegmentsStatSplittable(StatisticSumResSplittable):
#    pass
            
class RemoveOverlappingIntraTrackSegmentsStatUnsplittable(Statistic):
    
        
    def _compute(self):
        
        tv = self._children[0].getResult()
        startL, endL, valL = list(tv.startsAsNumpyArray()), list(tv.endsAsNumpyArray()), tv.valsAsNumpyArray()
        index = 0
        numSegments = len(startL)
        overlapTreshold = 0
        startRes, endRes, valRes = [], [], []
        
        while index<numSegments-1:
            start = startL[index]
            end = endL[index]
            if start>=overlapTreshold and startL[index+1] >= end:
                startRes.append(start)
                endRes.append(end)
                valRes.append(valL[index])
            overlapTreshold = max(overlapTreshold, end)
            index+=1
        
        
        if startL[-1]>=overlapTreshold:
            startRes.append(startL[index])
            endRes.append(endL[index])
            valRes.append(valL[index])
                
            
        
            
        return TrackView(genomeAnchor=tv.genomeAnchor, startList=np.array(startRes), endList=np.array(endRes), valList=np.array(valRes), \
                         strandList=None, idList=None, edgesList=None, weightsList=None, borderHandling=tv.borderHandling, allowOverlaps=False)
        
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(interval=True)) )

