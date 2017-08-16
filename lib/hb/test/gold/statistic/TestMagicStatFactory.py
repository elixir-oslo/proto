import unittest
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.SumStat import SumStat, SumStatUnsplittable, SumStatSplittable
from gold.track.GenomeRegion import GenomeRegion
from gold.statistic.Statistic import Statistic
from gold.track.Track import Track

import gold.util.CompBinManager
from gold.util.CompBinManager import CompBinManager

class TestMagicStatFactory(unittest.TestCase):
    def setUp(self):
        gold.util.CompBinManager.COMP_BIN_SIZE = 100
        self._ALLOW_COMP_BIN_SPLITTING = CompBinManager.ALLOW_COMP_BIN_SPLITTING
        CompBinManager.ALLOW_COMP_BIN_SPLITTING = True
        
    def tearDown(self):
        from config.Config import COMP_BIN_SIZE
        gold.util.CompBinManager.COMP_BIN_SIZE = COMP_BIN_SIZE
        CompBinManager.ALLOW_COMP_BIN_SPLITTING = self._ALLOW_COMP_BIN_SPLITTING
                            
    def testSplitMagic(self):
        self.assertTrue(isinstance(SumStat([GenomeRegion('TestGenome','chr21',0,100)], Track(['dummy'])), SumStatSplittable))
        self.assertTrue(isinstance(SumStat(GenomeRegion('TestGenome','chr21',0,150), Track(['dummy'])), SumStatSplittable))
        self.assertTrue(isinstance(SumStat(GenomeRegion('TestGenome','chr21',0,100), Track(['dummy'])), SumStatUnsplittable))
    
    def testMemoMagic(self):
        stat1v1 = SumStat(GenomeRegion('TestGenome','chr21',0,100), Track(['dummy']))
        stat1v1._result = 1
        self.assertEqual(stat1v1._result, 1)

        stat1v2 = SumStat(GenomeRegion('TestGenome','chr21',0,100), Track(['dummy']))
        self.assertEqual(stat1v2._result, 1)

        stat2 = SumStat(GenomeRegion('TestGenome','chr21',0,99), Track(['dummy']))
        self.assertFalse(stat2.hasResult())
    
if __name__ == "__main__":
    unittest.main()
