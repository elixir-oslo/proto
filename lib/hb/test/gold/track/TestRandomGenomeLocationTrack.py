import unittest

from gold.track.GenomeRegion import GenomeRegion
from gold.track.RandomGenomeLocationTrack import RandomGenomeLocationTrack
from test.gold.track.common.SampleTrack import SampleTrack
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
import sys
import StringIO

class TestRandomGenomeLocationTrack(unittest.TestCase):
    def setUp(self):
        sys.stdout = StringIO.StringIO()
    
    def _doRandTest(self, origTV):
        origTrack = SampleTrack(origTV)
        queryReg = GenomeRegion('TestGenome','chr21',100,400)
        for randClass in [RandomGenomeLocationTrack]:
            for i in range(10):
                randTrack = randClass(origTrack, queryReg, i)
                randTV = randTrack.getTrackView(queryReg)
                self.assertEqual(len(queryReg), len(randTV))

    def testRandomization(self):
        anchor = [0, 46944323]
        
        self._doRandTest( SampleTV( segments=[], anchor=anchor ) )
    
        self._doRandTest( SampleTV( starts=True, ends=True, vals=False, strands=False, numElements=1000, anchor=anchor ) )
        self._doRandTest( SampleTV( starts=True, ends=True, vals=True, strands=True, numElements=1000, anchor=anchor ) )

        self._doRandTest( SampleTV( starts=True, ends=False, vals=False, strands=False, numElements=1000, anchor=anchor ) )
        self._doRandTest( SampleTV( starts=True, ends=False, vals=True, strands=True, numElements=1000, anchor=anchor ) )

        self._doRandTest( SampleTV( starts=False, ends=True, vals=False, strands=False, numElements=1000, anchor=anchor ) )
        self._doRandTest( SampleTV( starts=False, ends=True, vals=True, strands=True, numElements=1000, anchor=anchor ) )
        
        #self._doRandTest( SampleTV_Num( anchor=anchor ) )
        
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestPermutedSegsAndIntersegsRandomizedTrack().debug()
    unittest.main()
