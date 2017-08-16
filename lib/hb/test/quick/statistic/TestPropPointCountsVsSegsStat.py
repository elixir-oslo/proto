import unittest
from quick.statistic.PropPointCountsVsSegsStat import PropPointCountsVsSegsStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
from collections import OrderedDict

class TestPropPointCountsVsSegsStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = PropPointCountsVsSegsStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        self._assertCompute(OrderedDict([('Both', 0), ('Only1', 0), ('BothProp', None), ('Only1Prop', None), ('SegCoverage', 0)]), \
                            SampleTV( starts=[], anchor=[10,100] ), SampleTV( segments=[], anchor=[10,100] ))
        
        self._assertCompute(OrderedDict([('Both', 3), ('Only1', 2), ('BothProp', 0.6), ('Only1Prop', 0.4), ('SegCoverage', 0.25)]), \
                            SampleTV( starts=[10, 20, 40, 49, 65], anchor=[10,90] ), SampleTV( segments=[[20,30], [40,50]], anchor=[10,90] ))
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([YStat], SampleTV( data2 ))

    def runTest(self):
        pass
    
#class TestPropPointCountsVsSegsStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = PropPointCountsVsSegsStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestPropPointCountsVsSegsStatSplittable().debug()
    #TestPropPointCountsVsSegsStatUnsplittable().debug()
    unittest.main()
