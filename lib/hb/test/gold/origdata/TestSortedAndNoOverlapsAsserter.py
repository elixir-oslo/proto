import unittest
from test.gold.origdata.common.Asserts import assertDecorator
from gold.origdata.SortedAndNoOverlapsAsserter import SortedAndNoOverlapsAsserter
from gold.util.CustomExceptions import NotValidGESequence

class TestSortedAndNoOverlapsAsserter(unittest.TestCase):
    def setUp(self):
        pass
    
    def _processAll(self, candidateList):
        assertDecorator(SortedAndNoOverlapsAsserter, self.assertEqual, candidateList, candidateList)

    def testAssertion(self):
        self._processAll([['A','chr2',3,8],['B','chr1',2,5]])
        self._processAll([['A','chr1',3,8],['A','chr2',2,5]])
        self._processAll([['A','chr1',2,5],['A','chr1',5,10]])

        self._processAll([[None,'chr2',2,5],[None,'chr1',3,8]])
        self._processAll([[None,'chr1',2,5],[None,'chr1',5,10]])

        self._processAll([['B','chr1',2,None],['A','chr2',3,None]])
        self._processAll([['A','chr1',2,None],['A','chr1',3,None]])

        self._processAll([['B','chr1',None,5],['A','chr2',None,8]])
        self._processAll([['A','chr1',None,5],['A','chr1',None,8]])

        self.assertRaises( NotValidGESequence, self._processAll, [['A','chr1',3,5],['A','chr1',2,8]] )
        self.assertRaises( NotValidGESequence, self._processAll, [['A','chr1',2,8],['A','chr1',2,5]] )
        
        self.assertRaises( NotValidGESequence, self._processAll,[[None,'chr1',3,5],[None,'chr1',2,8]] )
        self.assertRaises( NotValidGESequence, self._processAll,[[None,'chr1',2,8],[None,'chr1',2,5]] )
        
        self.assertRaises( NotValidGESequence, self._processAll,[['A','chr1',3,None],['A','chr1',2,None]] )
        self.assertRaises( NotValidGESequence, self._processAll,[['A','chr1',3,None],['A','chr1',3,None]] )
        self.assertRaises( NotValidGESequence, self._processAll,[['A','chr1',None,8],['A','chr1',None,5]] )
        self.assertRaises( NotValidGESequence, self._processAll,[['A','chr1',None,8],['A','chr1',None,8]] )

        self.assertRaises( NotValidGESequence, self._processAll,[['A','chr1',0,10],['A','chr1',2,5]] )
        self.assertRaises( NotValidGESequence, self._processAll,[['A','chr1',0,10],['A','chr1',0,10]] )
        self.assertRaises( NotValidGESequence, self._processAll,[['A','chr1',0,10],['A','chr1',2,15]] )
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestSortedAndNoOverlapsAsserter().debug()
    unittest.main()
