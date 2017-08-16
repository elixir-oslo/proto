import unittest
from gold.statistic.PointPositioningPValStat import PointPositioningPValStat, \
    PointPositioningPValStatUnsplittable
from gold.statistic.PointPositionsInSegsStat import PointPositionsInSegsStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestPointPositioningPValStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = PointPositioningPValStat

    def testIncompatibleTracks(self):
        self._assertIncompatibleTracks(SampleTV( numElements=5 ), SampleTV( numElements=5 ), tail='ha1', assumptions='independentPoints')
        self._assertIncompatibleTracks(SampleTV( starts=[0,5] ), SampleTV( starts=[0,5] ), tail='ha1', assumptions='independentPoints')
        self._assertIncompatibleTracks(SampleTV( ends=[0,5] ), SampleTV( ends=[0,5] ), tail='ha1', assumptions='independentPoints')
        self._assertIncompatibleTracks(SampleTV_Num( anchor=[5,10] ), SampleTV_Num( anchor=[5,10] ), tail='ha1', assumptions='independentPoints')

    def test_compute(self):
        self._assertCompute({'P-value': None, 'Test statistic: W12': 0, 'N': 0, 'Distribution': 'N/A', 'altHyp': 'ha1'}, \
                            SampleTV( starts=[] ), \
                            SampleTV( segments=[] ), \
                            tail='ha1', assumptions='independentPoints')
        self._assertCompute({'P-value': None, 'Test statistic: W12': 0, 'N': 0, 'Distribution': 'N/A', 'altHyp': 'ha1'}, \
                            SampleTV( starts=[1,2,3] ), \
                            SampleTV( segments=[] ), \
                            tail='ha1', assumptions='independentPoints')
        self._assertCompute({'P-value': None, 'Test statistic: W12': 0, 'N': 0, 'Distribution': 'N/A', 'altHyp': 'ha1'}, \
                            SampleTV( starts=[] ), \
                            SampleTV( segments=[[10,20]] ), \
                            tail='ha1', assumptions='independentPoints')
        self._assertCompute({'P-value': 0.5, 'Test statistic: W12': 232.5, 'N': 30, 'Distribution': 'Normal approximation', 'altHyp': 'ha1'},
                            SampleTV( starts=range(10,41), strands=False), \
                            SampleTV( segments=[[0,101]], strands=False), \
                            tail='ha1', assumptions='independentPoints')
        self._assertCompute({'P-value': 0.5, 'Test statistic: W34': 410, 'N': 40, 'Distribution': 'Normal approximation', 'altHyp': 'ha3'},
                            SampleTV( anchor=[0,101], starts=range(30,71), strands=False), \
                            SampleTV( anchor=[0,101], ends=[0,101], strands=False), \
                            tail='ha3', assumptions='independentPoints')
        
    def test_calcScore(self):
        self.assertEqual(-1, PointPositioningPValStatUnsplittable._calcScore(0.0, 'ha1'))
        self.assertEqual(0, PointPositioningPValStatUnsplittable._calcScore(0.25, 'ha1'))
        self.assertEqual(1, PointPositioningPValStatUnsplittable._calcScore(0.5, 'ha1'))
        self.assertEqual(-1, PointPositioningPValStatUnsplittable._calcScore(1.0, 'ha1'))

        self.assertEqual(-1, PointPositioningPValStatUnsplittable._calcScore(0.0, 'ha3'))
        self.assertEqual(-0.5, PointPositioningPValStatUnsplittable._calcScore(0.25, 'ha3'))
        self.assertEqual(0, PointPositioningPValStatUnsplittable._calcScore(0.5, 'ha3'))
        self.assertEqual(1, PointPositioningPValStatUnsplittable._calcScore(1.0, 'ha3'))
        
    def test_createChildren(self):
        self._assertCreateChildren([PointPositionsInSegsStatUnsplittable],
                                   SampleTV( starts=False, numElements=5 ), SampleTV( numElements=5 ), \
                                   tail='ha1', assumptions='independentPoints')

    def runTest(self):
        self.test_compute()
    
#class TestPointPositioningPValStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = PointPositioningPValStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestPointPositioningPValStatSplittable().debug()
    #TestPointPositioningPValStatUnsplittable().debug()
    unittest.main()
