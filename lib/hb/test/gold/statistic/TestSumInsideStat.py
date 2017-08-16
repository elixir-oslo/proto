import unittest
from gold.statistic.SumInsideStat import SumInsideStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestSumInsideStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = SumInsideStat

    def test_compute(self):
        self._assertCompute(0.0, SampleTV( segments=[], anchor=[0,0] ),
                            SampleTV_Num( vals=[], anchor=[0,0] ))
        self._assertCompute(0.0, SampleTV( segments=[], anchor=[0,100] ),
                            SampleTV_Num( vals=[1.0*x for x in range(100)], anchor=[0,100] ))
        self._assertCompute(1197.0, SampleTV( segments=[[3,5],[50,70]], anchor=[0,100] ),
                            SampleTV_Num( vals=[1.0*x for x in range(100)], anchor=[0,100] ))
        #self._assertCompute(0.0, SampleTV_Num( vals=[], anchor=[0,0] ), SampleTV( segments=[], anchor=[0,0] ))
        #self._assertCompute(0.0, SampleTV_Num( vals=[1.0*x for x in range(100)], anchor=[0,100] ), SampleTV( segments=[], anchor=[0,100] ))
        #self._assertCompute(1197.0, SampleTV_Num( vals=[1.0*x for x in range(100)], anchor=[0,100] ), SampleTV( segments=[[3,5],[50,70]], anchor=[0,100] ))

    def runTest(self):
        pass
    
class TestSumInsideStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = SumInsideStat

    def test_compute(self):
        self._assertCompute(0.0, SampleTV( segments=[], anchor=[0,200] ),
                            SampleTV_Num( vals=[1.0*x for x in range(200)], anchor=[0,200] ))
        self._assertCompute(1497.0, SampleTV( segments=[[3,5],[50,70],[99,102]], anchor=[0,200] ),
                            SampleTV_Num( vals=[1.0*x for x in range(200)], anchor=[0,200] ))
        
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestSumInsideStatSplittable().debug()
    #TestSumInsideStatUnsplittable().debug()
    unittest.main()
