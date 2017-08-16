import unittest
from quick.statistic.ThreeWayExpectedBpOverlapStat import ThreeWayExpectedBpOverlapStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestThreeWayExpectedBpOverlapStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = ThreeWayExpectedBpOverlapStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        #self._assertCompute(1, SampleTV( 2 ))
        answer = {'&&': 1/90.0, '*&': 0.1*0.2, '&*': 0.1*0.2, '**': 0.1*0.2}
        self._assertCompute(answer, \
                            SampleTV( segments=[[10,28]], anchor=[10,100] ), \
                            SampleTV( segments=[[27,36]], anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)


        exp = (108.0/180)*(99.0/180)
        answer = {'&&': 91/180.0, '*&':exp, '&*': exp, '**': exp}
        self._assertCompute(answer, \
                            SampleTV( segments=[[10,28], [90,180]], anchor=[10,190] ), \
                            SampleTV( segments=[[27,36], [90,180]], anchor=[10,190] ),\
                            assertFunc=self.assertListsOrDicts)
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([], SampleTV_Num( anchor= ))

    def runTest(self):
        pass
    
#class TestXSplittable(StatUnitTest):
#    CLASS_TO_CREATE = X
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestXSplittable().debug()
    #TestXUnsplittable().debug()
    unittest.main()
