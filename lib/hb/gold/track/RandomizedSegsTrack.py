import numpy
from gold.track.RandomizedTrack import RandomizedTrack
from gold.util.CustomExceptions import IncompatibleTracksError

class RandomizedSegsTrack(RandomizedTrack):
    def _checkTrackFormat(self, origTV):
        if origTV.trackFormat.isDense():
            raise IncompatibleTracksError()

    def _createRandomizedNumpyArrays(self, binLen, starts, ends, vals, strands, ids, edges, weights, extras, region):
        if len(starts)==0:
            assert len(ends)==0
            return starts, ends, vals, strands, ids, edges, weights, extras

        #create the pools (empiric distributions) of segLengths and intersegLengths (dists between segments)
        segLens, vals, strands, ids, edges, weights, extras = self._createSegs(starts, ends, vals, strands, ids, edges, weights, extras)
        intersegLens = self._createIntersegs(starts, ends, binLen)

        #combines segs and intersegs into a matrix, to allow them to be mixed intermittently
        combinedLenMatrix = numpy.concatenate( (segLens.reshape((-1,1)), intersegLens[1:].reshape((-1,1))), axis=1 )
        #flat version now has elements originally from segs and intersegs in intermittent order

        #combinedLens = numpy.concatenate((intersegLens[0:1], combinedLenMatrix.flat, intersegLens[-1:])) #or perhaps flatten() must be used instead of .flat
        combinedLens = numpy.concatenate((intersegLens[0:1], combinedLenMatrix.flatten()))

        #accumulate from lengths to positions
        eventPositions = numpy.add.accumulate(combinedLens)
        assert eventPositions[-1] == binLen

        #now only contain start and end positions of what will be the resulting segments
        eventPositions = eventPositions[:-1]
        assert len(eventPositions)%2 == 0

        #reshape to again extract positions intermittently as starts and ends
        eventPosMat = eventPositions.reshape((-1,2))
        starts, ends = [eventPosMat[:,col] for col in [0,1]]
        return starts, ends, vals, strands, ids, edges, weights, extras

    def _permuteSegs(self, starts, ends, vals, strands, ids, edges, weights, extras):
        segLens = ends-starts
        #permuting order (of length-elements) of both pools
        if vals is None and strands is None:
            numpy.random.shuffle(segLens)
        else:
            permutIndexes = numpy.random.permutation( len(segLens) )
            segLens = segLens[permutIndexes]
            vals = vals[permutIndexes] if vals is not None else None
            strands = strands[permutIndexes] if strands is not None else None
            ids = ids[permutIndexes] if ids is not None else None
            edges = edges[permutIndexes] if edges is not None else None
            weights = weights[permutIndexes] if weights is not None else None
            for key in extras:
                if extras[key] is not None:
                    extras[key] = extras[key][permutIndexes]
        return segLens, vals, strands, ids, edges, weights, extras

    def _permuteIntersegs(self, starts, ends, binLen):
        #(first disregarding start and end-case of bin)
        intersegLens = starts[1:] - ends[:-1]

        #add start and end-case of bin. Double-check with statistician..
        intersegLens = numpy.append(intersegLens, [starts[0], binLen-ends[-1]])

        numpy.random.shuffle(intersegLens)
        return intersegLens

    def _sampleIntervals(self, totalSpace, numElements):
        #two following lines are replaced by more efficient code that avoids array copying
        #splitPoints = numpy.random.random_integers(0, totalSpace, numElements-1)
        #numpy.append(splitPoints, [0,totalSpace])
        splitPoints = numpy.random.random_integers(0, totalSpace, numElements+1)
        splitPoints[-2:] = [0, totalSpace]

        splitPoints.sort()
        return splitPoints[1:] - splitPoints[:-1]
