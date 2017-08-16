import unittest
from quick.statistic.ThreeWayFocusedTrackProportionCoveragesAtDepthsStat import \
    ThreeWayFocusedTrackProportionCoveragesAtDepthsStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestThreeWayFocusedTrackProportionCoveragesAtDepthsStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = ThreeWayFocusedTrackProportionCoveragesAtDepthsStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        #self._assertCompute(1, SampleTV( 2 ))
        #answer = {'11': 1, '10': 18, '01': 9}        
        #self._assertCompute(answer, \
        #                    SampleTV( segments=[[10,28]], anchor=[10,100] ), \
        #                    SampleTV( segments=[[27,36]], anchor=[10,100] ),\
        #                    assertFunc=self.assertListsOrDicts)

        #answer = {'Depth 0': 64, 'Depth 1': 25, 'Depth 2': 91,'BinSize':180}
        answer = {'Prop. cover by T1 where depth 0 by other tracks':17.0/81, 'Prop. cover by T1 where depth 1 by other tracks':91.0/99,\
                  'Prop. cover by T2 where depth 0 by other tracks':8.0/72, 'Prop. cover by T2 where depth 1 by other tracks':91.0/108, 'BinSize':180}
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
