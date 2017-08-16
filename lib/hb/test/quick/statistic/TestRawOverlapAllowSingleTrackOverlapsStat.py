import unittest
from quick.statistic.RawOverlapAllowSingleTrackOverlapsStat import RawOverlapAllowSingleTrackOverlapsStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestRawOverlapAllowSingleTrackOverlapsStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = RawOverlapAllowSingleTrackOverlapsStat

    def testIncompatibleTracks(self):
        self._assertIncompatibleTracks(SampleTV_Num( anchor=[10,100] ), \
                                       SampleTV( anchor=[10,100], numElements=10 ))
        self._assertIncompatibleTracks(SampleTV( anchor=[10,100], numElements=10 ), \
                                       SampleTV_Num( anchor=[10,100] ))
        self._assertIncompatibleTracks(SampleTV( starts=False, anchor=[10,100], numElements=10 ), \
                                       SampleTV( starts=False, anchor=[10,100], numElements=10 ))

    def test_compute(self):
        self._assertCompute({ 'Both':15, 'Neither':35, 'Only1':35, 'Only2':5 }, \
                            SampleTV( segments=[[10,20], [30,70]], allowOverlaps=True, anchor=[10,100] ), \
                            SampleTV( segments=[[15,25], [37,47]], allowOverlaps=True, anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({ 'Both':25, 'Neither':30, 'Only1':45, 'Only2':0 }, \
                            SampleTV( segments=[[10,30], [20,70]], allowOverlaps=True, anchor=[10,100] ), \
                            SampleTV( segments=[[15,25], [37,47]], allowOverlaps=True, anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({ 'Both':27, 'Neither':30, 'Only1':28, 'Only2':13 }, \
                            SampleTV( segments=[[10,20], [30,70]], allowOverlaps=True, anchor=[10,100] ), \
                            SampleTV( segments=[[15,35], [27,47]], allowOverlaps=True, anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({ 'Both':53, 'Neither':30, 'Only1':28, 'Only2':0 }, \
                            SampleTV( segments=[[10,30], [20,70]], allowOverlaps=True, anchor=[10,100] ), \
                            SampleTV( segments=[[15,35], [27,47]], allowOverlaps=True, anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({ 'Both':0, 'Neither':90, 'Only1':0, 'Only2':0 }, \
                            SampleTV( segments=[], allowOverlaps=True, anchor=[10,100] ), \
                            SampleTV( segments=[], allowOverlaps=True, anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([RawDataStatUnsplittable] * 2, \
    #                               SampleTV_Num( anchor=[10,100] ), \
    #                               SampleTV_Num( anchor=[10,100] ))

class TestRawOverlapAllowSingleTrackOverlapsStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = RawOverlapAllowSingleTrackOverlapsStat

    def test_compute(self):
        
        self._assertCompute({ 'Both':15, 'Neither':125, 'Only1':35, 'Only2':5 }, \
                            SampleTV( segments=[[10,20], [130,170]], allowOverlaps=True, anchor=[10,190] ), \
                            SampleTV( segments=[[15,25], [137,147]], allowOverlaps=True, anchor=[10,190] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({ 'Both':25, 'Neither':20, 'Only1':145, 'Only2':0 }, \
                            SampleTV( segments=[[10,30], [20,170]], allowOverlaps=True, anchor=[10,190] ), \
                            SampleTV( segments=[[15,25], [137,147]], allowOverlaps=True, anchor=[10,190] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({ 'Both':22, 'Neither':20, 'Only1':28, 'Only2':118 }, \
                            SampleTV( segments=[[10,20], [130,170]], allowOverlaps=True, anchor=[10,190] ), \
                            SampleTV( segments=[[15,35], [27,147]], allowOverlaps=True, anchor=[10,190] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({ 'Both':153, 'Neither':20, 'Only1':28, 'Only2':0 }, \
                            SampleTV( segments=[[10,30], [20,170]], allowOverlaps=True, anchor=[10,190] ), \
                            SampleTV( segments=[[15,35], [27,147]], allowOverlaps=True, anchor=[10,190] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({ 'Both':0, 'Neither':180, 'Only1':0, 'Only2':0 }, \
                            SampleTV( segments=[], allowOverlaps=True, anchor=[10,190] ), \
                            SampleTV( segments=[], allowOverlaps=True, anchor=[10,190] ),\
                            assertFunc=self.assertListsOrDicts)
    
if __name__ == "__main__":
    unittest.main()
