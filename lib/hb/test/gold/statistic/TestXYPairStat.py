import unittest
from gold.statistic.XYPairStat import XYPairStat
from gold.statistic.CountStat import CountStat, CountStatSplittable, CountStatUnsplittable
from gold.statistic.SumStat import SumStat, SumStatSplittable, SumStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
from test.util.Asserts import AssertList

class TestXYPairStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = XYPairStat
    
    def _assertList(self, target, other):
        AssertList(target, other, self.assertEqual)
    
    def test_compute(self):
        self._assertCompute([3, 10.0],\
                             SampleTV( segments=[[0,1],[2,4]], anchor=[10,15] ),\
                             SampleTV_Num( vals=[1.0, 1.5, 2.0, 2.5, 3.0], anchor=[10,15] ),\
                             CountStat, SumStat, assertFunc=self._assertList)
        
    def test_createChildren(self):
        self._assertCreateChildren([CountStatUnsplittable, SumStatUnsplittable],\
                                    SampleTV( anchor=[10,100], numElements=5 ),\
                                    SampleTV_Num( anchor=[10,100] ), CountStat, SumStat)
        self._assertCreateChildren([CountStatSplittable, SumStatSplittable],\
                                    SampleTV( anchor=[10,121], numElements=5 ),\
                                    SampleTV_Num( anchor=[10,121] ), CountStat, SumStat)
    
if __name__ == "__main__":
    unittest.main()
