from gold.statistic.MagicStatFactory import MagicStatFactory
#from quick.track.SegsSampledByDistanceToReferenceTrack import SegsSampledByDistanceToReferenceTrack
from gold.statistic.Statistic import Statistic
#from quick.statistic.StatFacades import SegmentRawDataStat
from gold.util.CompBinManager import CompBinManager


class RandomizedTrackStat(MagicStatFactory):
    pass

class RandomizedTrackStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
        
    def __init__(self, region, track, track2=None, randTrackClass=None, randomSeed=None, **kwArgs):
        #print 'HEI'
        from gold.util.RandomUtil import getManualSeed, setManualSeed
        if randomSeed is not None and randomSeed != 'Random' and getManualSeed() is None:
            setManualSeed(int(randomSeed))
        
        Statistic.__init__(self, region, track, randTrackClass=randTrackClass, randomSeed=randomSeed, **kwArgs)
                
        self._randTrackClass = self.getRandTrackClass(randTrackClass)
                    
        CompBinManager.ALLOW_COMP_BIN_SPLITTING = False
        #self._randResults = []
        #to load r libraries for McFdr:
        #McFdr._initMcFdr()

    @staticmethod
    def getRandTrackClass(randTrackClassDef):
        from quick.util.RandomizationUtils import getRandTrackClass        
        return getRandTrackClass(randTrackClassDef)
        
    def _createRandomizedStat(self, rawStatistic, i):
        "Creates a randChild where certain tracks are randomized"
        tr1 = self._track if self._randTrackClass is None else \
              self._randTrackClass(self._track, self._region, i, **self._kwArgs)
        
        return rawStatistic(self._region, tr1, None, **self._kwArgs)


    def _createChildren(self):                
        #self._realChild = self._addChild( self._rawStatistic(self._region, self._track, self._track2, **self._kwArgs) )        
        from quick.statistic.StatFacades import SegmentRawDataStat
        self._randomizedRawDataTrack = self._addChild( self._createRandomizedStat(SegmentRawDataStat, 0) )

    def _compute(self):
        return self._randomizedRawDataTrack.getResult()
            
    #def getRawStatisticMainClassName(self):
    #    return self._rawStatistic.__name__.replace('Splittable', '').replace('Unsplittable', '')
