import unittest
from gold.statistic.MeanValAtPointsStat import MeanValAtPointsStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestMeanValAtPointsStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = MeanValAtPointsStat

    def test_compute(self):
        self._assertCompute(None, SampleTV( starts=[], anchor=[0,0] ),
                            SampleTV_Num( vals=[], anchor=[0,0] ))
        self._assertCompute(None, SampleTV( starts=[], anchor=[0,100] ),
                            SampleTV_Num( vals=[1.0*x for x in range(100)], anchor=[0,100] ))
        self._assertCompute(32.0, SampleTV( starts=[3,5,50,70], anchor=[0,100] ),
                            SampleTV_Num( vals=[1.0*x for x in range(100)], anchor=[0,100] ))

    def runTest(self):
        pass
        
if __name__ == "__main__":
    unittest.main()
