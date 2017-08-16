import unittest
from quick.statistic.ConvertToNonOverlappingCategorySegmentsPythonStat import \
    ConvertToNonOverlappingCategorySegmentsPythonStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestConvertToNonOverlappingCategorySegmentsStatUnsplittable(StatUnitTest):
    #CLASS_TO_CREATE = ConvertToNonOverlappingCategorySegmentsStat
    CLASS_TO_CREATE = ConvertToNonOverlappingCategorySegmentsPythonStat
    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))
    
    def test_compute(self):
        self._assertCompute(SampleTV( segments=[[10,12], [12,20], [20,22]], vals=['a(1/1, 1)','a;b(1/2, 2)','b(1/1, 1)'], valDType='S11' ), \
                            SampleTV( segments=[[10,20], [12,22]], vals=['a','b'], valDType='S10'))
        self._assertCompute(SampleTV( segments=[[10,16], [16,18], [18,20], [20,22]], vals=['a;b(1/2, 2)','a(2/3, 2)','a(2/2, 1)','a(1/1, 1)'], valDType='S11' ), \
                            SampleTV( segments=[[10,20], [10,18], [16,22]], vals=['a','b','a'], valDType='S10' ))
        
        self._assertCompute(SampleTV( segments=[[5,10], [10,12], [12,15], [15,30]], vals=['a(1/1, 1)','a;b(1/2, 2)','a(2/3, 2)','a(1/1, 1)'], valDType='S11' ), \
                            SampleTV( segments=[[5,30], [10,15], [12,15]], vals=['a','b','a'], valDType='S10' ))
        self._assertCompute(SampleTV( segments=[[5,15], [15,20], [20,25], [25,30]], vals=['a(1/1, 1)','a(2/3, 2)','a(2/2, 1)','a(1/1, 1)'], valDType='S11' ), \
                            SampleTV( segments=[[5,30], [15,20], [15,25]], vals=['a','b','a'], valDType='S10' ))
        self._assertCompute(SampleTV( segments=[[5,10], [10,12], [12,15], [15,20], [20,23], [23,30]], vals=['a(1/1, 1)','a;b(1/2, 2)','b(2/3, 2)','a(2/3, 2)','a;c(1/2, 2)','a(1/1, 1)'], valDType='S11' ), \
                            SampleTV( segments=[[5,30], [10,15], [12,15], [15,20], [15,23]], vals=['a','b','b','a','c'], valDType='S10' ))
    
        self._assertCompute(SampleTV( segments=[[10,20]], vals=['a(1/1, 1)'], valDType='S11' ), SampleTV( segments=[[10,20]], vals=['a'], valDType='S10' ))
        self._assertCompute(SampleTV( segments=[], vals=[], valDType='S10' ), SampleTV( segments=[], vals=[], valDType='S10' ))
    
    #def test_createChildren(self):
    #    self._assertCreateChildren([], SampleTV_Num( anchor= ))

    def runTest(self):
        pass
    
#class TestConvertToNonOverlappingCategorySegmentsStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = ConvertToNonOverlappingCategorySegmentsStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestConvertToNonOverlappingCategorySegmentsStatSplittable().debug()
    #TestConvertToNonOverlappingCategorySegmentsStatUnsplittable().debug()
    unittest.main()
