import unittest
import numpy
from quick.statistic.CorrCoefStat import CorrCoefStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestCorrCoefStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = CorrCoefStat

    #def testIncompatibleTracks(self):
        #self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        self._assertCompute(-1.0, SampleTV_Num( vals=[1.0,2.0] ), SampleTV_Num( vals=[2.0,1.0] ))
        self._assertCompute(1.0, SampleTV_Num( vals=[1.0,2.0] ), SampleTV_Num( vals=[2.0,4.0] ))
        self._assertCompute(numpy.nan, SampleTV_Num( vals=[1.0,2.0] ), SampleTV_Num( vals=[2.0,2.0] ))
        
        self._assertCompute(None, SampleTV_Num( vals=[] ), SampleTV_Num( vals=[] ))
        self._assertCompute(numpy.nan, SampleTV_Num( vals=[1.0,numpy.nan] ), SampleTV_Num( vals=[2.0,3.0] ))
        
    #def test_createChildren(self):
        #self._assertCreateChildren([], SampleTV_Num( anchor= ))

    def runTest(self):
        pass
    
#class TestCorrCoefStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = CorrCoefStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestCorrCoefStatSplittable().debug()
    #TestCorrCoefStatUnsplittable().debug()
    unittest.main()
