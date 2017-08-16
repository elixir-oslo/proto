import unittest
import numpy
from gold.statistic.BinScaledSegCoverageStat import BinScaledSegCoverageStat
from gold.track.GenomeRegion import GenomeRegion

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestBinScaledSegCoverageStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = BinScaledSegCoverageStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV( 1 ))

    def test_compute(self):
        #self._assertCompute([0.7, 1.0, 0.2, 0.0], \
        #    SampleTV( segments=[[0,5], [8,22]], anchor=[0,40] ), numSubBins=4, assertFunc=self.assertListsOrDicts)

        self._assertCompute([0.0, 0.0, 0.2, 1.0, 0.3, 0.0, 0.0], \
            SampleTV( segments=[[28,42],[44,45]], anchor=[0,70] ), numSubBins=7, assertFunc=self.assertListsOrDicts)

        self._assertCompute([0,0,0,0], \
            SampleTV( segments=[]), numSubBins=4,assertFunc=self.assertListsOrDicts)

        self._assertCompute(None, \
            SampleTV( segments=[], anchor=[0,1]), numSubBins=4)

    #def test_createChildren(self):
    #    self._assertCreateChildren([4], SampleTV_Num( anchor=5 ))

    def runTest(self):
        self.test_compute()
    
class TestBinScaledSegCoverageStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = BinScaledSegCoverageStat

    def test_compute(self):
        resultA = { 'Result': {'sdOfMean': [0.24748737, 0.35355339, 0.28284271, 0.35355339], \
                                         'mean':[0.35, 0.5, 0.6, 0.5]} }
        self._assertCompute(resultA, \
            SampleTV( segments=[[50,100], [100,105], [108,122]], anchor=[0,140] ), numSubBins=4, binRegs = \
            (GenomeRegion('TestGenome','chr21',0,100), GenomeRegion('TestGenome','chr21',100,140)), \
            assertFunc=self.assertListsOrDicts)
        
        self._assertCompute({ 'Result': {'sdOfMean': [0,0,0,0], 'mean':[0,0,0,0]} }, \
            SampleTV( segments=[], anchor=[0,4] ), numSubBins=4, binRegs = \
            (GenomeRegion('TestGenome','chr21',0,4), GenomeRegion('TestGenome','chr21',4,4)),\
            assertFunc=self.assertListsOrDicts)

        #Manually force use of _computeThatHandlesOverlap, and check that it gives equal result as above.
        self._assertCompute(resultA, \
            SampleTV( segments=[[50,100], [100,105], [108,122]], anchor=[0,140] ), numSubBins=4, binRegs = \
            (GenomeRegion('TestGenome','chr21',0,100), GenomeRegion('TestGenome','chr21',100,140)), \
            assertFunc=self.assertListsOrDicts, withOverlaps='yes')

        resultB = { 'Result': {'sdOfMean': [0.24748737, 0.35355339, 0.63639610306789274, 0.35355339], \
                                         'mean':[0.35, 0.5, 1.1, 0.5]} }
        
        self._assertCompute(resultB, \
            SampleTV( segments=[[50,100],[50,75], [100,105], [108,122]], anchor=[0,140] ), numSubBins=4, binRegs = \
            (GenomeRegion('TestGenome','chr21',0,100), GenomeRegion('TestGenome','chr21',100,140)), \
            assertFunc=self.assertListsOrDicts, withOverlaps='yes')
    #    
    #def test_createChildren(self):
    #    pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestBinScaledSegCoverageStatSplittable().debug()
    #TestBinScaledSegCoverageStatUnsplittable().debug()
    unittest.main()
