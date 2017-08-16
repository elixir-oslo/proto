from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.track.TrackView import TrackView
import numpy as np
#from gold.application.LogSetup import logMessage
from collections import defaultdict
from quick.util.GenomeInfo import GenomeInfo

class ConvertSegmentsToStepFunctionStat(MagicStatFactory):
    pass

#class ConvertSegmentsToStepFunctionStatSplittable(StatisticSumResSplittable):
#    pass
            
class ConvertSegmentsToStepFunctionStatUnsplittable(Statistic):
    
        
    def _compute(self):
        tv = self._children[0].getResult()
        starts, ends = tv.startsAsNumpyArray(), tv.endsAsNumpyArray()
        
        borderDict = defaultdict(int)
        listLen = len(starts)
        
        for index in xrange(listLen):
            borderDict[starts[index]]+=1
            borderDict[ends[index]]-=1
        
        
        sortedPos = sorted(borderDict)
        range(0, chrlength, microbinzie)
        
        #handle start border issues
        startList, endList, valList = (sortedPos,  sortedPos[1:], [])  if sortedPos[0] == 0 else  ([0] + sortedPos,  sortedPos,  [0])
        
        #Handle end border issues 
        chrEndPos = GenomeInfo.getChrLen(tv.genomeAnchor.genome, tv.genomeAnchor.chr)-1
        startList, endList  = (startList, endList+[chrEndPos])  if endList[-1]<chrEndPos else  (startList[:-1], endList)
        
        #make step-function values
        accVal = 0
        for pos in sortedPos:
            accVal+= borderDict[pos]
            valList.append(accVal)
        
        if chrEndPos == pos:
            valList.pop()
        
            
        return TrackView(genomeAnchor=tv.genomeAnchor, startList=np.array(startList), endList=np.array(endList), valList=np.array(valList), \
                         strandList=None, idList=None, edgesList=None, weightsList=None, borderHandling=tv.borderHandling, allowOverlaps=False)
        
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(interval=True)) )

