import numpy
from gold.track.RandomizedSegsTrack import RandomizedSegsTrack

class PermutedSegsAndIntersegsTrack(RandomizedSegsTrack):
    _createSegs = RandomizedSegsTrack._permuteSegs
    _createIntersegs = RandomizedSegsTrack._permuteIntersegs
