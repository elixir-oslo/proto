from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class PercentageChangeStat(MagicStatFactory):
    "Counts bps covered by track. If specified with intra-track overlaps, it will for each bp count the number of times the bp is covered by a track element."
    pass

class PercentageChangeStatSplittable(StatisticSumResSplittable):
    pass
            
class PercentageChangeStatUnsplittable(Statistic):    
    def _compute(self):
        
        companyTrack = self._children[0].getResult()
        companyStart = companyTrack.startsAsNumpyArray()
        companyVals = companyTrack.valsAsNumpyArray()
        
        calendarTrack = self._children[1].getResult()
        calStart = calendarTrack.startsAsNumpyArray()
        calEnd = calendarTrack.endsAsNumpyArray()
        
        index = 0
        result = 1.0
        companyIndex = len(companyTrack)
        try:
            for i in range(len(calStart)):
                rangeList = range(calStart[i], calEnd[i])
                if len(rangeList)==0:
                    continue
                valList = []
                while index < len(companyStart):
                    if companyStart[index] in rangeList:
                        valList.append(companyVals[index])
                    elif companyStart[index]>rangeList[-1]:
                        break
                    index+=1
                
                if len(valList)>1:
                    change = 1.0 + (valList[-1] - valList[0])/valList[0]
                    result *= change
        except:
            pass
        
        return (result*100.0) -100.0
    
        
        
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='number', allowOverlaps=self._configuredToAllowOverlaps(strict=False))) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(interval=True, allowOverlaps=self._configuredToAllowOverlaps(strict=False))) )
