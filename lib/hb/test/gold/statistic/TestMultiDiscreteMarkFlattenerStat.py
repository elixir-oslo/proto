import unittest
from gold.statistic.MultiDiscreteMarkFlattenerStat import MultiDiscreteMarkFlattenerStat
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

class TestMultiDiscreteMarkFlattenerStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = MultiDiscreteMarkFlattenerStat

    def setUp(self):
        gold.statistic.MultiDiscreteMarkFlattenerStat.PlainTrack = provideTrack 

    def tearDown(self):
        gold.statistic.MultiDiscreteMarkFlattenerStat.PlainTrack = PlainTrack

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        self._assertCompute( [0]*5 + [5]*5 + [10]*5 + [15]*5, SampleTV(numElements=0, anchor=[0,20]), numDiscreteVals=4, reducedNumDiscreteVals=4, \
            marksStat='MarksListStat', controlTrackNameList='^^'.join([encodeTn(range(10,30)), encodeTn(range(10,30))]) )

        self._assertCompute( [0,0,1,1,2,6,11,15], SampleTV(numElements=0, anchor=[0,8]), numDiscreteVals=4, reducedNumDiscreteVals=4, \
            marksStat='MarksListStat', controlTrackNameList='^^'.join([ encodeTn(range(0,8)), encodeTn([0,0,0,0,0,1,2,3]) ]) )

        self._assertCompute( [0]*5 + [1]*5 + [2]*5 + [3]*5, SampleTV(numElements=0, anchor=[0,20]), numDiscreteVals=4, reducedNumDiscreteVals=4, \
            marksStat='MarksListStat', controlTrackNameList=encodeTn(range(10,30)) )

    #def test_createChildren(self):
    #    self._assertCreateChildren([], SampleTV_Num( anchor= ))

    def runTest(self):
        pass
    
#class TestMultiDiscreteMarkFlattenerStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = MultiDiscreteMarkFlattenerStat
#
#    def test_compute(self):
#        pass#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestMultiDiscreteMarkFlattenerStatSplittable().debug()
    #TestMultiDiscreteMarkFlattenerStatUnsplittable().debug()
    unittest.main()
