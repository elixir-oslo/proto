import unittest
from quick.statistic.NumberOfNodesAndEdges3dStat import NumberOfNodesAndEdges3dStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestNumberOfNodesAndEdges3dStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = NumberOfNodesAndEdges3dStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        self._assertCompute({'totNodes': 0, 'totEdges': 0}, SampleTV( starts=[], ids=[], edges=[] ))
        self._assertCompute({'totNodes': 3, 'totEdges': 4}, SampleTV( starts=[0,10,20], ids=['a','b','c'], edges=[['b','c'],['a', 'c'],[]] ))
        
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
