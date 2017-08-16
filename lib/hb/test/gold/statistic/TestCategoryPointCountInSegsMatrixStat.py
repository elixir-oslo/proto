import unittest
from collections import OrderedDict
from numpy import array

from gold.statistic.CategoryPointCountInSegsMatrixStat import CategoryPointCountInSegsMatrixStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestCategoryPointCountInSegsMatrixStatUnsplittable(StatUnitTest):
    SPLITTABLE = False
    CLASS_TO_CREATE = CategoryPointCountInSegsMatrixStat

    def test_compute(self):
        t1 = SampleTV(starts=[], vals=[], valDType='S2')
        t2 = SampleTV(segments=[], vals=[], valDType='S2')

        self._assertCompute(None, t1, t2)

        # Testing empty tracks
        t1 = SampleTV(starts=[],
                        vals=[], valDType='S2')
        t2 = SampleTV(segments=[], vals=[], valDType='S2')

        self._assertCompute(None,
                            t1, t2, assertFunc=self.assertListsOrDicts)

        # Testing multiple overlaps of both points and segments
        t1 = SampleTV(starts=[5, 5, 10],
                        vals=['a', 'a', 'a'], valDType='S2')
        t2 = SampleTV(segments=[(0,10), (5,15)], vals=['A', 'A'], valDType='S2')

        self._assertCompute({'Result': OrderedDict([('Matrix', array([[2]], dtype='uint32')),
                                                    ('Rows', array(['a'], dtype='S2')),
                                                    ('Cols', array(['A'], dtype='S2'))])},
                            t1, t2, assertFunc=self.assertListsOrDicts)

        # 3x3 tracks test (without overlap)
        t1 = SampleTV(starts=[5, 5, 15, 15, 25, 25, 25, 35, 55],
                      vals=['a', 'b', 'a', 'c', 'a', 'c', 'b', 'b', 'a'], valDType='S2')
        t2 = SampleTV(segments=[(0,10), (20,30), (20,40), (30,50)],
                      vals=['B', 'B', 'C', 'A'], valDType='S2')

        self._assertCompute({'Result': OrderedDict([('Matrix', array([[0, 2, 1],
                                                                      [1, 2, 2],
                                                                      [0, 1, 1]], dtype='uint32')),
                                                    ('Rows', array(['a', 'b', 'c'], dtype='S2')),
                                                    ('Cols', array(['A', 'B', 'C'], dtype='S2'))])},
                            t1, t2, assertFunc=self.assertListsOrDicts)

    #def test_createChildren(self):
    #    self._assertCreateChildren([YStat], SampleTV( data2 ))

    def runTest(self):
        pass

class TestCategoryPointCountInSegsMatrixStatSplittable(StatUnitTest):
    SPLITTABLE = True
    CLASS_TO_CREATE = CategoryPointCountInSegsMatrixStat

    def setUp(self):
        StatUnitTest.setUp(self)

        from gold.application.LogSetup import setupDebugModeAndLogging
        setupDebugModeAndLogging()
        
    def test_compute(self):
        # Testing empty tracks
        t1 = SampleTV(starts=[],
                        vals=[], valDType='S2')
        t2 = SampleTV(segments=[], vals=[], valDType='S2')

        self._assertCompute(None,
                            t1, t2, assertFunc=self.assertListsOrDicts)

        # 3x3 tracks test (without overlap), 'c' and 'A' only in bin2
        t1 = SampleTV(starts=[5, 5, 15, 25, 25, 115, 125, 135, 155],
                      vals=['a', 'b', 'a', 'a', 'c', 'c', 'b', 'b', 'a'], valDType='S2')
        t2 = SampleTV(segments=[(0,10), (20,30), (20,140), (130,150)],
                      vals=['B', 'B', 'C', 'A'], valDType='S2')

        self._assertCompute({'Result': OrderedDict([('Matrix', array([[0, 2, 1],
                                                                      [1, 1, 2],
                                                                      [0, 1, 2]], dtype='uint32')),
                                                    ('Rows', array(['a', 'b', 'c'], dtype='S2')),
                                                    ('Cols', array(['A', 'B', 'C'], dtype='S2'))])}, t1, t2)

#    def test_createChildren(self):
#        pass

    #def runTest(self):
    #    pass

if __name__ == "__main__":
    #TestCategoryPointCountInSegsMatrixStatSplittable().debug()
    #TestCategoryPointCountInSegsMatrixStatUnsplittable().debug()
    unittest.main()
