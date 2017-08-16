import unittest
from quick.statistic.MarksSortedBySegmentOverlapStat import MarksSortedBySegmentOverlapStat
from gold.statistic.RawDataStat import RawDataStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestMarksSortedBySegmentOverlapStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = MarksSortedBySegmentOverlapStat

    def testIncompatibleTracks(self):
        pass
        #self._assertIncompatibleTracks(SampleTV( 1 ))

    def test_compute(self):
        self._assertCompute(([3,2,1],[0.8,0.6,0.5]), \
                            SampleTV(segments = [[10,20],[30,40],[50,55]], vals = [1,2,3], valDType='int32'),\
                            SampleTV(segments = [[15,25],[34,40],[51,55]]), markReq='number (integer)', \
                            assertFunc=self.assertListsOrDicts) 
        self._assertCompute(([],[]), \
                            SampleTV(numElements = 0, vals=[], valDType='int32'),\
                            SampleTV(segments = [[15,25],[34,40],[51,55]]), markReq='number (integer)', \
                            assertFunc=self.assertListsOrDicts) 
        
    def test_createChildren(self):  
        self._assertCreateChildren([RawDataStatUnsplittable]*2, \
                                    SampleTV( numElements=5 ), SampleTV( numElements=5  ))

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
