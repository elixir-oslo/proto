from gold.origdata.GenomeElement import GenomeElement
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import MultipleTrackStatistic
from gold.track.TrackFormat import TrackFormatReq
from gold.track.TrackView import TrackView
from quick.statistic.RawOverlapSortedStartEndCodedEventsStat import RawOverlapSortedStartEndCodedEventsStat
from numpy import array


class UnionTrackOfGSuiteTracksStat(MagicStatFactory):
    """
    Generate a track that represents the union of all the tracks in the GSuite
    """
    pass


#class UnionTrackOfGSuiteTracksStatSplittable(StatisticSumResSplittable):
#    pass


class UnionTrackOfGSuiteTracksStatUnsplittable(MultipleTrackStatistic):
    def _compute(self):
        tv1 = self._children[0].getResult()
        allSortedCodedEvents = self._children[1].getResult()

        allEventCodes = (allSortedCodedEvents % 4) - 2

        allSortedDecodedEvents = allSortedCodedEvents / 4

        from numpy.ma import add
        cumulativeCoverStatus = add.accumulate(allEventCodes)
        assert len(cumulativeCoverStatus) == len(allSortedDecodedEvents), str(len(allSortedDecodedEvents))

        unionStartList = []
        unionEndList = []

        startedFlag = False
        for i, cumVal in enumerate(cumulativeCoverStatus):
            if cumVal == 1 and not startedFlag:
                startPos = allSortedDecodedEvents[i]
                startedFlag = True
            elif cumVal == 0:
                if startPos:
                    unionStartList.append(startPos)
                    unionEndList.append(allSortedDecodedEvents[i])
                    startPos = None
                    startedFlag = False


        return [GenomeElement(start=x, end=y) for x, y in zip(unionStartList, unionEndList)]

        # return TrackView(genomeAnchor=tv1.genomeAnchor, startList=array(unionStartList),
        #                  endList=array(unionEndList), valList=None,
        #                  strandList=None, idList=None, edgesList=None,
        #                  weightsList=None, borderHandling=tv1.borderHandling,
        #                  allowOverlaps=False)


    def _createChildren(self):
        self._addChild(RawDataStat(self._region, self._track, TrackFormatReq(dense=False)))
        self._addChild(RawOverlapSortedStartEndCodedEventsStat(self._region, self._track, self._track2, **self._kwArgs))


