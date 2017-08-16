import unittest
from gold.statistic.BpOverlapPValStat import BpOverlapPValStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestBpOverlapPValStatUnsplittable(StatUnitTest):
    #THROW_EXCEPTION = False
    CLASS_TO_CREATE = BpOverlapPValStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV( (  )) ))

    def test_compute(self):
        self._assertCompute({'P-value': 1.0, 'track2Coverage': 0.25, 'E(Test statistic): ExpBpOverlap': 2.5, 'track1Coverage': 0.5, 'NumBpInBin': 20, 'Test statistic: ObsBpOverlap': 0, 'DiffFromMean': -2.5},\
                            SampleTV( segments=[[5,10],[15,20]], anchor=[0,20] ), SampleTV( segments=[[10,15]], anchor=[0,20] ))
        self._assertCompute({'P-value': 0.5, 'track2Coverage': 0.5, 'E(Test statistic): ExpBpOverlap': 5.0, 'track1Coverage': 0.5, 'NumBpInBin': 20, 'Test statistic: ObsBpOverlap': 5, 'DiffFromMean': 0.0},\
                            SampleTV( segments=[[0,10]], anchor=[0,20] ), SampleTV( segments=[[5,15]], anchor=[0,20] ))
        self._assertCompute({'P-value': 1.1102230246251565e-16, 'track2Coverage': 0.5, 'E(Test statistic): ExpBpOverlap': 50.0, 'track1Coverage': 0.5, 'NumBpInBin': 200, 'Test statistic: ObsBpOverlap': 100, 'DiffFromMean': 50.0},\
                            SampleTV( segments=[[0,100]], anchor=[0,200] ), SampleTV( segments=[[0,100]], anchor=[0,200] ))
        self._assertCompute({'P-value': 0.5, 'track2Coverage': 0.5, 'E(Test statistic): ExpBpOverlap': 5.0, 'track1Coverage': 0.5, 'NumBpInBin': 20, 'Test statistic: ObsBpOverlap': 5, 'DiffFromMean': 0.0},\
                            SampleTV( segments=[[0,10]], anchor=[0,20] ), SampleTV( segments=[[5,15]], anchor=[0,20] ))

        self._assertCompute({'P-value': None, 'track2Coverage': 0.0, 'E(Test statistic): ExpBpOverlap': 0.0, 'track1Coverage': 0.5, 'NumBpInBin': 20, 'Test statistic: ObsBpOverlap': 0, 'DiffFromMean': 0.0},\
                            SampleTV( segments=[[0,10]], anchor=[0,20] ), SampleTV( segments=[], anchor=[0,20] ))
        self._assertCompute({'P-value': None, 'track2Coverage': 0.0, 'E(Test statistic): ExpBpOverlap': 0.0, 'track1Coverage': 0.0, 'NumBpInBin': 20, 'Test statistic: ObsBpOverlap': 0, 'DiffFromMean': 0.0},\
                            SampleTV( segments=[], anchor=[0,20] ), SampleTV( segments=[], anchor=[0,20] ))
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([], SampleTV_Num( anchor=   ))

    def runTest(self):
        pass
    
#class TestBpOverlapPValStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = BpOverlapPValStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestBpOverlapPValStatSplittable().debug()
    #TestBpOverlapPValStatUnsplittable().debug()
    unittest.main()
