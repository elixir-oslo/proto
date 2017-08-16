#import unittest
#from quick.statistic.AggregateOfCoveredBpsInSegmentsStat import AggregateOfCoveredBpsInSegmentsStat
#
#from test.gold.statistic.StatUnitTest import StatUnitTest
#from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
#
#class TestMeanOfCoveredBpsInSegmentsStatUnsplittable(StatUnitTest):
#    CLASS_TO_CREATE = AggregateOfCoveredBpsInSegmentsStat
#    
#    def test_compute(self):
#        self._assertCompute(2, SampleTV_Num( vals=[2]*90, anchor=[10,100] ), \
#                            SampleTV( segments=[[0,10]], anchor=[10,100] ), method='mean_of_mean')
#        self._assertCompute(5.5, SampleTV( segments=[[10,20], [80,85]], vals=[1,10], anchor=[10,100] ), \
#                            SampleTV( segments=[[10,20], [80,85]], anchor=[10,100] ), method='mean_of_mean' )
#        #self._assertCompute(6,  SampleTV( starts=[2,15,60], vals=[2,10,100], anchor=[10,100] ), \
#        #                    SampleTV( segments=[[10,20], [80,90]], anchor=[10,100] ), method='mean_of_mean' )
#        #self._assertCompute(8, SampleTV( ends=[15,90], vals=[2,10], anchor=[10,100] ), \
#        #                    SampleTV( segments=[[10,20], [40,50]], anchor=[10,100] ), method='mean_of_mean' )
#        self._assertCompute(0, SampleTV( segments=[], vals=[], anchor=[10,100] ), \
#                            SampleTV( segments=[], anchor=[10,100] ), method='mean_of_mean' )
#        
#    #def test_createChildren(self):
#    #    self._assertCreateChildren([RawDataStatUnsplittable, RawDataStatUnsplittable], SampleTV_Num( anchor=[0,100] ), SampleTV(segments=[],  anchor=[0,100] ))
#
##class TestSumOfCoveredBpsInSegmentsStatUnsplittable(StatUnitTest):
##    CLASS_TO_CREATE = SumOverCoveredBpsStat
##
##    def test_compute(self):
##        self._assertCompute(200, SampleTV_Num( vals=[2]*100, anchor=[10,110] ))
##        self._assertCompute(210, SampleTV( segments=[[10,20], [80,100]], vals=[1,10], anchor=[10,110] ))
##        self._assertCompute(111,  SampleTV( starts=[2,15,99], vals=[1,10,100], anchor=[10,110] ))
##        self._assertCompute(865, SampleTV( ends=[15,100], vals=[1,10], anchor=[10,110] ))
##        self._assertCompute(0, SampleTV( segments=[], anchor=[10,110] ))
#        
#if __name__ == "__main__":
#    unittest.main()
