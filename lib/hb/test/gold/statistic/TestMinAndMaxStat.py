import unittest
from gold.statistic.MinAndMaxStat import MinAndMaxStat
from gold.statistic.RawDataStat import RawDataStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
from numpy import nan

class TestMinAndMaxStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = MinAndMaxStat

    def testIncompatibleTracks(self):
        self._assertIncompatibleTracks(SampleTV( anchor=[10,100], numElements=5 ))
        self._assertIncompatibleTracks(SampleTV( starts=False, anchor=[10,100], numElements=5 ))
        self._assertIncompatibleTracks(SampleTV( ends=False, anchor=[10,100], numElements=5 ))

    def test_compute(self):
        self._assertCompute({'min':-0.7, 'max':2.0}, SampleTV_Num( vals=[2.0, 1.5, -0.7] ), \
            assertFunc=self.assertListsOrDicts)
        self._assertCompute({'min':nan, 'max':nan}, SampleTV_Num( vals=[2.0, 1.5, nan] ), \
            assertFunc=self.assertListsOrDicts)
        self._assertCompute(None, SampleTV_Num( vals=[] ), \
            assertFunc=self.assertListsOrDicts)
        
    def test_createChildren(self):
        self._assertCreateChildren([RawDataStatUnsplittable], SampleTV_Num( anchor=[10,100] ))

class TestMinAndMaxStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = MinAndMaxStat

    def test_compute(self):
        self._assertCompute({'min':-0.7, 'max':2.0}, SampleTV_Num( vals=[2.0, 1.5, -0.7], anchor=[99,102] ),  \
            assertFunc=self.assertListsOrDicts)
        
if __name__ == "__main__":
    unittest.main()
