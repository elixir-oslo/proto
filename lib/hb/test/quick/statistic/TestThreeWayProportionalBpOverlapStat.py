import unittest
from quick.statistic.ThreeWayProportionalBpOverlapStat import ThreeWayProportionalBpOverlapStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestThreeWayProportionalBpOverlapStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = ThreeWayProportionalBpOverlapStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        #self._assertCompute(1, SampleTV( 2 ))
        answer = {'11': 1/90.0, '10': 18/90.0, '01': 9/90.0}
        self._assertCompute(answer, \
                            SampleTV( segments=[[10,28]], anchor=[10,100] ), \
                            SampleTV( segments=[[27,36]], anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)

        answer = {'11': 91/180.0, '10': 108/180.0, '01': 99/180.0}
        self._assertCompute(answer, \
                            SampleTV( segments=[[10,28], [90,180]], anchor=[10,190] ), \
                            SampleTV( segments=[[27,36], [90,180]], anchor=[10,190] ),\
                            assertFunc=self.assertListsOrDicts)
        #
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
