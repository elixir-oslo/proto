from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.track.PermutedSegsAndIntersegsTrack import PermutedSegsAndIntersegsTrack
from gold.track.PermutedSegsAndSampledIntersegsTrack import PermutedSegsAndSampledIntersegsTrack
from gold.track.ShuffledMarksTrack import ShuffledMarksTrack
from gold.track.SegsSampledByIntensityTrack import SegsSampledByIntensityTrack
from gold.track.RandomGenomeLocationTrack import RandomGenomeLocationTrack


class RandomizedRawDataStat(MagicStatFactory):
    pass

class RandomizedRawDataStatUnsplittable(Statistic):
    def _init(self, randTrackClass=None, **kwArgs):
        randTrackClass = (globals()[randTrackClass] if randTrackClass not in ['None',''] else None ) \
                if type(randTrackClass) is str else randTrackClass 

        assert randTrackClass in [None, PermutedSegsAndSampledIntersegsTrack, \
                       PermutedSegsAndIntersegsTrack, RandomGenomeLocationTrack, SegsSampledByIntensityTrack, ShuffledMarksTrack]
        self._randTrackClass = randTrackClass
                
    def _compute(self): #Numpy Version..
        tv = self._children[0].getResult()
        return tv
        #TrackView(genomeAnchor = tv.genomeAnchor, startList=segBorders[:-1], endList=segBorders[1:], valList=np.array(newVals[1:], dtype=combineMethod.getDataType()), \
        #                 strandList=None, idList=None, edgesList=None, weightsList=None, borderHandling=tv.borderHandling, allowOverlaps=tv.allowOverlaps)

            
        
    def _createChildren(self):
        randomizedTrack = self._track if self._randTrackClass is None else \
                          self._randTrackClass(self._track, self._region, 0, **self._kwArgs)
        self._addChild( RawDataStat(self._region, randomizedTrack, TrackFormatReq()) )
