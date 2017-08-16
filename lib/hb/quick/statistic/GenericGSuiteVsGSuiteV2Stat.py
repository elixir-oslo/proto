from urllib import unquote
from gold.util import CommonConstants
from collections import OrderedDict

'''
Created on Feb 29, 2016

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.StatisticV2 import StatisticV2
from quick.result.model.TableData import TableData


class GenericGSuiteVsGSuiteV2Stat(MagicStatFactory):
    '''
    classdocs
    '''
    pass


# class GenericGSuiteVsGSuiteV2StatSplittable(StatisticSumResSplittable):
#    pass

class GenericGSuiteVsGSuiteV2StatUnsplittable(StatisticV2):
    def _init(self, pairwiseStatistic, queryTrackTitleList=None, refTrackTitleList=None,
              removeZeroRow='No', removeZeroColumn='No', **kwArgs):
        assert isinstance(queryTrackTitleList, (basestring,
                                                list)), '''Mandatory parameter queryTrackTitleList is missing or is
                                                of wrong type (allowed types: str and list)'''
        assert isinstance(refTrackTitleList, (basestring,
                                              list)), '''Mandatory parameter refTrackTitleList is missing or is
                                              of wrong type (allowed types: str and list)'''
        assert removeZeroRow in ['No', 'Yes'], 'removeZeroRow argument must be one of Yes or No'
        assert removeZeroColumn in ['No', 'Yes'], 'removeZeroColumn argument must be one of Yes or No'

        self._rawStatistic = self.getRawStatisticClass(pairwiseStatistic)

        self._queryTrackTitles = [unquote(t) for t in
                                  queryTrackTitleList.split(CommonConstants.TRACK_TITLES_SEPARATOR)] if \
            isinstance(queryTrackTitleList, basestring) else [unquote(t) for t in queryTrackTitleList]

        self._refTrackTitles = [unquote(t) for t in refTrackTitleList.split(CommonConstants.TRACK_TITLES_SEPARATOR)] \
            if isinstance(refTrackTitleList, basestring) else [unquote(t) for t in refTrackTitleList]

        self._removeZeroRow = removeZeroRow == 'Yes'
        self._removeZeroCol = removeZeroColumn == 'Yes'

        self._childrenDict = OrderedDict()

    def _compute(self):
        resDict = TableData()
        for titlePair, child in self._childrenDict.iteritems():
            # if titlePair[0] not in resDict:
            #     resDict[titlePair[0]] = OrderedDict()
            resDict[titlePair[0]][titlePair[1]] = child.getResult()

        if (self._removeZeroCol or self._removeZeroRow):
            resDict = resDict.getReducedTableData(removeRows=self._removeZeroRow,
                                                  removeColumns=self._removeZeroCol,
                                                  removeValues=[0])

        return resDict

    def _createChildren(self):
        for i, t1 in enumerate(self._trackStructure.getQueryTrackList()):
            for j, t2 in enumerate(self._trackStructure.getReferenceTrackList()):
                titlePair = (self._queryTrackTitles[i], self._refTrackTitles[j])
                self._childrenDict[titlePair] = self._addChild(self._rawStatistic(self._region, t1, t2, **self._kwArgs))
