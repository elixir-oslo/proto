from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import RatioDictSingleDenomStatUnsplittable
#from gold.statistic.RawDataStat import RawDataStat
#from gold.track.TrackFormat import TrackFormatReq
#from quick.statistic.ThreeWayExpectedBpOverlapStat import ThreeWayExpectedBpOverlapStatUnsplittable
from quick.statistic.ThreeWayExpectedBpOverlapGivenBinPresenceAsWholeBpsStat import ThreeWayExpectedBpOverlapGivenBinPresenceAsWholeBpsStat
from quick.statistic.BinSizeStat import BinSizeStat


class ThreeWayExpectedBpOverlapGivenBinPresenceStat(MagicStatFactory):
    pass

#class ThreeWayExpectedBpOverlapGivenBinPresenceStatSplittable(StatisticDictSumResSplittable, OnlyGloballySplittable):
#    pass

class ThreeWayExpectedBpOverlapGivenBinPresenceStatUnsplittable(RatioDictSingleDenomStatUnsplittable):
    #def _compute(self):
    #    origRes = ThreeWayExpectedBpOverlapStatUnsplittable._compute(self)
    #    return dict([(key+'_GivenBinPresence', value) for key,value in origRes.items()])
        
    def _createChildren(self):
        self._addChild( ThreeWayExpectedBpOverlapGivenBinPresenceAsWholeBpsStat(self._region, self._track, self._track2, **self._kwArgs) )
        self._addChild( BinSizeStat(self._region, self._track) )
