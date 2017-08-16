import unittest
from gold.statistic.NearestSegmentDistsStat import NearestSegmentDistsStat
from gold.statistic.RawDataStat import RawDataStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestNearestSegmentDistsStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = NearestSegmentDistsStat

    def testIncompatibleTracks(self):
        self._assertIncompatibleTracks(SampleTV( starts=[0,5] ), SampleTV( starts=[0,5] ))
        self._assertIncompatibleTracks(SampleTV( ends=[0,5] ), SampleTV( ends=[0,5] ))
        self._assertIncompatibleTracks(SampleTV_Num( anchor=[5,10] ), SampleTV_Num( anchor=[5,10] ))

    def test_compute(self):
        self._assertCompute({'Result': [], 'SegLengths': []}, \
                            SampleTV( segments=[] ), SampleTV( segments=[[1,2],[4,5],[5,6],[6,7],[8,9]] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({'Result': [None,None], 'SegLengths': [1,1]}, \
                            SampleTV( segments=[[2,3],[6,7]] ), SampleTV( segments=[] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({'Result': [1,1,0,1,2], 'SegLengths': [1,1,1,1,1]}, \
                            SampleTV( segments=[[0,1],[2,3],[6,7],[7,8],[10,11]] ), \
                            SampleTV( segments=[[1,2],[4,5],[5,6],[6,7],[8,9]] ),\
                            assertFunc=self.assertListsOrDicts)
        
        self._assertCompute({'Result': [3,2,0,0,3,7], 'SegLengths': [2,3,4,3,2,2]}, \
                            SampleTV( segments=[[0,2],[8,11],[14,18],[20,23],[26,28],[30,32]] ), \
                            SampleTV( segments=[[4,6],[12,16],[22,24]] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({'Result': [0,0,0,0,0], 'SegLengths': [6,4,2,4,4]}, \
                            SampleTV( segments=[[20,26],[28,32],[34,36],[38,42],[54,58]] ), \
                            SampleTV( segments=[[22,24],[30,40],[52,56],[57,60]] ),\
                            assertFunc=self.assertListsOrDicts)

        #test strand-specific dist
        self._assertCompute({'Result': [3,3,0,0,None,7], 'SegLengths': [2,3,4,3,2,2]}, \
                            SampleTV( segments=[[0,2],[8,11],[14,18],[20,23],[26,28],[30,32]], strands=[True,False,False,True,True,False] ), \
                            SampleTV( segments=[[4,6],[12,16],[22,24]] ),\
                            assertFunc=self.assertListsOrDicts, distDirection='downstream')
        self._assertCompute({'Result': [3,3,0,0,None,7], 'SegLengths': [2,3,4,3,2,2]}, \
                            SampleTV( segments=[[0,2],[8,11],[14,18],[20,23],[26,28],[30,32]], strands=[False,True,True,False,False,True] ), \
                            SampleTV( segments=[[4,6],[12,16],[22,24]] ),\
                            assertFunc=self.assertListsOrDicts, distDirection='upstream')
        self._assertCompute({'Result': [None,2,0,0,3,None], 'SegLengths': [2,3,4,3,2,2]}, \
                            SampleTV( segments=[[0,2],[8,11],[14,18],[20,23],[26,28],[30,32]], strands=[True,False,False,True,True,False] ), \
                            SampleTV( segments=[[4,6],[12,16],[22,24]] ),\
                            assertFunc=self.assertListsOrDicts, distDirection='upstream')
        
        self._assertCompute({'Result': [100], 'SegLengths': [10]}, \
                            SampleTV( segments=[[110,120]] ), SampleTV( segments=[[0,11]] ),\
                            assertFunc=self.assertListsOrDicts)
        
        
    def test_createChildren(self):
        self._assertCreateChildren([RawDataStatUnsplittable] * 2, SampleTV( segments=[[10,100]] ), SampleTV( segments=[[10,100]] ))

    def runTest(self):
        self.test_compute()
    
#class TestNearestSegmentDistStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = NearestSegmentDistStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass

if __name__ == "__main__":    
    #TestNearestSegmentDistStatSplittable().debug()
    #TestNearestSegmentDistsStatUnsplittable().debug()
    unittest.main()
