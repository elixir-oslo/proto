import unittest
from gold.statistic.DiscreteMarksHistStat import DiscreteMarksHistStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestDiscreteMarksHistStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = DiscreteMarksHistStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV( 1 ))

    def test_compute(self):
        self._assertCompute([5,5,5,5], SampleTV_Num( vals=range(10,30) ), \
                            numDiscreteVals=4, marksStat='MarksListStat', assertFunc=self.assertListsOrDicts)
        
        self._assertCompute([3,2,2,3], SampleTV_Num( vals=range(10,20) ), \
                            numDiscreteVals=4, marksStat='MarksListStat', assertFunc=self.assertListsOrDicts)
        
        self._assertCompute([1,0,0,1], SampleTV_Num( vals=range(10,12) ), \
                            numDiscreteVals=4, marksStat='MarksListStat', assertFunc=self.assertListsOrDicts)
        
        self._assertCompute([1,1,1,1], SampleTV_Num( vals=range(10,30), anchor=[0,20]), SampleTV( starts=[0,5,10,15], anchor=[0,20]),\
                            numDiscreteVals=4, marksStat='ExtractMarksStat', assertFunc=self.assertListsOrDicts)
        
        self._assertCompute([5,3,0,0], SampleTV_Num( vals=range(10,30), anchor=[0,20]), SampleTV( starts=range(0,8), anchor=[0,20]),\
                            numDiscreteVals=4, marksStat='ExtractMarksStat', assertFunc=self.assertListsOrDicts)
        
        self._assertCompute([0,0,3,5], SampleTV_Num( vals=range(10,30), anchor=[0,20]), SampleTV( starts=range(12,20), anchor=[0,20]),\
                            numDiscreteVals=4, marksStat='ExtractMarksStat', assertFunc=self.assertListsOrDicts)
        
        self._assertCompute([0,0,0,0], SampleTV_Num( vals=range(10,30), anchor=[0,20]), SampleTV( starts=[], anchor=[0,20]),\
                            numDiscreteVals=4, marksStat='ExtractMarksStat', assertFunc=self.assertListsOrDicts)
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([4], SampleTV_Num( anchor=5 ))

    def runTest(self):
        pass
    
#class TestDiscreteMarksHistStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = DiscreteMarksHistStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestDiscreteMarksHistStatSplittable().debug()
    #TestDiscreteMarksHistStatUnsplittable().debug()
    unittest.main()
