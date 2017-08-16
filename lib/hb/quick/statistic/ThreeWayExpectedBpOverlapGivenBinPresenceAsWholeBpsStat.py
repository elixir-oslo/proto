from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticDictSumResSplittable, OnlyGloballySplittable
#from gold.statistic.RawDataStat import RawDataStat
#from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.ThreeWayExpectedBpOverlapStat import ThreeWayExpectedBpOverlapStat
from quick.statistic.BinSizeStat import BinSizeStat
from gold.util.CommonFunctions import isIter
class ThreeWayExpectedBpOverlapGivenBinPresenceAsWholeBpsStat(MagicStatFactory):
    pass

class ThreeWayExpectedBpOverlapGivenBinPresenceAsWholeBpsStatSplittable(StatisticDictSumResSplittable, OnlyGloballySplittable):
    pass
    #def _combineResults(self):
    #    self._result = OrderedDict([ (key, smartSum([res[key] for res in self._childResults])) for key in self._childResults[0] ])
    #    print 'here:    '
    #    print OrderedDict([ (key, [res[key] for res in self._childResults]) for key in self._childResults[0] ])
    #    print self._result

class ThreeWayExpectedBpOverlapGivenBinPresenceAsWholeBpsStatUnsplittable(Statistic):
    def _compute(self):
        #origRes = ThreeWayExpectedBpOverlapStatUnsplittable._compute(self)
        assert not isIter(self._region)
        #print 'REG: ',self._region
        origRes = self._children[0].getResult()
        binSize = self._children[1].getResult()
        return dict([(key+'_GivenBinPresence', value*binSize) for key,value in origRes.items()])
        
    def _createChildren(self):
        self._addChild( ThreeWayExpectedBpOverlapStat(self._region, self._track, self._track2, **self._kwArgs) )
        self._addChild( BinSizeStat(self._region, self._track) )
        
    #def _createChildren(self):
    #    self._addChild( ThreeWayProportionalBpOverlapStat(self._region, self._track, self._track2, **self._kwArgs) )
