'''
Created on Jul 2, 2015

@author: boris
'''

import unittest

from numpy import array
from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
from quick.statistic.CollectionVsCollectionStat import CollectionVsCollectionStat
from quick.statistic.StatFacades import TpRawOverlapStat


class TestCollectionVsCollectionStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = CollectionVsCollectionStat
    SPLITTABLE = False

#     def testIncompatibleTracks(self):
#         self._assertIncompatibleTracks(SampleTV_Num( anchor=[10,100] ), \
#                                        SampleTV( anchor=[10,100], numElements=10 ))
#         self._assertIncompatibleTracks(SampleTV( anchor=[10,100], numElements=10 ), \
#                                        SampleTV_Num( anchor=[10,100] ))
#         self._assertIncompatibleTracks(SampleTV( starts=False, anchor=[10,100], numElements=10 ), \
#                                        SampleTV( starts=False, anchor=[10,100], numElements=10 ))

    def test_compute(self):
        self._assertCompute({'Result': {'Matrix': array([[8, 4, 2], [4, 8, 4], [3, 5, 8]], dtype='float64'),
                                        'Rows':['t1', 't2', 't3'], 'Cols':['t4', 't5', 't6']}}, \
                            SampleTV( segments=[[2,4], [10,14], [18,20]], anchor=[1,23] ), \
                            SampleTV( segments=[[1,3], [9,11], [17,21]], anchor=[1,23] ),\
                            SampleTV( segments=[[1,5], [8,10], [19,22]], anchor=[1,23] ),\
                            SampleTV( segments=[[2,4], [10,14], [18,20]], anchor=[1,23] ), \
                            SampleTV( segments=[[1,3], [9,11], [17,21]], anchor=[1,23] ),\
                            SampleTV( segments=[[1,5], [8,10], [20,22]], anchor=[1,23] ),\
                            assertFunc=self.assertListsOrDicts, \
                            trackTitles='t1|||t2|||t3|||t4|||t5|||t6', \
                            firstCollectionTrackNr = '3', \
                            rawStatistic='TpRawOverlapStat')

        self._assertCompute({'Result': {'Matrix': array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], dtype='float64'),
                                        'Rows':['t1', 't2', 't3'], 'Cols':['t4', 't5', 't6']}},\
                            SampleTV( segments=[], anchor=[10,100] ), \
                            SampleTV( segments=[], anchor=[10,100] ),\
                            SampleTV( segments=[], anchor=[10,100] ),\
                            SampleTV( segments=[], anchor=[10,100] ), \
                            SampleTV( segments=[], anchor=[10,100] ),\
                            SampleTV( segments=[], anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts, \
                            trackTitles='t1|||t2|||t3|||t4|||t5|||t6', \
                            firstCollectionTrackNr = '3', \
                            rawStatistic='TpRawOverlapStat')
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([RawDataStatUnsplittable] * 2, \
    #                               SampleTV_Num( anchor=[10,100] ), \
    #                               SampleTV_Num( anchor=[10,100] ))

class TestCollectionVsCollectionStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = CollectionVsCollectionStat
    SPLITTABLE = True

    def test_compute(self):
        self._assertCompute({'Result': {'Matrix': array([[108, 5, 102], [5, 8, 7], [103, 7, 108]], dtype='float64'),
                                        'Rows':['t1', 't2', 't3'], 'Cols':['t4', 't5', 't6']}},
                            SampleTV( segments=[[2,4], [10,14], [18,120]], anchor=[1,123] ), \
                            SampleTV( segments=[[1,3], [9,11], [117,121]], anchor=[1,123] ),\
                            SampleTV( segments=[[1,5], [8,10], [19,122]], anchor=[1,123] ),\
                            SampleTV( segments=[[2,4], [10,14], [18,120]], anchor=[1,123] ), \
                            SampleTV( segments=[[1,3], [9,11], [117,121]], anchor=[1,123] ),\
                            SampleTV( segments=[[1,5], [8,10], [20,122]], anchor=[1,123] ),\
                            assertFunc=self.assertListsOrDicts, \
                            trackTitles='t1|||t2|||t3|||t4|||t5|||t6', \
                            rawStatistic='TpRawOverlapStat', \
                            firstCollectionTrackNr = '3')

        #Testing for combineResults with some bins only having nan as result
        self._assertCompute({'Result': {'Matrix': array([[5.8998358, 4.14039409, 5.43220743],
                                                         [4.14039409, 49.75, 5.2213555],
                                                         [5.4328301, 5.21119818, 5.49898888]], dtype='float64'),
                                        'Rows':['t1', 't2', 't3'], 'Cols':['t4', 't5', 't6']}},
                            SampleTV( segments=[[2,4], [10,14], [18,120]], anchor=[1,223] ), \
                            SampleTV( segments=[[1,3], [9,11], [117,121]], anchor=[1,223] ),\
                            SampleTV( segments=[[1,5], [8,10], [19,122]], anchor=[1,223] ),\
                            SampleTV( segments=[[2,4], [10,14], [18,120]], anchor=[1,223] ), \
                            SampleTV( segments=[[1,3], [9,11], [117,121]], anchor=[1,223] ),\
                            SampleTV( segments=[[1,5], [8,10], [20,122]], anchor=[1,223] ),\
                            assertFunc=self.assertListsOrDicts, \
                            trackTitles='t1|||t2|||t3|||t4|||t5|||t6', \
                            rawStatistic='SimpleObservedToExpectedBpOverlapStat', \
                            firstCollectionTrackNr = '3')

        self._assertCompute({'Result': {'Matrix': array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], dtype='float64'),
                                        'Rows':['t1', 't2', 't3'], 'Cols':['t4', 't5', 't6']}},\
                            SampleTV( segments=[], anchor=[10,180] ), \
                            SampleTV( segments=[], anchor=[10,180] ),\
                            SampleTV( segments=[], anchor=[10,180] ),\
                            SampleTV( segments=[], anchor=[10,180] ), \
                            SampleTV( segments=[], anchor=[10,180] ),\
                            SampleTV( segments=[], anchor=[10,180] ),\
                            assertFunc=self.assertListsOrDicts, \
                            trackTitles='t1|||t2|||t3|||t4|||t5|||t6', \
                            rawStatistic='TpRawOverlapStat', \
                            firstCollectionTrackNr = '3')

if __name__ == "__main__":
    unittest.main()
