import unittest
from gold.statistic.MultitrackFocusedCoverageDepthStat import MultitrackFocusedCoverageDepthStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestMultitrackFocusedCoverageDepthStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = MultitrackFocusedCoverageDepthStat

    def testIncompatibleTracks(self):
        self._assertIncompatibleTracks(SampleTV_Num( anchor=[10,100] ), \
                                       SampleTV( anchor=[10,100], numElements=10 ))
        self._assertIncompatibleTracks(SampleTV( anchor=[10,100], numElements=10 ), \
                                       SampleTV_Num( anchor=[10,100] ))
        self._assertIncompatibleTracks(SampleTV( starts=False, anchor=[10,100], numElements=10 ), \
                                       SampleTV( starts=False, anchor=[10,100], numElements=10 ))

    def test_compute(self):
        self._assertCompute({
                             'BinSize': 21,
                             (True, 0, 0):3,
                             (True, 0, 1):4,
                             (True, 0, 2):1,
                             (True, 1, 0):1,
                             (True, 1, 1):6,
                             (True, 1, 2):1,
                             (True, 2, 0):3,
                             (True, 2, 1):4,
                             (True, 2, 2):1,
                             (False, 0, 0):7,
                             (False, 0, 1):4,
                             (False, 0, 2):3,
                             (False, 1, 0):7,
                             (False, 1, 1):6,
                             (False, 1, 2):1,
                             (False, 2, 0):7,
                             (False, 2, 1):4,
                             (False, 2, 2):3
                             }, \
                            SampleTV( segments=[[2,8], [10,14], [18,20]], anchor=[1,22] ), \
                            SampleTV( segments=[[1,3], [9,11], [17,21]], anchor=[1,22] ),\
                            SampleTV( segments=[[1,5], [8,10], [20,22]], anchor=[1,22] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({
                             'BinSize': 30,
                             (True, 0, 0):4,
                             (True, 0, 1):3,
                             (True, 0, 2):2,
                             (True, 0, 3):0,
                             (True, 1, 0):2,
                             (True, 1, 1):4,
                             (True, 1, 2):2,
                             (True, 1, 3):0,
                             (True, 2, 0):1,
                             (True, 2, 1):5,
                             (True, 2, 2):3,
                             (True, 2, 3):0,
                             (True, 3, 0):2,
                             (True, 3, 1):4,
                             (True, 3, 2):2,
                             (True, 3, 3):0,
                             (False, 0, 0):10,
                             (False, 0, 1):5,
                             (False, 0, 2):5,
                             (False, 0, 3):1,
                             (False, 1, 0):10,
                             (False, 1, 1):7,
                             (False, 1, 2):4,
                             (False, 1, 3):1,
                             (False, 2, 0):10,
                             (False, 2, 1):8,
                             (False, 2, 2):3,
                             (False, 2, 3):0,
                             (False, 3, 0):10,
                             (False, 3, 1):7,
                             (False, 3, 2):4,
                             (False, 3, 3):1
                             }, \
                            SampleTV( segments=[[8,12], [24,29]], anchor=[1,31] ),\
                            SampleTV( segments=[[2,4], [10,14], [18,20]], anchor=[1,31] ), \
                            SampleTV( segments=[[1,3], [9,11], [17,21], [25,26]], anchor=[1,31] ),\
                            SampleTV( segments=[[1,5], [8,10], [20,22]], anchor=[1,31] ),\
                            assertFunc=self.assertListsOrDicts)
#         self._assertCompute({ 'Both':27, 'Neither':30, 'Only1':33, 'Only2':0 }, \
#                             SampleTV( segments=[[10,20], [20,70]], anchor=[10,100] ), \
#                             SampleTV( segments=[[15,25], [30,47]], anchor=[10,100] ),\
#                             assertFunc=self.assertListsOrDicts)
        self._assertCompute({
                             'BinSize': 90,
                             (True, 0, 0):0,
                             (True, 0, 1):0,
                             (True, 0, 2):0,
                             (True, 1, 0):0,
                             (True, 1, 1):0,
                             (True, 1, 2):0,
                             (True, 2, 0):0,
                             (True, 2, 1):0,
                             (True, 2, 2):0,
                             (False, 0, 0):90,
                             (False, 0, 1):0,
                             (False, 0, 2):0,
                             (False, 1, 0):90,
                             (False, 1, 1):0,
                             (False, 1, 2):0,
                             (False, 2, 0):90,
                             (False, 2, 1):0,
                             (False, 2, 2):3
                             }, \
                            SampleTV( segments=[], anchor=[10,100] ), \
                            SampleTV( segments=[], anchor=[10,100] ),\
                            SampleTV( segments=[], anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([RawDataStatUnsplittable] * 2, \
    #                               SampleTV_Num( anchor=[10,100] ), \
    #                               SampleTV_Num( anchor=[10,100] ))

class TestMultitrackFocusedCoverageDepthStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = MultitrackFocusedCoverageDepthStat

    def test_compute(self):
        self._assertCompute({
                             'BinSize': 21,
                             (True, 0, 0):3,
                             (True, 0, 1):4,
                             (True, 0, 2):1,
                             (True, 1, 0):1,
                             (True, 1, 1):6,
                             (True, 1, 2):1,
                             (True, 2, 0):3,
                             (True, 2, 1):4,
                             (True, 2, 2):1,
                             (False, 0, 0):7,
                             (False, 0, 1):4,
                             (False, 0, 2):3,
                             (False, 1, 0):7,
                             (False, 1, 1):6,
                             (False, 1, 2):1,
                             (False, 2, 0):7,
                             (False, 2, 1):4,
                             (False, 2, 2):3
                             }, \
                            SampleTV( segments=[[2,4], [10,14], [18,20]], anchor=[1,22] ), \
                            SampleTV( segments=[[1,3], [9,11], [17,21]], anchor=[1,22] ),\
                            SampleTV( segments=[[1,5], [8,10], [20,22]], anchor=[1,22] ),\
                            assertFunc=self.assertListsOrDicts)
#         self._assertCompute({ 'Both':15, 'Neither':125, 'Only1':35, 'Only2':5 }, \
#                             SampleTV( segments=[[10,20], [130,170]], anchor=[10,190] ), \
#                             SampleTV( segments=[[15,25], [137,147]], anchor=[10,190] ),\
#                             assertFunc=self.assertListsOrDicts)
#         self._assertCompute({
#                              'BinSize': 21,
#                              (True, 0, 0):0,
#                              (True, 0, 1):0,
#                              (True, 0, 2):0,
#                              (True, 1, 0):0,
#                              (True, 1, 1):0,
#                              (True, 1, 2):0,
#                              (True, 2, 0):0,
#                              (True, 2, 1):0,
#                              (True, 2, 2):0,
#                              (False, 0, 0):180,
#                              (False, 0, 1):0,
#                              (False, 0, 2):0,
#                              (False, 1, 0):180,
#                              (False, 1, 1):0,
#                              (False, 1, 2):0,
#                              (False, 2, 0):180,
#                              (False, 2, 1):0,
#                              (False, 2, 2):3
#                              }, \
#                             SampleTV( segments=[], anchor=[10,190] ), \
#                             SampleTV( segments=[], anchor=[10,190] ),\
#                             SampleTV( segments=[], anchor=[10,190] ),\
#                             assertFunc=self.assertListsOrDicts)
    
if __name__ == "__main__":
    unittest.main()
