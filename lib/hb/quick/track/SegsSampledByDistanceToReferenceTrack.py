import numpy
from gold.track.RandomizedTrack import RandomizedTrack
from gold.util.CustomExceptions import IncompatibleTracksError, InvalidRunSpecException
from gold.track.Track import PlainTrack
from gold.track.SegsSampledByIntensityTrack import SegsSampledByIntensityTrack
from collections import OrderedDict
#from quick.util.CommonFunctions import convertTNstrToTNListFormat
from urllib import unquote
from config.Config import IS_EXPERIMENTAL_INSTALLATION
from random import randint, random

class SegsSampledByDistanceToReferenceTrack(SegsSampledByIntensityTrack):
    WORKS_WITH_MINIMAL = False

    def _checkTrackFormat(self, origTV):
        if origTV.trackFormat.isDense():
            raise IncompatibleTracksError()

    def _createRandomizedNumpyArrays(self, binLen, starts, ends, vals, strands, ids, edges, weights, extras, region):
        referenceTV = PlainTrack(self._trackNameIntensity).getTrackView(region) #self._trackNameIntensity based on naming convenience wrt. inheritance
        if len(referenceTV.valsAsNumpyArray())==0:
            raise InvalidRunSpecException('Error: No reference data available for sampling randomized locations in region' + \
                                          str(region) + \
                                          '. Please check that the reference track was created with the same main track that is being randomized in this analysis.')


        if referenceTV.trackFormat.isDense():
            raise InvalidRunSpecException('Error: Cannot sample by distance to reference if reference is a dense track')
        else:
            return self._createRandomizedNumpyArraysFromDistanceToReference(binLen, starts, ends, vals, strands, ids, edges, weights, extras, referenceTV)

    def _createRandomizedNumpyArraysFromDistanceToReference(self, binLen, starts, ends, vals, strands, ids, edges, weights, extras, referenceTV):
        if len(starts)==0:
            assert len(ends)==0
            return starts, ends, vals, strands, ids, edges, weights, extras

        #assert (ends == starts+1).all() #temp, remove after checking compatibility below..

        #elementLength = ends[0]-starts[0]
        #assert ((ends-starts)==elementLength).all(), numpy.unique(ends-starts)

        elementLengths = ends - starts

        #Permute vals and strands. Later also segment lengths..
        if vals is not None or strands is not None:
            permutedIndexes = numpy.random.permutation(max(len(starts), len(ends)))
            if vals is not None:
                vals = vals[permutedIndexes]
            if strands is not None:
                strands = strands[permutedIndexes]
            if ids is not None:
                ids = ids[permutedIndexes]
            if edges is not None:
                edges = edges[permutedIndexes]
            if weights is not None:
                weights = weights[permutedIndexes]
            for key in extras:
                extras[key] = extras[key][permutedIndexes]

        #Main permutation of locations
        offsetsFromReference = vals #temporary solution, should find this automatically..
        assert offsetsFromReference is not None
        numElements = len(offsetsFromReference)
        #print offsetsFromReference
        referenceStarts = referenceTV.startsAsNumpyArray()
        referenceEnds = referenceTV.endsAsNumpyArray()
        referenceSpacings = referenceStarts[1:] - referenceEnds[:-1]
        numReferences = len(referenceStarts)

        tries = 0
        while (True):
            tries+=1
            assert tries<30
            sampledPositions = []
            for i in range(numElements):
                offset = offsetsFromReference[i]
                #print 'Offset: ', offset, 'Num large enough spacings: ', sum(referenceSpacings>offset*2), 'out of', len(referenceSpacings)

                #tries = 0
                #while (True):
                #    tries +=1
                #    assert tries<500, 'did not find suited location (10 tries without finding enough space from a randomly selected reference element..'
                #
                #    refIndex = randint(0, numReferences-1)
                #    newStart = referenceStarts[refIndex] - offset
                #    if refIndex==0:
                #        if newStart>0:
                #            break
                #    else:
                #        #print 'Try: ', tries, refIndex, 'Offset: ',offset, 'Interval: ', referenceStarts[refIndex] - referenceEnds[refIndex-1], 'Coords: ', referenceEnds[refIndex-1], newStart, referenceStarts[refIndex]
                #        if newStart > referenceEnds[refIndex-1]+offset: #should be far enough away also from preceding element
                #            break
                #print 'USED %i tries' %tries
                if offset==0:
                    refElIndex = randint(0,len(referenceStarts)-1)
                    newStart = randint(referenceStarts[refElIndex], referenceEnds[refElIndex]-1)
                else:
                    candidateRefIndices = numpy.where(referenceSpacings > offset*2)[0]
                    #candidateRefIndices += 1 #+1 to get element after spacing - temp..
                    assert len(candidateRefIndices) >= 1, 'No candidates!'

                    totalCandidateSpaces = len(candidateRefIndices) + (0.5 if referenceStarts[0] > offset else 0) + (0.5 if binLen-referenceEnds[-1]>offset else 0)
                    #consider space before first or after last
                    if referenceStarts[0] > offset and random() < (0.5/totalCandidateSpaces): #should happen in 1 out of possible spacings, also multiplied by 0.5 as this space is only close to a single reference element..
                        newStart = referenceStarts[0] - offset
                    elif binLen-referenceEnds[-1]>offset and random() < (0.5/totalCandidateSpaces):
                        newStart = referenceEnds[-1]+offset
                    else:
                        refIndex = candidateRefIndices[ randint(0, len(candidateRefIndices)-1) ]
                        newStart = (referenceEnds[refIndex] + offset) if random()<0.5 else (referenceStarts[refIndex+1] - offset)
                        assert referenceEnds[refIndex]+offset <= newStart <= referenceStarts[refIndex+1]-offset, (referenceEnds[refIndex], newStart, referenceStarts[refIndex+1])
                sampledPositions.append(newStart)

            assert len(sampledPositions) == numElements
            sampledElementLengths = elementLengths
            numpy.random.shuffle(sampledElementLengths)
            sampledPositions = numpy.array(sampledPositions)
            sampledPositions.sort()
            sampledStarts = (sampledPositions - (sampledElementLengths/2)).astype('int')
            sampledEnds = (sampledPositions + ((sampledElementLengths+1)/2)).astype('int')

            validSpacings = ((sampledStarts[1:]-sampledEnds[:-1])>0)
            #print sampledPositions, sampledStarts, sampledEnds
            #print 'Try ',tries, '- num valid: ', sum(validSpacings), ' out of ', len(validSpacings)
            #print validSpacings, validSpacings.dtype, numpy.array([True]), numpy.array([True]).dtype
            #print numpy.concatenate([validSpacings, numpy.array([True])]), numpy.concatenate([validSpacings, numpy.array([True])]).dtype
            #print numpy.concatenate([numpy.array([True]), validSpacings]), numpy.concatenate([numpy.array([True], validSpacings)]).dtype
            #Invalidates element before and after an invalid spacing:
            #validIndices = numpy.logical_and( numpy.concatenate([validSpacings, numpy.array([True])]), numpy.concatenate([numpy.array([True]), validSpacings]))
            #print validSpacings
            #print validSpacings.all()
            if validSpacings.all():
                if (sampledStarts>=0).all() and (sampledEnds<binLen).all():
                    assert (sampledStarts>=0).all(), sampledStarts
                    assert (sampledEnds<binLen).all(), (binLen, sampledEnds)
                    assert ((sampledStarts[1:]-sampledEnds[:-1])>0).all(), (((sampledStarts[1:]-sampledEnds[:-1])>0), sampledElementLengths, sampledStarts, sampledEnds)
                    #sortedIndexes = numpy.argsort(sampledStarts)
                    return sampledStarts, sampledEnds, vals, strands, ids, edges, weights, extras
                #else:
                    #print 'Sampled coordinates outside bin (size %s): ' %binLen, sampledStarts, sampledEnds
