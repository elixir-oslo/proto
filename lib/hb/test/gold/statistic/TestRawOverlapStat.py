import unittest
from gold.statistic.RawOverlapStat import RawOverlapStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestRawOverlapStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = RawOverlapStat

    def testIncompatibleTracks(self):
        self._assertIncompatibleTracks(SampleTV_Num( anchor=[10,100] ), \
                                       SampleTV( anchor=[10,100], numElements=10 ))
        self._assertIncompatibleTracks(SampleTV( anchor=[10,100], numElements=10 ), \
                                       SampleTV_Num( anchor=[10,100] ))
        self._assertIncompatibleTracks(SampleTV( starts=False, anchor=[10,100], numElements=10 ), \
                                       SampleTV( starts=False, anchor=[10,100], numElements=10 ))

    def test_compute(self):
        self._assertCompute({ 'Both':15, 'Neither':35, 'Only1':35, 'Only2':5 }, \
                            SampleTV( segments=[[10,20], [30,70]], anchor=[10,100] ), \
                            SampleTV( segments=[[15,25], [37,47]], anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({ 'Both':27, 'Neither':30, 'Only1':33, 'Only2':0 }, \
                            SampleTV( segments=[[10,20], [20,70]], anchor=[10,100] ), \
                            SampleTV( segments=[[15,25], [30,47]], anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({ 'Both':0, 'Neither':90, 'Only1':0, 'Only2':0 }, \
                            SampleTV( segments=[], anchor=[10,100] ), \
                            SampleTV( segments=[], anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([RawDataStatUnsplittable] * 2, \
    #                               SampleTV_Num( anchor=[10,100] ), \
    #                               SampleTV_Num( anchor=[10,100] ))

class TestRawOverlapStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = RawOverlapStat

    def test_compute(self):
        self._assertCompute({ 'Both':15, 'Neither':125, 'Only1':35, 'Only2':5 }, \
                            SampleTV( segments=[[10,20], [130,170]], anchor=[10,190] ), \
                            SampleTV( segments=[[15,25], [137,147]], anchor=[10,190] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({ 'Both':0, 'Neither':180, 'Only1':0, 'Only2':0 }, \
                            SampleTV( segments=[], anchor=[10,190] ), \
                            SampleTV( segments=[], anchor=[10,190] ),\
                            assertFunc=self.assertListsOrDicts)
    
if __name__ == "__main__":
    unittest.main()
