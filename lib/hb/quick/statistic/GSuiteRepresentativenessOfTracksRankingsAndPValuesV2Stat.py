from quick.statistic.StatisticV2 import StatisticV2
from gold.track.TrackStructure import TrackStructure
from quick.statistic.RandomizationManagerV3Stat import RandomizationManagerV3Stat
from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.MultitrackSummarizedInteractionV2Stat import MultitrackSummarizedInteractionV2Stat
from collections import OrderedDict
from gold.util import CommonConstants
from urllib import unquote


class GSuiteRepresentativenessOfTracksRankingsAndPValuesV2Stat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class GSuiteRepresentativenessOfTracksRankingsAndPValuesV2StatSplittable(StatisticSumResSplittable):
#    pass
            
class GSuiteRepresentativenessOfTracksRankingsAndPValuesV2StatUnsplittable(StatisticV2):
    
    def _init(self, trackTitles='', **kwArgs):
        assert isinstance(trackTitles, (basestring, list)), 'Mandatory parameter trackTitles is missing or is of wrong type (allowed types: basestring and list)'
        self._trackTitles = [unquote(t) for t in trackTitles.split(CommonConstants.TRACK_TITLES_SEPARATOR)] if \
        isinstance(trackTitles, basestring) else [unquote(t) for t in trackTitles]
    
    def _compute(self):
        resultTuples = []
        observedResults = self._children[0].getResult()
        assert len(observedResults) == len(self._children[1:]), 'Observed results list and MC children list must be of same length'
        for i, chld in enumerate(self._children[1:]):
            chldRes = chld.getResult()
            resultTuples.append((self._trackTitles[i], [observedResults[i], chldRes['P-value']]))
        
        return OrderedDict(sorted(resultTuples, key = lambda t: (-t[1][1], t[1][0]), reverse = True))
                  
    
    def _createChildren(self):
        self._addChild(MultitrackSummarizedInteractionV2Stat(self._region, self._trackStructure, multitrackSummaryFunc = 'raw', **self._kwArgs))
        queryTrackList = self._trackStructure.getQueryTrackList()
        for i, t1 in enumerate(queryTrackList):
            ts = TrackStructure()
#             print 't1: ', t1.trackName
            ts[TrackStructure.QUERY_KEY] = [t1]
#             for j, t in enumerate(queryTrackList[:i]):
#                 print 't%i' % j, t.trackName
#             for j, t in enumerate(queryTrackList[i+1:]):
#                 print 't%i' % j, t.trackName
            ts[TrackStructure.REF_KEY] = queryTrackList[:i] + queryTrackList[i+1:]
            self._addChild(RandomizationManagerV3Stat(self._region, ts, **self._kwArgs))
