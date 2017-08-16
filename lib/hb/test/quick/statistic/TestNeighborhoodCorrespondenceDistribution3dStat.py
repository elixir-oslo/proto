import unittest
from quick.statistic.NeighborhoodCorrespondenceDistribution3dStat import NeighborhoodCorrespondenceDistribution3dStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestNeighborhoodCorrespondenceDistribution3dStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = NeighborhoodCorrespondenceDistribution3dStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        from gold.application.StatRunner import StatJob
        #from quick.application.UserBinSource import UserBinSource
        from gold.track.GenomeRegion import GenomeRegion
        
        StatJob.USER_BIN_SOURCE = [GenomeRegion('TestGenome', 'chr21', 0, 100), GenomeRegion('TestGenome', 'chr21', 100, 200)]
        self._assertCompute([2.0,None], \
                            SampleTV( starts=[0,10,120,130], ids=['a','b','c','d'], edges=[['d'],['d'],['d'],list('abc')], anchor=[0,200] ), \
                            globalSource='userbins', weightThreshold='0')
        
        self._assertCompute([None,None], \
                            SampleTV( starts=[], ids=[], edges=[], anchor=[0,200] ), \
                            globalSource='userbins', weightThreshold='0')
        
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([], SampleTV_Num( anchor= ))

    def runTest(self):
        pass
    
#class TestXSplittable(StatUnitTest):
#    CLASS_TO_CREATE = NumberOfNodesAndEdges3dStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestNumberOfNodesAndEdges3dStatSplittable().debug()
    #TestNumberOfNodesAndEdges3dStatUnsplittable().debug()
    unittest.main()
