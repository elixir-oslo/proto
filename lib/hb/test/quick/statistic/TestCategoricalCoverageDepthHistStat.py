import unittest
from quick.statistic.CategoricalCoverageDepthHistStat import CategoricalCoverageDepthHistStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestCategoricalCoverageDepthHistStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = CategoricalCoverageDepthHistStat

    def testIncompatibleTracks(self):
        self._assertIncompatibleTracks(SampleTV( starts=[0,3,5], anchor=[10,20] ))
        self._assertIncompatibleTracks(SampleTV( ends=[0,3,5,10], anchor=[10,20] ))
        self._assertIncompatibleTracks(SampleTV( segments=[[3,5], [7,9]], anchor=[10,20] ))

    def test_compute(self):
        self._assertCompute([10], \
                            SampleTV( segments=[], vals=[], anchor=[10,20], valDType='S2', allowOverlaps=True ))
        self._assertCompute([4,4,2], \
                            SampleTV( segments=[[3,7], [5,9]], vals=['AA','BB'], anchor=[10,20], valDType='S', allowOverlaps=True ))
        self._assertCompute([4,4,1,1], \
                            SampleTV( segments=[[3,7], [6,7], [5,9]], vals=['AA','BB','CC'], anchor=[10,20], valDType='S', allowOverlaps=True ))

    #def test_createChildren(self):
    #    self._assertCreateChildren([YStat], SampleTV( data2 ))

    def runTest(self):
        pass

#class TestCategoricalCoverageDepthHistStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = CategoricalCoverageDepthHistStat
#
#    def test_compute(self):
#        pass
#
#    def test_createChildren(self):
#        pass

    #def runTest(self):
    #    pass

if __name__ == "__main__":
    #TestCategoricalCoverageDepthHistStatSplittable().debug()
    #TestCategoricalCoverageDepthHistStatUnsplittable().debug()
    unittest.main()
