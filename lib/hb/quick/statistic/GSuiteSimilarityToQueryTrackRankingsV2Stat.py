from collections import OrderedDict
from quick.statistic.SummarizedInteractionWithOtherTracksV2Stat import SummarizedInteractionWithOtherTracksV2Stat
from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.StatisticV2 import StatisticV2
from gold.util import CommonConstants
from urllib import unquote


class GSuiteSimilarityToQueryTrackRankingsV2Stat(MagicStatFactory):
    '''
    classdocs
    '''
    pass


# class GSuiteSimilarityToQueryTrackRankingsV2StatSplittable(StatisticSumResSplittable):
#    pass

class GSuiteSimilarityToQueryTrackRankingsV2StatUnsplittable(StatisticV2):
    def _init(self, trackTitles='', **kwArgs):
        assert isinstance(trackTitles, (basestring, list)), \
            'Mandatory parameter trackTitles is missing or is of wrong type (allowed types: ' \
            'basestring and list)'
        self._trackTitles = [unquote(t) for t in trackTitles.split(CommonConstants.TRACK_TITLES_SEPARATOR)] if \
            isinstance(trackTitles, basestring) else [unquote(t) for t in trackTitles]

    def _compute(self):
        resultsList = self._children[0].getResult()
        assert len(resultsList) == len(self._trackTitles[1:]), 'One result per track expected.'
        titleResultPairs = zip(self._trackTitles[1:], resultsList)
        return OrderedDict(sorted(titleResultPairs, key=lambda t: t[1], reverse=True))

    def _createChildren(self):
        self._addChild(SummarizedInteractionWithOtherTracksV2Stat(self._region, self._trackStructure, summaryFunc='raw',
                                                                  **self._kwArgs))
