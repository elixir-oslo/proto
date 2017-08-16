#Untested, to be rewritten
#import stats
from gold.util.RandomUtil import random
import numpy
from numpy import array
from gold.track.TrackView import TrackView
from gold.statistic.RawDataStat import RawDataStat
from gold.track.Track import Track
from gold.track.TrackFormat import NeutralTrackFormatReq
from test.gold.track.common.SampleTrackView import SampleTV_Num
from gold.util.CommonFunctions import isIter
from gold.util.CustomExceptions import AbstractClassError
from config.Config import DebugConfig

class RandomizedTrack(Track):
    IS_MEMOIZABLE = False
    WORKS_WITH_MINIMAL = True

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, origTrack, origRegion, randIndex, **kwArgs):
        self._origTrack = origTrack
        self.trackName = origTrack.trackName + ['Randomized', str(randIndex)]
        self._origRegion = origRegion
        self._trackFormatReq = NeutralTrackFormatReq()
        self._cachedTV = None
        self._minimal = ('minimal' in kwArgs and kwArgs['minimal'] == True)

        from gold.formatconversion.FormatConverter import TrivialFormatConverter
        self.formatConverters = [TrivialFormatConverter] #To allow construction of uniqueID
        self._trackId = None #To allow construction of uniqueID

    def _checkTrackFormat(self, origTV):
        pass

    def getTrackView(self, region):
        #print 'TEMP5: get tv for reg: ',region, ' for TrackName: ', self.trackName
        #print str(type(self._origRegion)) + " and " + str(type(region))
        if DebugConfig.USE_SLOW_DEFENSIVE_ASSERTS:
            assert (not isIter(self._origRegion) and self._origRegion  == region) or \
                    (isIter(self._origRegion) and region in self._origRegion)

        if self._minimal and not self.WORKS_WITH_MINIMAL:
            return self._origTrack.getTrackView(region)

        return self._getTrackView(region)

    def _getTrackView(self, region):
        #if self._cachedTV is None:
        rawData = RawDataStat(region, self._origTrack, self._trackFormatReq)
        origTV = rawData.getResult()

        self._checkTrackFormat(origTV)
        assert(not origTV.allowOverlaps)
        assert(origTV.borderHandling == 'crop')
        assert region == origTV.genomeAnchor

        starts, ends, vals, strands, ids, edges, weights, extras = \
            self._createRandomizedNumpyArrays(len(origTV.genomeAnchor), origTV.startsAsNumpyArray(), \
                                              origTV.endsAsNumpyArray(), origTV.valsAsNumpyArray(), \
                                              origTV.strandsAsNumpyArray(), origTV.idsAsNumpyArray(), \
                                              origTV.edgesAsNumpyArray(), origTV.weightsAsNumpyArray(), \
                                              origTV.allExtrasAsDictOfNumpyArrays(), region)

        starts, ends, vals, strands, ids, edges, weights, extras = \
            self._undoTrackViewChanges(starts, ends, vals, strands, ids, edges, weights, extras, origTV)

        from gold.util.CommonFunctions import getClassName
        self._cachedTV = TrackView(origTV.genomeAnchor, starts, ends, vals, strands, ids, edges, weights, \
                                   origTV.borderHandling, origTV.allowOverlaps, extraLists=extras)

        assert self._trackFormatReq.isCompatibleWith(self._cachedTV.trackFormat), 'Incompatible track-format: '\
               + str(self._trackFormatReq) + ' VS ' + str(self._cachedTV.trackFormat)
        return self._cachedTV

    def _undoTrackViewChanges(self, starts, ends, vals, strands, ids, edges, weights, extras, origTV):
        if origTV.trackFormat.isPoints():
            ends = None

        elif origTV.trackFormat.isPartitionOrStepFunction():
            ends = numpy.append([0], ends)
            starts = None

        if starts is not None:
            starts += origTV.genomeAnchor.start

        if ends is not None:
            ends += origTV.genomeAnchor.start

        return starts, ends, vals, strands, ids, edges, weights, extras

    def _createRandomizedNumpyArrays(self, binLen, starts, ends, vals, strands, ids, edges, weights, extras, region):
        raise AbstractClassError
