from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq
#from gold.statistic.GeneralOneTrackIterateValsStat import GeneralOneTrackIterateValsStatUnsplittable

class GeneralOneCatTrackStat(MagicStatFactory):
    pass

#class GeneralOneCatTrackStatUnsplittable(GeneralOneTrackIterateValsStatUnsplittable):
class GeneralOneCatTrackStatUnsplittable(Statistic):
    STORE_CHILDREN = True
    
    #def __init__(self, region, track, track2, rawStatistic=None, **kwArgs):
    #    GeneralOneTrackIterateValsStatUnsplittable.__init__(self, region, track, track2, \
    #                                                        rawStatistic=rawStatistic, \
    #                                                        storeChildren=self.STORE_CHILDREN, \
    #                                                        **kwArgs)
        
    def _createChildren(self):
        #GeneralOneTrackIterateValsStatUnsplittable._createChildren(self)
        self._addChild( FormatSpecStat(self._region, self._track, TrackFormatReq(val='category')) )
