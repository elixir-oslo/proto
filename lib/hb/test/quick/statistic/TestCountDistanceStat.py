import unittest
from quick.statistic.CountDistanceStat import CountDistanceStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestCountDistanceStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = CountDistanceStat
    
    def test_compute(self):
        self._assertCompute([1],  SampleTV( starts=[15], anchor=[10,100]), maxNum=1500)
        self._assertCompute([3],  SampleTV( starts=[1,15,60], anchor=[10,100]), maxNum=1500)
        self._assertCompute([3, 1, 2, 1, 2],  SampleTV( starts=[5,8,11,20, 29, 32, 45, 58, 60], anchor=[0,90]), maxNum=5)
        self._assertCompute([], SampleTV( starts=[], anchor=[10,100] ))
        

class TestCountDistanceStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = CountDistanceStat

    def test_compute(self):
        self._assertCompute([2, 1],  SampleTV( starts=[11,15,160], anchor=[10,200]), maxNum=1500)
      
if __name__ == "__main__":
    unittest.main()
