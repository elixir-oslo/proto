import unittest
from gold.statistic.PointCountInSegsPvalStat import PointCountInSegsPvalStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestPointCountInSegsPvalStatUnsplittable(StatUnitTest):
    #THROW_EXCEPTION = False
    CLASS_TO_CREATE = PointCountInSegsPvalStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV( 1 ))

    def test_compute(self):
        self._assertCompute(None, SampleTV( starts=[] ), SampleTV( segments=[] ))
        self._assertCompute(None, SampleTV( starts=[15, 40, 45, 60, 70] ), SampleTV( segments=[] ))
        self._assertCompute(None, SampleTV( starts=[] ), SampleTV( segments=[[15,40], [50,75]] ))
        self._assertCompute({'DiffFromExpected': -0.5, 'P-value': 0.5, 'SegCoverage': 0.5, 'E(Test statistic): ExpPointsInside': 2.5, 'Test statistic: PointsInside': 2, 'PointsTotal': 5},\
                             SampleTV( starts=[15, 40, 45, 60, 80], anchor=[0,100] ), \
                             SampleTV( segments=[[15,40], [50,75]], anchor=[0,100] ), tail='less',\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({'DiffFromExpected': 0.5, 'P-value': 0.5, 'SegCoverage': 0.5, 'E(Test statistic): ExpPointsInside': 2.5, 'Test statistic: PointsInside': 3, 'PointsTotal': 5},\
                             SampleTV( starts=[15, 40, 45, 60, 70], anchor=[0,100] ), \
                             SampleTV( segments=[[15,40], [50,75]], anchor=[0,100] ), tail='more',\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({'DiffFromExpected': -0.5, 'P-value': 1.0, 'SegCoverage': 0.5, 'E(Test statistic): ExpPointsInside': 2.5, 'Test statistic: PointsInside': 2, 'PointsTotal': 5},\
                             SampleTV( starts=[15, 40, 45, 60, 80], anchor=[0,100] ), \
                             SampleTV( segments=[[15,40], [50,75]], anchor=[0,100] ), tail='different',\
                            assertFunc=self.assertListsOrDicts)
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([], SampleTV_Num( anchor=[]  ))

    def runTest(self):
        self.test_compute()
    
#class TestPointCountInSegsPvalStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = PointCountInSegsPvalStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    ##def runTest(self):
        #pass
    
if __name__ == "__main__":
    #TestPointCountInSegsPvalStatSplittable().run()
    #TestPointCountInSegsPvalStatUnsplittable().run()
    unittest.main()
