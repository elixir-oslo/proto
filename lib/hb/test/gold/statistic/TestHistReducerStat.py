import unittest
from gold.statistic.HistReducerStat import HistReducerStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestHistReducerStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = HistReducerStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV( 1 ))

    def test_compute(self):
        self._assertCompute(range(4), SampleTV_Num( vals=range(10,30) ), \
                            numDiscreteVals=4, reducedNumDiscreteVals=4, assertFunc=self.assertListsOrDicts)


    #def test_createChildren(self):
    #    self._assertCreateChildren([4], SampleTV_Num( anchor=5 ))

    def runTest(self):
        pass
    
#class TestHistReducerStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = HistReducerStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestHistReducerStatSplittable().debug()
    #TestHistReducerStatUnsplittable().debug()
    unittest.main()
