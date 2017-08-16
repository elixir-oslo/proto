import unittest
from gold.statistic.MeanStat import MeanStat
from gold.statistic.SumStat import SumStatSplittable, SumStatUnsplittable
from gold.statistic.CountStat import CountStatSplittable, CountStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestMeanStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = MeanStat

    def testIncompatibleTracks(self):
        self._assertIncompatibleTracks(SampleTV( numElements=5 ))
        self._assertIncompatibleTracks(SampleTV( starts=False, numElements=5 ))
        self._assertIncompatibleTracks(SampleTV( ends=False, numElements=5 ))

    def test_compute(self):
        self._assertCompute(None, SampleTV_Num( vals=[] ))
        self._assertCompute(1.1, SampleTV_Num( vals=[2.0, 1.5, -0.2] ), assertFunc=self.assertAlmostEqual)
        self._assertCompute(55.0, SampleTV_Num( vals=range(111) ), assertFunc=self.assertAlmostEqual)
    
    def test_createChildren(self):
        self._assertCreateChildren([SumStatUnsplittable, CountStatUnsplittable], SampleTV_Num( anchor=[10,20] ))
        self._assertCreateChildren([SumStatSplittable, CountStatSplittable], SampleTV_Num( anchor=[10,120] ))

if __name__ == "__main__":
    unittest.main()
