'''
Created on Feb 29, 2016

@author: boris
'''

from collections import OrderedDict

from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.GenericGSuiteVsGSuiteV2Stat import GenericGSuiteVsGSuiteV2Stat
from quick.statistic.SingleValueOverlapStat import SingleValueOverlapStat
from quick.statistic.StatisticV2 import StatisticV2

RAW_OVERLAP_TABLE_RESULT_KEY = 'Raw_overlap_table'
SIMILARITY_SCORE_TABLE_RESULT_KEY = 'Similarity_score_table'

class GSuiteVsGSuiteFullAnalysisV2Stat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class GSuiteVsGSuiteFullAnalysisV2StatSplittable(StatisticSumResSplittable):
#    pass
            
class GSuiteVsGSuiteFullAnalysisV2StatUnsplittable(StatisticV2):
    
    def _init(self, similarityStatClassName=None, **kwArgs):
        self._similarityStatClassName = similarityStatClassName

    def _compute(self):
        res = OrderedDict()
        res[RAW_OVERLAP_TABLE_RESULT_KEY] = self._rawOverlapTable.getResult()
        res[SIMILARITY_SCORE_TABLE_RESULT_KEY] = self._similarityScoreTable.getResult()
        return res
    
    def _createChildren(self):
        self._rawOverlapTable = self._addChild(GenericGSuiteVsGSuiteV2Stat(self._region, self._trackStructure, pairwiseStatistic = SingleValueOverlapStat, **self._kwArgs))
        self._similarityScoreTable = self._addChild(GenericGSuiteVsGSuiteV2Stat(self._region, self._trackStructure, pairwiseStatistic = self._similarityStatClassName, **self._kwArgs))
