from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, MultipleRawDataStatistic
from numpy import concatenate
from gold.track.TrackFormat import TrackFormatReq


class RawOverlapSortedStartEndCodedEventsStat(MagicStatFactory):
    """
    For multiple tracks get a sorted numpy array of coded events encoding wether it is a start or end position
    """
    pass


#class RawOverlapSortedStartEndCodedEventsStatSplittable(StatisticSumResSplittable):
#    pass


class RawOverlapSortedStartEndCodedEventsStatUnsplittable(MultipleRawDataStatistic):
    def _compute(self):
        tvs = [x.getResult() for x in self._children]
        tvStarts = [x.startsAsNumpyArray() for x in tvs]
        tvEnds = [x.endsAsNumpyArray() for x in tvs]
        numTracks = len(tvStarts)

        tvCodedStarts = []
        tvCodedEnds = []
        for i in xrange(numTracks):
            tvCodedStarts.append(tvStarts[i] * 4 + 3)
            tvCodedEnds.append(tvEnds[i] * 4 + 1)

        allSortedCodedEvents = concatenate((concatenate(tvCodedStarts), concatenate(tvCodedEnds)))
        allSortedCodedEvents.sort()
        return allSortedCodedEvents

    def _getTrackFormatReq(self):
        return TrackFormatReq(dense=False)
