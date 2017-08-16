import unittest
import os
from config.Config import PROCESSED_DATA_PATH, ORIG_DATA_PATH
from gold.util.CompBinManager import CompBinManager
from gold.track.GenomeRegion import GenomeRegion
from gold.util.CommonFunctions import createDirPath, parseDirPath, extractTrackNameFromOrigPath, smartSum

class TestCommonFunctions(unittest.TestCase):
    def setUp(self):
        self.genome = 'hg18'
        self.chr = 'chr1'

    def testCreateDirPath(self):
        trackName = ['melting', 'discr']
        self.assertEqual('BASE/' + str(CompBinManager.getIndexBinSize()) + '/noOverlaps/hg18/melting/discr/chr1', \
                         createDirPath(trackName, self.genome, self.chr, False, 'BASE'))
        self.assertEqual('BASE/' + str(CompBinManager.getIndexBinSize()) + '/withOverlaps/hg18/melting/discr/chr1', \
                         createDirPath(trackName, self.genome, self.chr, True, 'BASE'))

        self.assertEqual('BASE/' + str(CompBinManager.getIndexBinSize()) + '/noOverlaps/hg18/melting/discr', \
                         createDirPath(trackName, self.genome, None, False, 'BASE'))
        self.assertEqual('BASE/' + str(CompBinManager.getIndexBinSize()) + '/noOverlaps/hg18/melting/discr/', \
                         createDirPath(trackName, self.genome, '', False, 'BASE'))

    def testParseDirPath(self):
        self.assertEqual(('hg18', ('melting','discr'), 'chr1'), parseDirPath(PROCESSED_DATA_PATH + '/noOverlaps/10000/hg18/melting/discr/chr1'))

    def testExtractTrackNameFromOrigPath(self):
        self.assertEqual(['melting', 'discr'], extractTrackNameFromOrigPath(ORIG_DATA_PATH + os.sep + 'hg18/melting/discr/chr1.wig'))

    def testSmartSum(self):
        self.assertEqual(6, smartSum([1, 2, 3]))
        self.assertEqual(3, smartSum([1, 2, None]))
        self.assertEqual(None, smartSum([None, None, None]))
        self.assertEqual(0, smartSum([]))
        self.assertRaises(TypeError, smartSum['a','b'])

if __name__ == "__main__":
    unittest.main()
