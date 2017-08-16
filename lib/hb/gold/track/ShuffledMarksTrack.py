import numpy
from gold.track.RandomizedTrack import RandomizedTrack
from gold.util.CustomExceptions import IncompatibleTracksError

class ShuffledMarksTrack(RandomizedTrack):
    def _checkTrackFormat(self, origTV):
        if not origTV.trackFormat.isValued():
            raise IncompatibleTracksError(str(origTV.trackFormat))

    def _createRandomizedNumpyArrays(self, binLen, starts, ends, vals, strands, ids, edges, weights, extras, region):
        newVals = numpy.copy(vals)
        numpy.random.shuffle(newVals)

        return starts, ends, newVals, strands, ids, edges, weights, extras
