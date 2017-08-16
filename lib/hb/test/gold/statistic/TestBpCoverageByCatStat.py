import unittest
from gold.statistic.BpCoverageByCatStat import BpCoverageByCatStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
from gold.origdata.GenomeElementSource import GenomeElementSource

class TestBpCoverageByCatStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = BpCoverageByCatStat
    
    def test_compute(self):
        self._assertCompute({'c1':2,'c2':1}, SampleTV_Num( anchor=[10,13], valDType='S', vals=['c1','c2','c1']  ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({'c1':20,'c2':5}, SampleTV( segments=[[10,20], [50,55], [80,90]], vals=['c1','c2','c1'], valDType='S', anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({'c1':80,'c2':15}, SampleTV( segments=[[10,50], [40,55], [40,70], [40,90]], vals=['c1','c2','c1','c1'], valDType='S', anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({'c1':75,'c2':15}, SampleTV( segments=[[10,70], [40,55], [40,60], [50,80], [85,88], [87,90]], vals=['c1','c2','c1','c1','c1','c1'], valDType='S', anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({'c1':2,'c2':1},  SampleTV( starts=[2,15,60], vals=['c1','c2','c1'], valDType='S', anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({'c1':85,'c2':5}, SampleTV( ends=[15,20,90], vals=['c1','c2','c1'], valDType='S', anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)

        self._assertCompute({'c1':1}, SampleTV( segments=[[0,1]], vals=['c1'], valDType='S', anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({}, SampleTV( segments=[], vals=[], valDType='S2', anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([RawDataStatUnsplittable], SampleTV_Num( anchor=[0,100] ))

class TestBpCoverageByCatStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = BpCoverageByCatStat

    def test_compute(self):
        self._assertCompute({'c1':2,'c2':1}, SampleTV_Num( anchor=[99,102], valDType='S', vals=['c1','c2','c1']  ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({'c1':120,'c2':105}, SampleTV( segments=[[10,20], [50,155], [80,190]], vals=['c1','c2','c1'], valDType='S', anchor=[10,200] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({'c1':180,'c2':115}, SampleTV( segments=[[10,50], [40,155], [40,170], [40,190]], vals=['c1','c2','c1','c1'], valDType='S', anchor=[10,200] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({'c1':2,'c2':1},  SampleTV( starts=[2,15,160], vals=['c1','c2','c1'], valDType='S', anchor=[10,200] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({'c1':185,'c2':5}, SampleTV( ends=[15,20,190], vals=['c1','c2','c1'], valDType='S', anchor=[10,200] ),\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute({}, SampleTV( segments=[], vals=[], valDType='S2', anchor=[10,200] ),\
                            assertFunc=self.assertListsOrDicts)

        #self._assertCompute(111, SampleTV_Num( anchor=[10,121] ))
        #self._assertCompute(41,  SampleTV( segments=[[10,20], [80,111]], anchor=[10,121] ))
        #self._assertCompute(3,   SampleTV( starts=[2,15,110], anchor=[10,121] ))
        #self._assertCompute(111, SampleTV( ends=[15,111], anchor=[10,121] ))
        #self._assertCompute(0, SampleTV( segments=[], anchor=[10,121] ))
        
if __name__ == "__main__":
    unittest.main()
