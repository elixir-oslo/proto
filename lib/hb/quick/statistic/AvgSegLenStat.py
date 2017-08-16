from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
#from gold.statistic.RawDataStat import RawDataStat
#from gold.track.TrackFormat import TrackFormatReq
#from gold.statistic.CountSegmentStat import CountSegmentStat
#from quick.statistic.CountNumSegmentsStat import CountNumSegmentsStat
from gold.statistic.SegmentLengthsStat import SegmentLengthsStat

class AvgSegLenStat(MagicStatFactory):
    pass
            
class AvgSegLenStatUnsplittable(Statistic):    
    def _init(self, withOverlaps='no', **kwArgs):
        assert( withOverlaps in ['no','yes'])
        self._withOverlaps = withOverlaps
        
    def _compute(self):
        #return 1.0 * self._children[0].getResult() / self._children[1].getResult()
        return self._children[0].getResult()['Result'].mean()
        
    def _createChildren(self):
        #self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(interval=True)) )
        #self._addChild( CountSegmentStat(self._region, self._track) )
        #self._addChild( CountNumSegmentsStat(self._region, self._track) )
        self._addChild( SegmentLengthsStat(self._region, self._track, withOverlaps=self._withOverlaps) )
