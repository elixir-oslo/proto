import unittest
from gold.statistic.CountPointStat import CountPointStat
from gold.statistic.RawDataStat import RawDataStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestCountPointStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = CountPointStat

    def testIncompatibleTracks(self):
        self._assertIncompatibleTracks(SampleTV_Num( anchor=[10,100] ))
        self._assertIncompatibleTracks(SampleTV( segments=[[1,2], [10,20]] ))
        self._assertIncompatibleTracks(SampleTV( ends=[10,20,30] ))

    def test_compute(self):
        self._assertCompute(1, SampleTV( starts=[0], anchor=[10,100] ))
        self._assertCompute(3, SampleTV( starts=[2,15,89], anchor=[10,100] ))
        
    def test_createChildren(self):
        self._assertCreateChildren([RawDataStatUnsplittable], SampleTV( starts=[0], anchor=[10,100] ))

class TestCountPointStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = CountPointStat

    def test_compute(self):
        self._assertCompute(1, SampleTV( starts=[0], anchor=[10,121] ))
        self._assertCompute(3, SampleTV( starts=[2,15,110], anchor=[10,121] ))
    
if __name__ == "__main__":
    unittest.main()
