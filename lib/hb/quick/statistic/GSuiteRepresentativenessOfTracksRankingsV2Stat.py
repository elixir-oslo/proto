from quick.statistic.StatisticV2 import StatisticV2
from quick.statistic.MultitrackSummarizedInteractionV2Stat import MultitrackSummarizedInteractionV2Stat
from gold.statistic.MagicStatFactory import MagicStatFactory
from collections import OrderedDict
from gold.util import CommonConstants
from urllib import unquote


class GSuiteRepresentativenessOfTracksRankingsV2Stat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class GSuiteRepresentativenessOfTracksRankingsV2StatSplittable(StatisticSumResSplittable):
#    pass
            
class GSuiteRepresentativenessOfTracksRankingsV2StatUnsplittable(StatisticV2):
    
    def _init(self, ascending='No', trackTitles='', **kwArgs):
        assert ascending in ['Yes', 'No'], ascending
        self._ascending = ascending == 'Yes'
        assert isinstance(trackTitles, (basestring, list)), 'Mandatory parameter trackTitles is missing or is of wrong type (allowed types: basestring and list)'
        self._trackTitles = [unquote(t) for t in trackTitles.split(CommonConstants.TRACK_TITLES_SEPARATOR)] if \
        isinstance(trackTitles, basestring) else [unquote(t) for t in trackTitles]
    
    def _compute(self):
        resultsList = self._children[0].getResult()
        assert len(resultsList) == len(self._trackTitles), 'One result per track expected.' 
        titleResultPairs = zip(self._trackTitles, resultsList)
        return OrderedDict(sorted(titleResultPairs, key = lambda t: t[1], reverse=(not self._ascending)))
    
    def _createChildren(self):
        self._addChild(MultitrackSummarizedInteractionV2Stat(self._region, self._trackStructure, multitrackSummaryFunc = 'raw', **self._kwArgs))
