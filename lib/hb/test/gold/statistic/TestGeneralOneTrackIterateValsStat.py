#import unittest
#from gold.statistic.GeneralOneTrackIterateValsStat import GeneralOneTrackIterateValsStat
#
#from test.gold.statistic.StatUnitTest import StatUnitTest
#from test.gold.track.common.SampleTrackWithConverters import SampleTrackWithConverters
#from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
#from gold.origdata.GenomeElementSource import GenomeElementSource
#from gold.track.GenomeRegion import GenomeRegion
#from gold.statistic.MagicStatFactory import MagicStatFactory

#class TestGeneralOneTrackIterateValsStatUnsplittable(StatUnitTest):
#    CLASS_TO_CREATE = GeneralOneTrackIterateValsStat
#
#    def testIncompatibleTracks(self):
#        self._assertIncompatibleTracks(SampleTV( starts=[1,3,6], vals=['a','b','a'], \
#                                       valDType=GenomeElementSource.CATEGORY_DATA_TYPE ), \
#                                       rawStatistic='CountSegmentStat', testWithConverter=True)
#                                       
#    def test_compute(self):
#        self._assertCompute({'a':9, 'b':2}, SampleTV( anchor=[10,100], segments=[[2,6], [8,10], [15,20]], vals=['a','b','a'], \
#                                                      valDType=GenomeElementSource.CATEGORY_DATA_TYPE ), \
#                            rawStatistic='CountStat', testWithConverter=True)
#        self._assertCompute({True:9, False:6}, SampleTV( anchor=[10,100], segments=[[2,6], [4,10], [15,20]], \
#                                                         vals=[True, False, True], valDType='bool8' ), \
#                            rawStatistic='CountStat', testWithConverter=True)
#        self._assertCompute({}, SampleTV( anchor=[10,100], segments=[], vals=[], \
#                                          valDType=GenomeElementSource.CATEGORY_DATA_TYPE ), \
#                            rawStatistic='CountStat', testWithConverter=True)
#    #
#    #def test_createChildren(self):
#    #    self._assertCreateChildren([], SampleTV_Num( anchor= ))
#    #
#    #def runTest(self):
#    #    pass
#    
#class TestGeneralOneTrackIterateValsStatSplittableChildren(StatUnitTest):
#    CLASS_TO_CREATE = GeneralOneTrackIterateValsStat
#
#    def test_compute(self):
#        self._assertCompute({'a':9, 'b':12, 'c':10}, SampleTV( anchor=[0,1000], segments=[[2,6], [98,110], [115,120], [210,220]], \
#                                                               vals=['a','b','a','c'], valDType=GenomeElementSource.CATEGORY_DATA_TYPE ), \
#                            rawStatistic='CountStat', testWithConverter=True)
#        self._assertCompute({}, SampleTV( anchor=[0,1000], segments=[], vals=[], \
#                                          valDType=GenomeElementSource.CATEGORY_DATA_TYPE ), \
#                            rawStatistic='CountStat', testWithConverter=True)
# 
#class TestGeneralOneTrackIterateValsStatSplittable(TestGeneralOneTrackIterateValsStatSplittableChildren):
#    from gold.statistic.Statistic import StatisticDynamicDictSumResSplittable
#    class GeneralOneTrackIterateValsStatSplittable(StatisticDynamicDictSumResSplittable):
#        pass
#
#    CLASS_TO_CREATE = GeneralOneTrackIterateValsStatSplittable
#
#class TestGeneralOneTrackIterateValsStatGloballySplittable(TestGeneralOneTrackIterateValsStatSplittableChildren):
#    from gold.statistic.Statistic import StatisticDynamicDictSumResSplittable, OnlyGloballySplittable
#    class GeneralOneTrackIterateValsStatSplittable(StatisticDynamicDictSumResSplittable, OnlyGloballySplittable):
#        pass
#
#    CLASS_TO_CREATE = GeneralOneTrackIterateValsStatSplittable

        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
#if __name__ == "__main__":
#    #TestGeneralOneTrackIterateValsStatSplittable().debug()
#    #TestGeneralOneTrackIterateValsStatUnsplittable().debug()
#    unittest.main()
