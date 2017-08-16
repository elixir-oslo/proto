import unittest
from gold.statistic.GenericNodeValueStat import GenericNodeValueStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
from gold.statistic.GenericNodeValueStat import GenericNodeValueStat

class TestGenericNodeValueStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = GenericNodeValueStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    #def test_compute(self):
    #    self._assertCompute(1, SampleTV(  ))
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([], SampleTV_Num( anchor= ))

    def runTest(self):
        pass
    
#class TestXSplittable(StatUnitTest):
#    CLASS_TO_CREATE = X
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestXSplittable().debug()
    #TestXSplittableUnsplittable().debug()
    unittest.main()
