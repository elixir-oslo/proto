import unittest
from quick.statistic.MarksSortedByFunctionValueStat import MarksSortedByFunctionValueStat
from gold.statistic.RawDataStat import RawDataStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestMarksSortedByFunctionValueStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = MarksSortedByFunctionValueStat

    def testIncompatibleTracks(self):
        pass
        #self._assertIncompatibleTracks(SampleTV( 1 ))

    def test_compute(self):
        self._assertCompute(([3,2,1], [52.0, 34.5, 14.5]), \
                            SampleTV( segments = [[10,20],[30,40],[50,55]], vals = [1,2,3], anchor = [0,100], valDType='int32'),\
                            SampleTV_Num( vals = range(100), anchor = [0,100] ), markReq='number (integer)',\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute(([],[]), \
                            SampleTV( numElements = 0, vals = [], anchor = [0,100], valDType='int32'),\
                            SampleTV_Num( vals = range(100),anchor = [0,100]), markReq='number (integer)',\
                            assertFunc=self.assertListsOrDicts)
        
    def test_createChildren(self):  
        self._assertCreateChildren([RawDataStatUnsplittable]*2, \
                                    SampleTV( numElements=5 ), SampleTV_Num( anchor = [10,1000]  ))

    def runTest(self):
        pass
    
#class TestMarksSortedBySegmentOverlapStatStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = MarksSortedBySegmentOverlapStatStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestMarksSortedBySegmentOverlapStatStatSplittable().debug()
    #TestMarksSortedBySegmentOverlapStatStatUnsplittable().debug()
    unittest.main()
