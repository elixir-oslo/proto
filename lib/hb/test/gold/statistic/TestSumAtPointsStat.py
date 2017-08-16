import unittest
from gold.statistic.SumAtPointsStat import SumAtPointsStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestSumAtPointsStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = SumAtPointsStat

    def test_compute(self):
        self._assertCompute(0.0, SampleTV( starts=[], anchor=[0,0] ),
                            SampleTV_Num( vals=[], anchor=[0,0] ))
        self._assertCompute(0.0, SampleTV( starts=[], anchor=[0,100] ),
                            SampleTV_Num( vals=[1.0*x for x in range(100)], anchor=[0,100] ))
        self._assertCompute(128.0, SampleTV( starts=[3,5,50,70], anchor=[0,100] ),
                            SampleTV_Num( vals=[1.0*x for x in range(100)], anchor=[0,100] ))

    def runTest(self):
        pass
        
if __name__ == "__main__":
    unittest.main()
