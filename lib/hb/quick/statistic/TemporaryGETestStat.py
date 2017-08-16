from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class TemporaryGETestStat(MagicStatFactory):
    '''
    To be deleted after testing..
    '''
    pass



class TemporaryGETestStatUnsplittable(Statistic):
    def _compute(self): 
        from gold.origdata.GenomeElement import GenomeElement
        ge = GenomeElement(start=0, end=1)
        ge2 = GenomeElement(start=10, end=11)
        return [ge,ge2]
                
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq() ) )
