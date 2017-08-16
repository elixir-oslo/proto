import unittest
from gold.statistic.SimpleDiscreteMarksIntensityStat import SimpleDiscreteMarksIntensityStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestSimpleDiscreteMarksIntensityStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = SimpleDiscreteMarksIntensityStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV( 1 ))

    def test_compute(self):
        self._assertCompute([0.2,0.2,0.2,0.2], SampleTV_Num( vals=range(10,30), anchor=[0,20] ), SampleTV( starts=[0,5,10,15], anchor=[0,20] ),\
                            numDiscreteVals=4, assertFunc=self.assertListsOrDicts)
        
        self._assertCompute([ 0.875, 0.475, 0.075, 0.075], SampleTV_Num( vals=range(10,26), anchor=[0,16] ), SampleTV( starts=range(0,6), anchor=[0,16] ),\
                            numDiscreteVals=4, assertFunc=self.assertListsOrDicts)

        self._assertCompute([0,0,0,0], SampleTV_Num( vals=range(10,30), anchor=[0,20] ), SampleTV( starts=[], anchor=[0,20] ),\
                            numDiscreteVals=4, assertFunc=self.assertListsOrDicts)
        
    #def test_createChildren(self):
        #self._assertCreateChildren([4], SampleTV_Num( anchor=5 ))

    def runTest(self):
        pass
    
#class TestSimpleDiscreteMarksIntensityStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = SimpleDiscreteMarksIntensityStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestDiscreteMarksIntensityStatSplittable().debug()
    #TestDiscreteMarksIntensityStatUnsplittable().debug()
    unittest.main()
