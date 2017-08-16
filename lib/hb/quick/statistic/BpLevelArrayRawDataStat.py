from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import ShouldNotOccurError

class BpLevelArrayRawDataStat(MagicStatFactory):
    pass

class BpLevelArrayRawDataStatUnsplittable(Statistic):
    def _init(self, bpDepthType='coverage', useFloatValues=False, **kwArgs):

        assert bpDepthType in ['coverage','binary']
        self._bpDepthType = bpDepthType

        assert useFloatValues in [True, 'True', False,'False']
        self._useFloatValues = useFloatValues in [True, 'True']

    def _compute(self): #Numpy Version..
        tv = self._children[0].getResult()

        if self._bpDepthType == 'coverage':
            vals = tv.getCoverageBpLevelArray()
        elif self._bpDepthType == 'binary':
            vals = tv.getBinaryBpLevelArray()
        else:
            raise ShouldNotOccurError

        if self._useFloatValues:
            return vals.astype('float64')

        else:
            return vals


    def _createChildren(self):
        allowOverlaps = self._configuredToAllowOverlaps(strict=False, allowReturningNone=True)
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=allowOverlaps)) )

    def _afterComputeCleanup(self):
        if self.hasResult():
            del self._result
