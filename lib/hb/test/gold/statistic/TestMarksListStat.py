import unittest
from gold.statistic.MarksListStat import MarksListStat
from gold.track.GenomeRegion import GenomeRegion
from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestMarksListStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = MarksListStat

    def testIncompatibleTracks(self):
        pass
        #self._assertIncompatibleTracks(SampleTV( 1 ))

    def test_compute(self):
        self._assertCompute([1,2,3], SampleTV( starts = [10,30,50], vals = [1,2,3], anchor = [0,100], valDType='int32' ), \
                            assertFunc=self.assertListsOrDicts, markType='number (integer)')
        self._assertCompute([1,2,3], SampleTV_Num( vals = [1,2,3], anchor = [0,3], valDType='int32' ), \
                            assertFunc=self.assertListsOrDicts, markType='number (integer)')
        self._assertCompute([], SampleTV( vals = [], ends=False, numElements = 0, anchor = [0,100], valDType='int32' ), \
                            assertFunc=self.assertListsOrDicts, markType='number (integer)') 
        
    #def test_createChildren(self):  
        #self._assertCreateChildren([RawDataStatUnsplittable]*2, \
        #                            SampleTV( numElements=5 ), SampleTV_Num( anchor = [10,1000]  ))

class TestMarksListStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = MarksListStat
#
    def test_compute(self):
        self._assertCompute([1,2,3], SampleTV( starts = [10,30,150], vals = [1,2,3], anchor = [0,200], valDType='int32' ),\
                            binRegs = (GenomeRegion('TestGenome','chr21',0,100), GenomeRegion('TestGenome','chr21',100,200)),\
                            assertFunc=self.assertListsOrDicts, markType='number (integer)')
        self._assertCompute([1,2,3], SampleTV_Num( vals = [1,2,3], anchor = [99,102], valDType='int32' ), \
                            binRegs = (GenomeRegion('TestGenome','chr21',99,100), GenomeRegion('TestGenome','chr21',100,102)),\
                            assertFunc=self.assertListsOrDicts, markType='number (integer)')
        #        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    unittest.main()
