from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.track.Track import Track
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import IncompatibleTracksError, ShouldNotOccurError
from gold.util.CommonFunctions import createDirPath
import os.path
from copy import copy

class GeneralOneTcTrackStat(MagicStatFactory):
    pass

#class GeneralOneTcTrackStatSplittable(StatisticDictSumResSplittable):
    #pass
            
class GeneralOneTcTrackStatUnsplittable(Statistic):    
    def __init__(self, region, track, track2, rawStatistic=None, **kwArgs):        
        assert rawStatistic is not None
        assert isinstance(rawStatistic, basestring)
        from gold.statistic.AllStatistics import STAT_CLASS_DICT
        self._rawStatistic = STAT_CLASS_DICT[rawStatistic] 
        
        Statistic.__init__(self, region, track, track2, rawStatistic=rawStatistic, **kwArgs)

    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)
    def _compute(self):
        if len(self._children) != 4 or self._indexOfFirstSubCatChild != 2:
            raise ShouldNotOccurError
        self._children[1].getResult() #To avoid problems due to it not being accessed correctly..
        #self._children[0]._curChild=None
        #self._children[1]._curChild=None
        #self._children[2].getResult()
        #self._children[3].getResult()
        target, control = [x.getResult() for x in self._children[self._indexOfFirstSubCatChild:]]
        return {'Target':target, 'Control':control, 'PropTargetOfAll':(1.0*target/(target+control))}
    
    def _createChildren(self):
        kwArgs = copy(self._kwArgs)
        if 'rawStatistic' in kwArgs:
            del kwArgs['rawStatistic']
        track2 = self._track2 if hasattr(self, '_track2') else None
        self._addChild( FormatSpecStat(self._region, self._track, TrackFormatReq(dense=False, val='tc') ) )
        #self._track.formatConverters = 'Dummy' #to avoid check of tracks not being used..
        #self._track2.formatConverters = 'Dummy' #to avoid check of tracks not being used..
        #self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, val='tc') ) )
        self._addChild( self._rawStatistic(self._region, self._track, track2, **kwArgs) ) #This will actually compute, without any use for it. 
        self._indexOfFirstSubCatChild = len(self._children)

        for subtype1 in ['0','1']:
            #for subtype2 in ['0','1']:
            tn1 = self._track.trackName + [subtype1]
            if not os.path.exists(createDirPath(tn1, self.getGenome())):
                #logMessage('DID NOT EXIST.. '+createOrigPath(self.getGenome(),tn1))
                raise IncompatibleTracksError
            #else:
            #    logMessage('DID EXIST')
            track1 = Track( tn1)
            track1.formatConverters = self._track.formatConverters
            #track2 = Track( self._track2.trackName + [subtype2])
            #track2.formatConverters = self._track2.formatConverters
            self._addChild(self._rawStatistic(self._region, track1, track2, **kwArgs) )
            #logMessage('Came all down..')
        
