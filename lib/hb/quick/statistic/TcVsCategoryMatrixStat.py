from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.track.Track import Track
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq
from copy import copy
from quick.application.ProcTrackOptions import ProcTrackOptions
from numpy import array
from gold.statistic.ResultsMemoizer import ResultsMemoizer
from gold.util.CustomExceptions import IncompatibleTracksError
from gold.util.CommonFunctions import createDirPath
import os.path
from collections import OrderedDict

class TcVsCategoryMatrixStat(MagicStatFactory):
    pass

#class CategoryMatrixStatSplittable(StatisticDictSumResSplittable):
#    pass
            
class TcVsCategoryMatrixStatUnsplittable(Statistic):    
    def __init__(self, region, track, track2, rawStatistic=None, **kwArgs):        
        assert rawStatistic is not None
        assert isinstance(rawStatistic, basestring)
        from gold.statistic.AllStatistics import STAT_CLASS_DICT
        self._rawStatistic = STAT_CLASS_DICT[rawStatistic] 
        
        Statistic.__init__(self, region, track, track2, rawStatistic=rawStatistic, **kwArgs)

    def _compute(self):
        kwArgs = copy(self._kwArgs)
        if 'rawStatistic' in kwArgs:
            del kwArgs['rawStatistic']
            
        matrixElRes = []
        tr1Subtypes = ProcTrackOptions.getSubtypes(self.getGenome(), self._track.trackName, True)
        assert len(tr1Subtypes) > 0
        for subtype1 in tr1Subtypes:#['0','1']:
            for subtype2 in ['0','1']:
                tn1 = self._track.trackName + [subtype1]
                tn2 = self._track2.trackName + [subtype2]
                if not os.path.exists(createDirPath(tn1,self.getGenome())) or not os.path.exists(createDirPath(tn2,self.getGenome())):
                    raise IncompatibleTracksError
                
                #print ','
                track1 = Track( tn1)
                track1.formatConverters = self._track.formatConverters
                track2 = Track( tn2)
                track2.formatConverters = self._track2.formatConverters
                #self._addChild(self._rawStatistic(self._region, track1, track2, **kwArgs) )
                matrixElRes.append( self._rawStatistic(self._region, track1, track2, **kwArgs).getResult() )
                ResultsMemoizer.flushStoredResults()
        
        #assert len(self._children) == 7
        #return dict(zip( '00,01,10,11'.split(','), [x.getResult() for x in self._children[3:]]))
        
        allChildRes = array(matrixElRes)
        #allChildRes = array([x.getResult() for x in self._children[3:]])
        allChildRes = allChildRes.reshape((-1,2))
        return OrderedDict([('Matrix', allChildRes.tolist()), ('Rows', tr1Subtypes), ('Cols', ['Case','Control'])])

    def _createChildren(self):
        kwArgs = copy(self._kwArgs)
        if 'rawStatistic' in kwArgs:
            del kwArgs['rawStatistic']
        self._addChild( FormatSpecStat(self._region, self._track, TrackFormatReq(dense=False, val='category') ) ) #category
        self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(dense=False, val='tc') ) )
        self._addChild( self._rawStatistic(self._region, self._track, self._track2, **kwArgs) )

        #Currently only to get an excpetion raised here.. Should later happen by itself in _compute..
        #tr1Subtypes = ProcTrackOptions.getSubtypes(self.getGenome(), self._track.trackName, True)
        #for subtype1 in tr1Subtypes:#['0','1']:
        #    for subtype2 in ['0','1']:
        #        tn1 = self._track.trackName + [subtype1]
        #        tn2 = self._track2.trackName + [subtype2]
        #        if not os.path.exists(createOrigPath(self.getGenome(),tn1)) or not os.path.exists(createOrigPath(self.getGenome(),tn2)):
        #            raise IncompatibleTracksError
        
                
        #tr1Subtypes = ProcTrackOptions.getSubtypes(self._region.genome, self._track.trackName, True)
        #for subtype1 in tr1Subtypes:#['0','1']:
        #    for subtype2 in ['0','1']:
        #        track1 = Track( self._track.trackName + [subtype1])
        #        track1.formatConverters = self._track.formatConverters
        #        track2 = Track( self._track2.trackName + [subtype2])
        #        track2.formatConverters = self._track2.formatConverters
        #        self._addChild(self._rawStatistic(self._region, track1, track2, **kwArgs) )
                
                
        
