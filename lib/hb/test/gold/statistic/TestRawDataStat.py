import unittest
from gold.track.TrackFormat import TrackFormatReq
from gold.statistic.RawDataStat import RawDataStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
from test.util.Asserts import AssertList

class TestRawDataStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = RawDataStat

    def testIncompatibleTracks(self):
        self._assertIncompatibleTracks(SampleTV( numElements=5 ), TrackFormatReq(dense=True))

    def _assertTVEqual(self, target, other):
        self.assertEqual(target.genomeAnchor, other.genomeAnchor)
        self.assertEqual(target.trackFormat, other.trackFormat)
        AssertList([el.start() for el in target],
                   [el.start() for el in other], self.assertEqual)
        AssertList([el.end() for el in target],
                   [el.end() for el in other], self.assertEqual)
        AssertList([el.val() for el in target],
                   [el.val() for el in other], self.assertAlmostEqual)
        AssertList([el.strand() for el in target],
                   [el.strand() for el in other], self.assertEqual)

    def test_compute(self):
        sampleTV = SampleTV( numElements=5 )
        self._assertCompute(sampleTV,
                            sampleTV, TrackFormatReq(), assertFunc=self._assertTVEqual)

    def test_createChildren(self):
        self._assertCreateChildren([],
                                   SampleTV_Num( anchor=[10,100] ), TrackFormatReq())

    def runTest(self):
        self.test_compute()

if __name__ == "__main__":
    #TestRawDataStatUnsplittable().debug()
    unittest.main()
