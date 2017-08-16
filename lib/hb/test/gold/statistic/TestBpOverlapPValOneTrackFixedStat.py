import unittest
from collections import OrderedDict
from gold.statistic.BpOverlapPValOneTrackFixedStat import BpOverlapPValOneTrackFixedStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestBpOverlapPValOneTrackFixedStatUnsplittable(StatUnitTest):
    #THROW_EXCEPTION = False
    CLASS_TO_CREATE = BpOverlapPValOneTrackFixedStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV( (  )) ))

    def test_compute(self):
        self._assertCompute(OrderedDict([('P-value', 1.0), ('Test statistic: ObsBpOverlap', 0L), ('E(Test statistic): ExpBpOverlap', 2.5), ('DiffFromMean', -2.5), ('BpsInTrack2Segments', 5L), ('NumBpInBin', 20), ('track1Coverage', 0.5), ('track2Coverage', 0.25)]),\
                            SampleTV( segments=[[5,10],[15,20]], anchor=[0,20] ), SampleTV( segments=[[10,15]], anchor=[0,20] ))
        self._assertCompute(OrderedDict([('P-value', 0.5), ('Test statistic: ObsBpOverlap', 5L), ('E(Test statistic): ExpBpOverlap', 5.0), ('DiffFromMean', 0.0), ('BpsInTrack2Segments', 10L), ('NumBpInBin', 20), ('track1Coverage', 0.5), ('track2Coverage', 0.5)]),\
                            SampleTV( segments=[[0,10]], anchor=[0,20] ), SampleTV( segments=[[5,15]], anchor=[0,20] ))
        self._assertCompute(OrderedDict([('P-value', 0.0), ('Test statistic: ObsBpOverlap', 100L), ('E(Test statistic): ExpBpOverlap', 50.0), ('DiffFromMean', 50.0), ('BpsInTrack2Segments', 100L), ('NumBpInBin', 200), ('track1Coverage', 0.5), ('track2Coverage', 0.5)]),\
                            SampleTV( segments=[[0,100]], anchor=[0,200] ), SampleTV( segments=[[0,100]], anchor=[0,200] ))
        self._assertCompute(OrderedDict([('P-value', 0.5), ('Test statistic: ObsBpOverlap', 5L), ('E(Test statistic): ExpBpOverlap', 5.0), ('DiffFromMean', 0.0), ('BpsInTrack2Segments', 10L), ('NumBpInBin', 20), ('track1Coverage', 0.5), ('track2Coverage', 0.5)]),\
                            SampleTV( segments=[[0,10]], anchor=[0,20] ), SampleTV( segments=[[5,15]], anchor=[0,20] ))

        self._assertCompute(OrderedDict([('P-value', None), ('Test statistic: ObsBpOverlap', 0L), ('E(Test statistic): ExpBpOverlap', 0.0), ('DiffFromMean', 0.0), ('BpsInTrack2Segments', 0L), ('NumBpInBin', 20), ('track1Coverage', 0.5), ('track2Coverage', 0.0)]),\
                            SampleTV( segments=[[0,10]], anchor=[0,20] ), SampleTV( segments=[], anchor=[0,20] ))
        self._assertCompute(OrderedDict([('P-value', None), ('Test statistic: ObsBpOverlap', 0L), ('E(Test statistic): ExpBpOverlap', 0.0), ('DiffFromMean', 0.0), ('BpsInTrack2Segments', 0L), ('NumBpInBin', 20L), ('track1Coverage', 0.0), ('track2Coverage', 0.0)]),\
                            SampleTV( segments=[], anchor=[0,20] ), SampleTV( segments=[], anchor=[0,20] ))
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([], SampleTV_Num( anchor=   ))

    def runTest(self):
        pass
    
#class TestBpOverlapPValOneTrackFixedStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = BpOverlapPValOneTrackFixedStat
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
