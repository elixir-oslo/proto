import unittest
from gold.statistic.FlattenedDiscreteMarksHistStat import FlattenedDiscreteMarksHistStat
import gold.statistic.MultiDiscreteMarkFlattenerStat
from gold.track.Track import PlainTrack

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
from test.gold.track.common.SampleTrack import SampleTrack

def provideTrack(tn):
    valList = tn[0].split(',')
    return SampleTrack(SampleTV_Num( vals=valList, anchor=[0,len(valList)] ))

def encodeTn(intList):
    return ','.join([str(x) for x in intList])

class TestFlattenedDiscreteMarksHistStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = FlattenedDiscreteMarksHistStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV( 1 ))

    def setUp(self):
        gold.statistic.MultiDiscreteMarkFlattenerStat.PlainTrack = provideTrack 

    def tearDown(self):
        gold.statistic.MultiDiscreteMarkFlattenerStat.PlainTrack = PlainTrack

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        self._assertCompute( [5,0,0,0,0,5,0,0,0,0,5,0,0,0,0,5], SampleTV(numElements=0, anchor=[0,20]), numDiscreteVals=4, reducedNumDiscreteVals=4, \
            marksStat='MarksListStat', controlTrackNameList='^^'.join([encodeTn(range(10,30)), encodeTn(range(10,30))]) )

        self._assertCompute( [2,2,1,0,0,0,1,0,0,0,0,1,0,0,0,1], SampleTV(numElements=0, anchor=[0,8]), numDiscreteVals=4, reducedNumDiscreteVals=4, \
            marksStat='MarksListStat', controlTrackNameList='^^'.join([ encodeTn(range(0,8)), encodeTn([0,0,0,0,0,1,2,3]) ]) )

        self._assertCompute( [2,2,1,0,0,0,0,1,0,0,0,1,0,0,1,0], SampleTV(numElements=0, anchor=[0,8]), numDiscreteVals=4, reducedNumDiscreteVals=4, \
            marksStat='MarksListStat', controlTrackNameList='^^'.join([ encodeTn(range(0,8)), encodeTn([0,0,0,0,0,3,2,1]) ]) )

        self._assertCompute( [5]*4, SampleTV(numElements=0, anchor=[0,20]), numDiscreteVals=4, reducedNumDiscreteVals=4, \
            marksStat='MarksListStat', controlTrackNameList=encodeTn(range(10,30)) )

        self._assertCompute( [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1], SampleTV(starts=[0,5,10,15], anchor=[0,20]), numDiscreteVals=4, reducedNumDiscreteVals=4, \
            marksStat='ExtractMarksStat', controlTrackNameList='^^'.join([encodeTn(range(10,30)), encodeTn(range(10,30))]) )

        self._assertCompute( [2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1], SampleTV(starts=[0,1,2,7], anchor=[0,8]), numDiscreteVals=4, reducedNumDiscreteVals=4, \
            marksStat='ExtractMarksStat', controlTrackNameList='^^'.join([ encodeTn(range(0,8)), encodeTn([0,0,0,0,0,1,2,3]) ]) )
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([4], SampleTV_Num( anchor=5 ))

    def runTest(self):
        pass
    
#class TestFlattenedDiscreteMarksHistStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = FlattenedDiscreteMarksHistStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestFlattenedDiscreteMarksHistStatSplittable().debug()
    #TestFlattenedDiscreteMarksHistStatUnsplittable().debug()
    unittest.main()
