
from gold.track.PermutedSegsAndIntersegsTrack import PermutedSegsAndIntersegsTrack
from gold.track.PermutedSegsAndSampledIntersegsTrack import PermutedSegsAndSampledIntersegsTrack
from gold.track.ShuffledMarksTrack import ShuffledMarksTrack
from gold.track.SegsSampledByIntensityTrack import SegsSampledByIntensityTrack
from gold.track.RandomGenomeLocationTrack import RandomGenomeLocationTrack
#from quick.track.SegsSampledByDistanceToReferenceTrack import SegsSampledByDistanceToReferenceTrack
from quick.track.SegsSampledByDistanceToReferenceTrack import SegsSampledByDistanceToReferenceTrack
from gold.util.CommonFunctions import getClassName
from gold.track.TrackStructure import TrackStructure
from gold.track.RandomizedTrack import RandomizedTrack

def getRandTrackClassList(randTrackClassNameList):
    #to be refactored:
    if isinstance(randTrackClassNameList, basestring):
        randTrackClassNameList = randTrackClassNameList.split('_')
        
    return [getRandTrackClass(x) for x in randTrackClassNameList]


def getRandTrackClass(randTrackClassName):
    randTrackClass =  ( globals()[randTrackClassName] if randTrackClassName not in ['None',''] else None ) \
        if isinstance(randTrackClassName, basestring) else randTrackClassName

    assert randTrackClass in [None, PermutedSegsAndSampledIntersegsTrack, \
                       PermutedSegsAndIntersegsTrack, RandomGenomeLocationTrack, SegsSampledByIntensityTrack, ShuffledMarksTrack, SegsSampledByDistanceToReferenceTrack], getClassName(randTrackClass)
    return randTrackClass


def createRandomizedStat(tracks, randomizationStrategies, rawStatistic, region, kwArgs, i):
    "Creates a randChild where certain tracks are randomized"
    assert len(tracks)>0
    assert rawStatistic is not None
    
    randomizedTracks = [] #or not randomized, if there is no randomization strategy for the corresponding track
          
    for track, randStratStr in zip(tracks, randomizationStrategies):
                    
        randStrat = (globals()[randStratStr] if type(randStratStr) is str else randStratStr) if randStratStr not in [None, ''] else None
        
        if randStrat:
            randomizedTracks.append(randStrat(track, region, i, **kwArgs))
        else:
            randomizedTracks.append(track)
        

    return rawStatistic(region, randomizedTracks[0], randomizedTracks[1] if len(randomizedTracks)>1 else None, extraTracks='^'.join(randomizedTracks[2:]), **kwArgs)

def createRandomizedTrackStructureStat(trackStructure, randTrackClassDict, rawStatistic, region, kwArgs, i):
    randomizedTrackStructure = TrackStructure()
    for key in trackStructure:
        randTrackClassStr = randTrackClassDict[key] if key in randTrackClassDict else None
        if randTrackClassStr:
            randTrackClass = globals()[randTrackClassStr] if type(randTrackClassStr) is str else randTrackClassStr
            if issubclass(randTrackClass, RandomizedTrack):
                randomizedTrackStructure[key] = [randTrackClass(track, region, i, **kwArgs) for track in trackStructure[key]]
            else: #randomize whole collection
                pass
        else:
            randomizedTrackStructure[key] = trackStructure[key]                
    return rawStatistic(region, randomizedTrackStructure, **kwArgs)



