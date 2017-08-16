import unittest
import numpy
from gold.statistic.SumOfSquaresInsideStat import SumOfSquaresInsideStat
from gold.statistic.RawDataStat import RawDataStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestSumOfSquaresInsideStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = SumOfSquaresInsideStat

    def test_compute(self):
        self._assertCompute(0.0, SampleTV( segments=[], anchor=[0,0] ),
                            SampleTV_Num( vals=[], anchor=[0,0] ))
        self._assertCompute(numpy.nan, SampleTV( segments=[[0,2]], anchor=[0,2] ),
                            SampleTV_Num( vals=[1.0, numpy.nan], anchor=[0,2] ))
        self._assertCompute(0.0, SampleTV( segments=[], anchor=[0,100] ),
                            SampleTV_Num( vals=[1.0*x for x in range(100)], anchor=[0,100] ))
        self._assertCompute(13555.0, SampleTV( segments=[[3,5],[50,55]], anchor=[0,100] ),
                            SampleTV_Num( vals=[1.0*x for x in range(100)], anchor=[0,100] ))

    def runTest(self):
        pass
    
class TestSumOfSquaresInsideStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = SumOfSquaresInsideStat

    def test_compute(self):
        self._assertCompute(0.0, SampleTV( segments=[], anchor=[0,200] ),
                            SampleTV_Num( vals=[1.0*x for x in range(200)], anchor=[0,200] ))
        self._assertCompute(43557.0, SampleTV( segments=[[3,5],[50,55],[99,102]], anchor=[0,200] ),
                            SampleTV_Num( vals=[1.0*x for x in range(200)], anchor=[0,200] ))
        
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestSumInsideStatSplittable().debug()
    #TestSumInsideStatUnsplittable().debug()
    unittest.main()
