from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.track.Track import Track
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import IncompatibleTracksError
from gold.util.CommonFunctions import createDirPath
import os.path
from copy import copy
from gold.statistic.GeneralOneTcTrackStat import GeneralOneTcTrackStatUnsplittable

class GeneralTrack2TcStat(MagicStatFactory):
    pass

#class GeneralTrack2TcStatSplittable(StatisticDictSumResSplittable):
    #pass
            
class GeneralTrack2TcStatUnsplittable(GeneralOneTcTrackStatUnsplittable):        
    def _createChildren(self):
        kwArgs = copy(self._kwArgs)
        if 'rawStatistic' in kwArgs:
            del kwArgs['rawStatistic']
        self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(dense=False, val='tc') ) )
        #self._track.formatConverters = 'Dummy' #to avoid check of tracks not being used..
        #self._track2.formatConverters = 'Dummy' #to avoid check of tracks not being used..
        #self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, val='tc') ) )
        self._addChild( self._rawStatistic(self._region, self._track, self._track2, **kwArgs) ) #This will actually compute, without any use for it. 
        self._indexOfFirstSubCatChild = len(self._children)

        for subtype2 in ['0','1']:
            #for subtype2 in ['0','1']:
            tn2 = self._track2.trackName + [subtype2]
            if not os.path.exists(createDirPath(tn2, self.getGenome())):
                #logMessage('DID NOT EXIST.. '+createOrigPath(self.getGenome(),tn1))
                raise IncompatibleTracksError
            #else:
            #    logMessage('DID EXIST')
            track2 = Track( tn2)
            track2.formatConverters = self._track2.formatConverters
            #track2 = Track( self._track2.trackName + [subtype2])
            #track2.formatConverters = self._track2.formatConverters
            self._addChild(self._rawStatistic(self._region, self._track, track2, **kwArgs) )
            #logMessage('Came all down..')
        
