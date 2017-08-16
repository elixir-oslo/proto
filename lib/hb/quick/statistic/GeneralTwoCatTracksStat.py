from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq
#from gold.statistic.GeneralTwoTracksIterateValsStat import GeneralTwoTracksIterateValsStatUnsplittable

class GeneralTwoCatTracksStat(MagicStatFactory):
    pass

#class GeneralTwoCatTracksStatUnsplittable(GeneralTwoTracksIterateValsStatUnsplittable):
class GeneralTwoCatTracksStatUnsplittable(Statistic):
    STORE_CHILDREN = True
    
    #def __init__(self, region, track, track2, rawStatistic=None, **kwArgs):
    #    GeneralTwoTracksIterateValsStatUnsplittable.__init__(self, region, track, track2, \
    #                                                         rawStatistic=rawStatistic, \
    #                                                         storeChildren=self.STORE_CHILDREN, \
    #                                                         **kwArgs)
    #    
    def _createChildren(self):
        #GeneralTwoTracksIterateValsStatUnsplittable._createChildren(self)
        self._addChild( FormatSpecStat(self._region, self._track, TrackFormatReq(val='category')) )
        self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(val='category')) )
