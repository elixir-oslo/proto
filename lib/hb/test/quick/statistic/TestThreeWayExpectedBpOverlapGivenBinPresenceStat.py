import unittest
from quick.statistic.ThreeWayExpectedBpOverlapGivenBinPresenceStat import \
    ThreeWayExpectedBpOverlapGivenBinPresenceStat
from gold.track.GenomeRegion import GenomeRegion

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestThreeWayExpectedBpOverlapGivenBinPresenceStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = ThreeWayExpectedBpOverlapGivenBinPresenceStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        #self._assertCompute(1, SampleTV( 2 ))
        ans = {'&&': 1/90.0, '*&': 0.1*0.2, '&*': 0.1*0.2, '**': 0.1*0.2}
        answer = dict([(k+'_GivenBinPresence',v) for k,v in ans.items()])
        self._assertCompute(answer, \
                            SampleTV( segments=[[10,28]], anchor=[10,100] ), \
                            SampleTV( segments=[[27,36]], anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)


        exp = 0.5*(0.1*0.2) + 0.5*(1.0*1.0)
        ans = {'&&': 91/180.0, '*&':exp, '&*': exp, '**': exp}
        answer = dict([(k+'_GivenBinPresence',v) for k,v in ans.items()])
        #NB! This test assumes splittable statistic is applied below. This is not done as of now, since ThreeWayExpectedBpOverlapGivenBinPresenceAsWholeBpsStatSplittable inherits OnlyGloballySplittable
        #Must for now remove this inheritance to make test work. Should be changed to allow tests to split globally, but how?        
        self._assertCompute(answer, \
                            SampleTV( segments=[[10,28], [90,180]], anchor=[10,190] ), \
                            SampleTV( segments=[[27,36], [90,180]], anchor=[10,190] ),\
                            assertFunc=self.assertListsOrDicts, \
                            binRegs = (GenomeRegion('TestGenome','chr21',10,100), GenomeRegion('TestGenome','chr21',100,190)))
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([], SampleTV_Num( anchor= ))

    def runTest(self):
        pass
    
#class TestXSplittable(StatUnitTest):
#    CLASS_TO_CREATE = X
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestXSplittable().debug()
    #TestXUnsplittable().debug()
    unittest.main()
