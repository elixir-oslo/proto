from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticDictSumResSplittable
from gold.track.Track import Track
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from copy import copy
from gold.util.CustomExceptions import IncompatibleTracksError
from gold.util.CommonFunctions import createDirPath
import os.path

class ConfusionMatrixStat(MagicStatFactory):
    pass

class ConfusionMatrixStatSplittable(StatisticDictSumResSplittable):
    pass
            
class ConfusionMatrixStatUnsplittable(Statistic):    
    def __init__(self, region, track, track2, rawStatistic=None, **kwArgs):        
        assert rawStatistic is not None
        assert isinstance(rawStatistic, basestring)
        from gold.statistic.AllStatistics import STAT_CLASS_DICT
        self._rawStatistic = STAT_CLASS_DICT[rawStatistic] 
        
        Statistic.__init__(self, region, track, track2, rawStatistic=rawStatistic, **kwArgs)
        
    #from gold.util.CommonFunctions import repackageException
    #@repackageException(OSError, IncompatibleTracksError)
    def _compute(self):
        assert len(self._children) == 7
        return dict(zip( '00,01,10,11'.split(','), [x.getResult() for x in self._children[3:]]))
    
    def _createChildren(self):
        kwArgs = copy(self._kwArgs)
        if 'rawStatistic' in kwArgs:
            del kwArgs['rawStatistic']
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, val='tc') ) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, val='tc') ) )
        self._addChild( self._rawStatistic(self._region, self._track, self._track2, **kwArgs) )
        #try:
        for subtype1 in ['0','1']:
            for subtype2 in ['0','1']:
                tn1 = self._track.trackName + [subtype1]
                tn2 = self._track2.trackName + [subtype2]
                
                if not os.path.exists(createDirPath(tn1, self.getGenome())) or not os.path.exists(createDirPath(tn2,self.getGenome())):
                    raise IncompatibleTracksError
                track1 = Track( tn1)
                track1.formatConverters = self._track.formatConverters
                track2 = Track( tn2)
                track2.formatConverters = self._track2.formatConverters
                self._addChild(self._rawStatistic(self._region, track1, track2, **kwArgs) )
        
