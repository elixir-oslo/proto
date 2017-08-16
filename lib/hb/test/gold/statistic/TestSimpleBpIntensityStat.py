import unittest
from gold.statistic.SimpleBpIntensityStat import SimpleBpIntensityStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestSimpleBpIntensityStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = SimpleBpIntensityStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV( 1 ))

    def test_compute(self):
        self._assertCompute([0.2]*20, SampleTV_Num( vals=range(10,30), anchor=[0,20] ), SampleTV( starts=[0,5,10,15], anchor=[0,20] ),\
                            numDiscreteVals=4, assertFunc=self.assertListsOrDicts)
        
        self._assertCompute([0.875]*4+[0.475]*4+[0.075]*8, SampleTV_Num( vals=range(10,26), anchor=[0,16] ), SampleTV( starts=range(0,6), anchor=[0,16] ),\
                            numDiscreteVals=4, assertFunc=self.assertListsOrDicts)

        self._assertCompute([0]*20, SampleTV_Num( vals=range(10,30), anchor=[0,20] ), SampleTV( starts=[], anchor=[0,20] ),\
                            numDiscreteVals=4, assertFunc=self.assertListsOrDicts)
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([4], SampleTV_Num( anchor=5 ))

    def runTest(self):
        pass
    
#class TestSimpleBpIntensityStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = SimpleBpIntensityStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestBpIntensityStatSplittable().debug()
    #TestBpIntensityStatUnsplittable().debug()
    unittest.main()
