import unittest
from quick.statistic.SmoothedPointMarksStat import SmoothedPointMarksStat
from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestSmoothedPointMarksStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = SmoothedPointMarksStat

    def testIncompatibleTracks(self):
        pass
        #self._assertIncompatibleTracks(SampleTV( 1 ))

    def test_compute(self):
        self._assertCompute([1.119203,1.891642,2.989013], SampleTV( starts = [10,30,60], vals = [1,2,3], anchor = [0,100], valDType='int32'),\
                                     markReq='number' ,windowSize=3, windowBpSize=5000, sdOfGaussian=10,guaranteeBpCoverByWindow='False',assertFunc=self.assertListsOrDicts)
        #self._assertCompute([1.119203,1.891642,2.989013,1.119203,1.891642,2.989013], SampleTV( starts = [10,30,60,110,130,160], vals = [1,2,3,1,2,3], anchor = [0,200], valDType='int32'),\
        #                             markReq='number' ,windowSize=3, windowBpSize=5000, sdOfGaussian=10,guaranteeBpCoverByWindow='False',assertFunc=self.assertListsOrDicts)
        self._assertCompute([], SampleTV( starts=[], anchor = [0,100], valDType='int32'),\
                                     markReq='number' ) 
        
    #def test_createChildren(self):  
        #self._assertCreateChildren([RawDataStatUnsplittable]*2, \
        #                            SampleTV( numElements=5 ), SampleTV_Num( anchor = [10,1000]  ))

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
