from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import SplittableStatNotAvailableError
from gold.util.CommonFunctions import isIter

class RawDataStat(MagicStatFactory):
    def __new__(cls, region, track, trackFormatReq, **kwArgs):
        assert isinstance(trackFormatReq, TrackFormatReq)
        track.addFormatReq(trackFormatReq)
        return MagicStatFactory.__new__(cls, region, track, **kwArgs)
        #return MagicStatFactory.__new__(cls, region, track, trackFormatReq=trackFormatReq, **kwArgs)

class RawDataStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    def __init__(self, region, track, **kwArgs):
        if isIter(region):
            raise SplittableStatNotAvailableError()

        #super(self.__class__, self).__init__(region, track, trackFormatReq=trackFormatReq, **kwArgs)
        super(self.__class__, self).__init__(region, track, **kwArgs)
        #self._trackFormatReq = trackFormatReq

    def _compute(self):
        return self._track.getTrackView(self._region)

    def _createChildren(self):
        #if self._trackFormatReq is None:
        #    print 'dense'
        self._children = []
        #self._track.addFormatReq(self._trackFormatReq)

    def _afterComputeCleanup(self):
        if self.hasResult():
            #print 'clean up for reg: ',self._region ,'with trackname: ',self._track.trackName
            del self._result
    
    def _updateInMemoDict(self, statKwUpdateDict):
        pass
