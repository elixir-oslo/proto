from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class GetMutatedSequenceStat(MagicStatFactory):
    pass

#class GetMutatedSequenceStatSplittable(StatisticSumResSplittable):
#    pass
    
class GetMutatedSequenceStatUnsplittable(Statistic):    
    
    from gold.util.CommonFunctions import repackageException
    from gold.util.CustomExceptions import ShouldNotOccurError
    @repackageException(Exception, ShouldNotOccurError)
    def _compute(self):
        tv1 = self._children[0].getResult()
        tv2 = self._children[1].getResult()
        
        fastaSequence = list(tv1.valsAsNumpyArray())
        mutationStarts, mutationValues = tv2.startsAsNumpyArray(), list(tv2.valsAsNumpyArray())
        if len(mutationValues)>0 and mutationValues[0].find('>')>=0:
            mutationValues = [v[-1] for v in mutationValues]
        for index, mutationPos in enumerate(mutationStarts):
            fastaSequence[mutationPos] = mutationValues[index]
            #fastaSequence.insert(mutationPos+1, '#'+mutationValues[index])
        
        return ''.join(fastaSequence)
    
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=True, val='char')) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(val='category')) )
        
        
        
