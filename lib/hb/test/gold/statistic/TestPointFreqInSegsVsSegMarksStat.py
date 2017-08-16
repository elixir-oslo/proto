import unittest
from gold.statistic.PointFreqInSegsVsSegMarksStat import \
    PointFreqInSegsVsSegMarksStat, PointFreqInSegsVsSegMarksStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
import numpy
#from proto.RSetup import r

class TestPointFreqInSegsVsSegMarksStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = PointFreqInSegsVsSegMarksStat

    def setUp(self):
        from proto.RSetup import r
        r('sink(file("/dev/null", open="wt"), type="message")')
        StatUnitTest.setUp(self)

    def testDown(self):
        from proto.RSetup import r
        r('sink(type="message")')
        StatUnitTest.tearDown(self)
    
    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        PointFreqInSegsVsSegMarksStatUnsplittable.PRINT_RPY_OUTPUT = False
        PointFreqInSegsVsSegMarksStatUnsplittable.MIN_NUM_SEGS_FOR_TEST = 0

        # NB: Segments should have had equal lengths
        self._assertCompute({'AverageNumberOfPointsInSegments': 0.59999999999999998, 'Test statistic: ObservedTau': 0.92582009977255153, 'P-value': 0.052807511416113506, 'NumberOfSegments': 5},
                            SampleTV( starts=range(2,20,2) ),
                            SampleTV( segments=[[0,2], [3,4], [6,9], [14,15], [15,16]], vals=[False, False, True, True, False], valDType='bool8'),\
                            markType='tc')
        self._assertCompute({'AverageNumberOfPointsInSegments': 0.80000000000000004, 'Test statistic: ObservedTau': 0.72168783648703227, 'P-value': 0.1281465612656798, 'NumberOfSegments': 5},
                            SampleTV( starts=range(2,20,2) ),
                            SampleTV( segments=[[0,2], [3,5], [6,9], [14,15], [15,16]], vals=[False, False, True, True, False], valDType='bool8'),\
                            markType='tc')
        self._assertCompute({'AverageNumberOfPointsInSegments': 0.80000000000000004, 'Test statistic: ObservedTau': numpy.nan, 'P-value': numpy.nan, 'NumberOfSegments': 5},
                            SampleTV( starts=range(2,20,2) ),\
                            SampleTV( segments=[[0,2], [3,5], [6,9], [14,15], [15,16]], vals=[False, False, False, False, False], valDType='bool8'),\
                            markType='tc')
        self._assertCompute(None, SampleTV( starts=[] ),\
                            SampleTV( segments=[[0,2], [3,4], [6,9], [14,15], [15,16]], vals=[False, False, False, False, False], valDType='bool8' ),\
                            markType='tc')
        self._assertCompute(None, SampleTV( starts=range(2,20,2) ),\
                            SampleTV( segments=[], vals=[], valDType='bool8' ),\
                            markType='tc')
        self._assertCompute(None, SampleTV(starts=[] ),\
                            SampleTV( segments=[], vals=[], valDType='bool8' ),\
                            markType='tc')
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([], SampleTV_Num( anchor= ))

    def runTest(self):
        pass
    
#class TestPointFreqInSegsVsSegMarksStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = PointFreqInSegsVsSegMarksStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestPointFreqInSegsVsSegMarksStatSplittable().debug()
    #TestPointFreqInSegsVsSegMarksStatUnsplittable().debug()
    unittest.main()
