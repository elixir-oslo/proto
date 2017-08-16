import unittest
from gold.statistic.XyzStat import XyzStat
# from quick.statistic.XyzStat import XyzStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num


class TestXyzStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = XyzStat

    # def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        self._assertCompute(someResult, SampleTV( someData ))
        
    # def test_createChildren(self):
    #    self._assertCreateChildren([XyzStat], SampleTV( someOtherData ))

    def runTest(self):
        pass


# class TestXyzStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = XyzStat
#
#    def test_compute(self):
#        pass
#
#    def test_createChildren(self):
#        pass
#
#     def runTest(self):
#        pass


if __name__ == "__main__":
    #TestXyzStatSplittable().debug()
    #TestXyzStatUnsplittable().debug()
    unittest.main()
