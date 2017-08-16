from gold.extra.nmers.NmerTools import NmerTools
from quick.util.CommonFunctions import flattenList
import unittest

class TestNmerTools(unittest.TestCase):
    def setUp(self):
        pass
    
    def testAllNmers(self):
        allTwoMers = flattenList([ [bp1+bp2 for bp2 in 'acgt'] for bp1 in 'acgt'])
        self.assertEqual(allTwoMers, list(NmerTools.allNmers(2)))
        self.assertEqual(4**3, len(list(NmerTools.allNmers(3))))
    
    def testNmerAsInt(self):
        self.assertEqual(0, NmerTools.nmerAsInt(''))
        self.assertEqual(0, NmerTools.nmerAsInt('a'))
        self.assertEqual(0, NmerTools.nmerAsInt('aa'))
        self.assertEqual(1, NmerTools.nmerAsInt('ac'))
        self.assertEqual(7, NmerTools.nmerAsInt('ct'))
        self.assertEqual(147, NmerTools.nmerAsInt('gcat'))

    def testIntAsNmer(self):
        self.assertEqual('', NmerTools.intAsNmer(0,0))
        self.assertEqual('a', NmerTools.intAsNmer(0,1))
        self.assertEqual('aa', NmerTools.intAsNmer(0,2))
        self.assertEqual('ac', NmerTools.intAsNmer(1,2))
        self.assertEqual('ct', NmerTools.intAsNmer(7,2))
        self.assertEqual('gcat', NmerTools.intAsNmer(147,4))

    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestNmerTools().debug()
    unittest.main()
