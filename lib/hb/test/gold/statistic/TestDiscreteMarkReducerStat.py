import unittest
from gold.statistic.DiscreteMarkReducerStat import DiscreteMarkReducerStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestDiscreteMarkReducerStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = DiscreteMarkReducerStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        self._assertCompute([0]*5 + [1]*5 + [2]*5 + [3]*5, SampleTV_Num( vals=range(10,30) ), \
            numDiscreteVals=4, reducedNumDiscreteVals=4, marksStat='MarksListStat', assertFunc=self.assertListsOrDicts)
        
        self._assertCompute([0]*3 + [1]*2 + [2]*2 + [3]*3, SampleTV_Num( vals=range(10,20) ), \
            numDiscreteVals=4, reducedNumDiscreteVals=4, marksStat='MarksListStat', assertFunc=self.assertListsOrDicts)
        
        self._assertCompute([0, 3], SampleTV_Num( vals=range(10,12) ), \
            numDiscreteVals=4, reducedNumDiscreteVals=4, marksStat='MarksListStat', assertFunc=self.assertListsOrDicts)
        
        self._assertCompute([], SampleTV_Num( vals=range(10,12), anchor=[0,2]), SampleTV( starts=[], anchor=[0,2]),\
            numDiscreteVals=4, reducedNumDiscreteVals=4, marksStat='ExtractMarksStat', assertFunc=self.assertListsOrDicts)
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([], SampleTV_Num( anchor= ))

    def runTest(self):
        pass
    
#class TestDiscreteMarkReducerStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = DiscreteMarkReducerStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestDiscreteMarkReducerStatSplittable().debug()
    #TestDiscreteMarkReducerStatUnsplittable().debug()
    unittest.main()
