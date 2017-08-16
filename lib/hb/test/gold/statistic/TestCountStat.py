import unittest
from gold.statistic.CountStat import CountStat
from gold.statistic.RawDataStat import RawDataStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestCountStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = CountStat
    
    def test_compute(self):
        self._assertCompute(90, SampleTV_Num( anchor=[10,100] ))
        self._assertCompute(20, SampleTV( segments=[[10,20], [80,90]], anchor=[10,100] ))
        self._assertCompute(3,  SampleTV( starts=[2,15,60], anchor=[10,100] ))
        self._assertCompute(90, SampleTV( ends=[15,90], anchor=[10,100] ))
        self._assertCompute(0, SampleTV( segments=[], anchor=[10,100] ))
        
    def test_createChildren(self):
        self._assertCreateChildren([RawDataStatUnsplittable], SampleTV_Num( anchor=[0,100] ))

class TestCountStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = CountStat

    def test_compute(self):
        self._assertCompute(111, SampleTV_Num( anchor=[10,121] ))
        self._assertCompute(41,  SampleTV( segments=[[10,20], [80,111]], anchor=[10,121] ))
        self._assertCompute(3,   SampleTV( starts=[2,15,110], anchor=[10,121] ))
        self._assertCompute(111, SampleTV( ends=[15,111], anchor=[10,121] ))
        self._assertCompute(0, SampleTV( segments=[], anchor=[10,121] ))
        
if __name__ == "__main__":
    unittest.main()
