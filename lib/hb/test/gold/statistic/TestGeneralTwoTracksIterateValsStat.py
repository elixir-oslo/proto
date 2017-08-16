#import unittest
#from gold.statistic.GeneralTwoTracksIterateValsStat import GeneralTwoTracksIterateValsStat
#
#from test.gold.statistic.StatUnitTest import StatUnitTest
#from test.gold.track.common.SampleTrackWithConverters import SampleTrackWithConverters
#from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
#from gold.origdata.GenomeElementSource import GenomeElementSource
#from gold.track.GenomeRegion import GenomeRegion
#from gold.statistic.MagicStatFactory import MagicStatFactory

#class TestGeneralTwoTracksIterateValsStatUnsplittable(StatUnitTest):
#    CLASS_TO_CREATE = GeneralTwoTracksIterateValsStat
#
#    def testIncompatibleTracks(self):
#        self._assertIncompatibleTracks(SampleTV( anchor=[10,17], starts=[1,3,6], vals=['a','b','a'], \
#                                       valDType=GenomeElementSource.CATEGORY_DATA_TYPE ), \
#                                       SampleTV_Num( vals=range(7) ) , \
#                                       rawStatistic='TpRawSegsOverlapStat', testWithConverter=True)
#        self._assertIncompatibleTracks(SampleTV_Num( vals=range(7) ) , \
#                                       SampleTV( anchor=[10,17], starts=[1,3,6], vals=['a','b','a'], \
#                                       valDType=GenomeElementSource.CATEGORY_DATA_TYPE ), \
#                                       rawStatistic='TpRawSegsOverlapStat', testWithConverter=True)
#                                       
#    def test_compute(self):
#        self._assertCompute({'a':{'A':4, 'B':3}, 'b':{'A':0, 'B':1}}, \
#                            SampleTV( anchor=[10,100], segments=[[2,6], [8,10], [15,20]], \
#                                      vals=['a','b','a'], valDType=GenomeElementSource.CATEGORY_DATA_TYPE ), \
#                            SampleTV( anchor=[10,100], segments=[[0,8], [9,12], [14,18]], \
#                                      vals=['A','B','B'], valDType=GenomeElementSource.CATEGORY_DATA_TYPE ), \
#                            rawStatistic='TpRawSegsOverlapStat', testWithConverter=True)
#        self._assertCompute({False:{False:1, True:4}, True:{False:2, True:3}}, \
#                            SampleTV( anchor=[10,100], segments=[[2,6], [4,10], [15,20]], \
#                                      vals=[True, False, False], valDType='bool8' ), \
#                            SampleTV( anchor=[10,100], segments=[[3,5], [3,8], [20,22]], \
#                                      vals=[False, True, False], valDType='bool8' ), \
#                            rawStatistic='TpRawSegsOverlapStat', testWithConverter=True)
#        self._assertCompute({True:{}, False:{}},
#                            SampleTV( anchor=[10,100], segments=[[3,5], [3,8], [20,22]], \
#                                      vals=[True, True, False], valDType='bool8' ), \
#                            SampleTV( anchor=[10,100], segments=[], vals=[], \
#                                      valDType=GenomeElementSource.CATEGORY_DATA_TYPE ), \
#                            rawStatistic='TpRawSegsOverlapStat', testWithConverter=True)
#        self._assertCompute({},
#                            SampleTV( anchor=[10,100], segments=[], vals=[], \
#                                      valDType=GenomeElementSource.CATEGORY_DATA_TYPE ), \
#                            SampleTV( anchor=[10,100], segments=[[3,5], [3,8], [20,22]], \
#                                      vals=[True, True, False], valDType='bool8' ), \
#                            rawStatistic='TpRawSegsOverlapStat', testWithConverter=True)
#    #
#    #def test_createChildren(self):
#    #    self._assertCreateChildren([], SampleTV_Num( anchor= ))
#    #
#    #def runTest(self):
#    #    pass
#    
#class TestGeneralTwoTracksIterateValsStatSplittableChildren(StatUnitTest):
#    CLASS_TO_CREATE = GeneralTwoTracksIterateValsStat
#
#    _targetForFirstTest = {'a':{'A':2, 'B':5}, 'b':{'A':14, 'B':0}}
#    
#    def test_compute(self):
#        for storeChildren in [True, False]:
#            self._assertCompute(self._targetForFirstTest, \
#                                SampleTV( anchor=[0,1000], segments=[[2,6], [94,110], [215,220], [310,320]], \
#                                          vals=['a','b','a','a'], valDType=GenomeElementSource.CATEGORY_DATA_TYPE ), \
#                                SampleTV( anchor=[0,1000], segments=[[3,5], [93,108], [220,222], [315,325]], \
#                                          vals=['A','A','B','B'], valDType=GenomeElementSource.CATEGORY_DATA_TYPE ), \
#                                rawStatistic='TpRawSegsOverlapStat', storeChildren=storeChildren, testWithConverter=True)
#            self._assertCompute({True:{}, False:{}},
#                                SampleTV( anchor=[0,1000], segments=[[3,5], [93,108], [220,222]], \
#                                          vals=[True, True, False], valDType='bool8' ), \
#                                SampleTV( anchor=[0,1000], segments=[], vals=[], \
#                                          valDType=GenomeElementSource.CATEGORY_DATA_TYPE ), \
#                                rawStatistic='TpRawSegsOverlapStat', storeChildren=storeChildren, testWithConverter=True)
#            self._assertCompute({},
#                                SampleTV( anchor=[0,1000], segments=[], vals=[], \
#                                          valDType=GenomeElementSource.CATEGORY_DATA_TYPE ), \
#                                SampleTV( anchor=[0,1000], segments=[[3,5], [3,8], [20,22]], \
#                                          vals=[True, True, False], valDType='bool8' ), \
#                                rawStatistic='TpRawSegsOverlapStat', storeChildren=storeChildren, testWithConverter=True)
# 
#class TestGeneralTwoTracksIterateValsStatSplittable(TestGeneralTwoTracksIterateValsStatSplittableChildren):
#    from gold.statistic.Statistic import StatisticDynamicDoubleDictSumResSplittable
#    class GeneralTwoTracksIterateValsStatSplittable(StatisticDynamicDoubleDictSumResSplittable):
#        pass
#
#    CLASS_TO_CREATE = GeneralTwoTracksIterateValsStatSplittable
#
#    _targetForFirstTest = {'a':{'A':2, 'B':5}, 'b':{'A':14}}
#
#class TestGeneralTwoTracksIterateValsStatGloballySplittable(TestGeneralTwoTracksIterateValsStatSplittableChildren):
#    from gold.statistic.Statistic import StatisticDynamicDoubleDictSumResSplittable, OnlyGloballySplittable
#    class GeneralTwoTracksIterateValsStatSplittable(StatisticDynamicDoubleDictSumResSplittable, OnlyGloballySplittable):
#        pass
#
#    CLASS_TO_CREATE = GeneralTwoTracksIterateValsStatSplittable
#
#    _targetForFirstTest = {'a':{'A':2, 'B':5}, 'b':{'A':14}}
#
##    def test_createChildren(self):
##        pass
#    
#    #def runTest(self):
#    #    pass
    
#if __name__ == "__main__":
#    #TestGeneralTwoTracksIterateValsStatSplittable().debug()
#    #TestGeneralTwoTracksIterateValsStatUnsplittable().debug()
#    unittest.main()
