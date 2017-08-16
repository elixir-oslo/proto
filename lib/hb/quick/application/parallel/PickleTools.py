from gold.track.Track import Track
from gold.track.RandomizedTrack import RandomizedTrack
from gold.statistic.Statistic import Statistic

class StatisticArgumentPickleWrapper(object):    
    def __init__(self, cls, region, track1, track2=None, **kwArgs):
        self._cls = cls
        self._region = region
        self._trackPickle1 = TrackPickleWrapper.fromTrack(track1)
        self._trackPickle2 = TrackPickleWrapper.fromTrack(track2)
        self._kwArgs = kwArgs
            
    def toStatistic(self):
        track1 = self._trackPickle1.toTrack()
        track2 = self._trackPickle2.toTrack() 
    
        return self._cls(self._region, track1, track2, **self._kwArgs)

class RandomizationStatisticArgumentPickleWrapper(object):
    def __init__(self, randomizationManagerStat, sampleNumbers, seed=None, **kwArgs):
        self._rawStatistic = randomizationManagerStat._rawStatistic
        self._region = randomizationManagerStat._region
        self._trackPickle1 = TrackPickleWrapper.fromTrack(randomizationManagerStat._track)
        self._trackPickle2 = TrackPickleWrapper.fromTrack(randomizationManagerStat._track2)
        self._kwArgs = kwArgs
        self._seed = seed
        
        self._randTrackClass1 = randomizationManagerStat._randTrackClass1
        self._randTrackClass2 = randomizationManagerStat._randTrackClass2
        self._sampleNumbers = sampleNumbers
        
    def toStatistic(self):
        self._track = self._trackPickle1.toTrack()
        self._track2 = self._trackPickle2.toTrack() 
        
        #self._reseed(self._seed)
        for i in self._sampleNumbers:
            yield self._createRandomizedStat(i)  
    
    def _createRandomizedStat(self, i):
        "Creates a randChild where second track is randomized"
        tr1, tr2 = self._createRandomizedTracks(i)
        
        return self._rawStatistic(self._region, tr1, tr2, **self._kwArgs)
    
    def _createRandomizedTracks(self, i):
        tr1 = self._track if self._randTrackClass1 is None else \
              self._randTrackClass1(self._track, self._region, i, **self._kwArgs)
        
        tr2 = self._track2 if self._randTrackClass2 is None else \
              self._randTrackClass2(self._track2, self._region, i, **self._kwArgs)
              
        return tr1, tr2      
    
    def _reseed(self, seed):
        if seed == None:
            return
        
        from gold.util.RandomUtil import setManualSeed
        #randomUtil = gold.util.RandomUtil.RandomUtil()
        uniqueSeed = int(hash(seed) ^ hash(self._region) ^ self._sampleNumbers[0])
        setManualSeed(uniqueSeed) #this currently crashes due to rpy/numpy acting silly...
        

class TrackPickleWrapper(object):
    @classmethod
    def fromTrack(cls, track):      
        if isinstance(track, RandomizedTrack):
            return RandomizedTrackPickle(track)
        return NormalTrackPickle(track)
    
    @classmethod
    def fromStatistic(cls, statistic):
        if not hasattr(statistic, "_track"):
            raise ValueError("All statistics should have at least one track") #TODO: fix exception class
        
        trackPickle1 = cls.fromTrack(statistic._track)
        
        trackPickle2 = None
        if hasattr(statistic, "_track2"):
            trackPickle2 = cls.fromTrack(statistic._track2)
        
        return trackPickle1, trackPickle2
    
    
          
class TrackPickle(object):    
    def _extractTrackName(self, track):
            return track.trackName
        
    def _extractTrackClass(self, track):
            return track.__class__
        
    def _extractFormatConverters(self, track):
        if hasattr(track, "formatConverters"):
            return track.formatConverters
        else:
            return None
    
class RandomizedTrackPickle(TrackPickle):
    def __init__(self, track):
        if track is None:
            self._trackName = None
            return
        
        self._trackName = "dummy"
        self._origTrack = NormalTrackPickle(track._origTrack)
        self._origRegion = track._origRegion
        self._trackClass = self._extractTrackClass(track)
        self._randIndex = track._randIndex
        self._formatConverters = self._extractFormatConverters(track)
        
    def toTrack(self):
        if self._trackName is None:
            return None
        
        origTrack = self._origTrack.toTrack()
        track = self._trackClass(origTrack, self._origRegion, self._randIndex)
        
        if self._formatConverters is not None:
            track.formatConverters = self._formatConverters
        
        return track
        
class NormalTrackPickle(TrackPickle):
    def __init__(self, track):
        if track is None:
            self._trackName = None
            return
        
        self._trackName = self._extractTrackName(track)
        self._trackClass = self._extractTrackClass(track)
        self._formatConverters = self._extractFormatConverters(track)        
    
    def toTrack(self):
        if self._trackName is None:
            return None
            
        track = self._trackClass(self._trackName)
        
        if self._formatConverters is not None:
            track.formatConverters = self._formatConverters
        
        return track
    
class CustomTrackCreatorPickleWrapper(object):
    def __init__(self, stat, chr):
        self.cls = stat.cls
        self.genome = stat.genome
        self.inTrackName = stat.inTrackName
        self.outTrackName = stat.outTrackName
        self.windowSize = stat.windowSize
        self.chr = chr
        self.func = stat.func
        
class FunctionPickleWrapper(object):
    def __init__(self, expression, midPointIsZero):
        self.expression = expression
        self.midPointIsZero = midPointIsZero
        
    def __call__(self, val):
        import quick.application.GalaxyInterface
        return quick.application.GalaxyInterface.GalaxyInterfaceTools.wrappedDnaFunc(val, self.expression, self.midPointIsZero)   
        