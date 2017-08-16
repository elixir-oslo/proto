from numpy import concatenate, add

from quick.statistic.RawOverlapSortedStartEndCodedEventsStat import RawOverlapSortedStartEndCodedEventsStat

'''
Created on Jul 1, 2015

@author: boris
'''


from gold.track.TrackFormat import TrackFormatReq
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleRawDataStatistic, MultipleTrackStatistic


class RawOverlapEventsStat(MagicStatFactory):
    '''
    Same as RawOverlapCodedEventsStat except we don't need to encode events to know which track is in question, we only encode if it is a start or end
    It will work with arbitrary number of tracks.
    '''
    pass

#class RawOverlapEventsStatSplittable(StatisticSumResSplittable):
#    pass
            
class RawOverlapEventsStatUnsplittable(MultipleTrackStatistic):
    def _compute(self):
        # tvs = [x.getResult() for x in self._children]
        # tvStarts = [x.startsAsNumpyArray()for x in tvs]
        # tvEnds = [x.endsAsNumpyArray() for x in tvs]
        # numTracks = len(tvStarts)
        #
        # tvCodedStarts = []
        # tvCodedEnds = []
        # for i in xrange(numTracks):
        #     tvCodedStarts.append(tvStarts[i] * 4 + 3)
        #     tvCodedEnds.append(tvEnds[i] * 4 + 1)
        #
        # allSortedCodedEvents = concatenate((concatenate(tvCodedStarts), concatenate(tvCodedEnds) ))
        # allSortedCodedEvents.sort()

        allSortedCodedEvents = self._children[0].getResult()

        allEventCodes = (allSortedCodedEvents % 4) - 2

        allSortedDecodedEvents = allSortedCodedEvents / 4
        allEventLengths = allSortedDecodedEvents[1:] - allSortedDecodedEvents[:-1]

        cumulativeCoverStatus = add.accumulate(allEventCodes)

        return allSortedDecodedEvents, allEventLengths, cumulativeCoverStatus

    def _createChildren(self):
        self._addChild(RawOverlapSortedStartEndCodedEventsStat(self._region, self._track, self._track2, **self._kwArgs))
