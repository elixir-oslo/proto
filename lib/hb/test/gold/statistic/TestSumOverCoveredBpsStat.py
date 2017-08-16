import unittest
from gold.statistic.SumOverCoveredBpsStat import SumOverCoveredBpsStat
from gold.statistic.RawDataStat import RawDataStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestSumOverCoveredBpsStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = SumOverCoveredBpsStat
    
    def test_compute(self):
        self._assertCompute(180, SampleTV_Num( vals=[2]*90, anchor=[10,100] ))
        self._assertCompute(60, SampleTV( segments=[[10,20], [80,85]], vals=[1,10], anchor=[10,100] ))
        self._assertCompute(111,  SampleTV( starts=[2,15,60], vals=[1,10,100], anchor=[10,100] ))
        self._assertCompute(765, SampleTV( ends=[15,90], vals=[1,10], anchor=[10,100] ))
        self._assertCompute(0, SampleTV( segments=[], vals=[], anchor=[10,100] ))
        
    def test_createChildren(self):
        self._assertCreateChildren([RawDataStatUnsplittable], SampleTV_Num( anchor=[0,100] ))

class TestSumOverCoveredBpsStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = SumOverCoveredBpsStat

    def test_compute(self):
        self._assertCompute(200, SampleTV_Num( vals=[2]*100, anchor=[10,110] ))
        self._assertCompute(210, SampleTV( segments=[[10,20], [80,100]], vals=[1,10], anchor=[10,110] ))
        self._assertCompute(111,  SampleTV( starts=[2,15,99], vals=[1,10,100], anchor=[10,110] ))
        self._assertCompute(865, SampleTV( ends=[15,100], vals=[1,10], anchor=[10,110] ))
        self._assertCompute(0, SampleTV( segments=[], vals=[], anchor=[10,110] ))
        
if __name__ == "__main__":
    unittest.main()
