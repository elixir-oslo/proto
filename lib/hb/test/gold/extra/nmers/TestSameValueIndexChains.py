from gold.extra.nmers.SameValueIndexChains import SameValueIndexChainsFactory
from test.util.FileUtils import removeFile
import unittest
import os
import sys

class TestSameValueIndexChains(unittest.TestCase):
    def setUp(self):
        self.stderr = sys.stderr
        sys.stderr = open('/dev/null', 'w')
        
    def tearDown(self):
        sys.stderr = sys.stderr

    def _assertChain(self, target, chains, maxValue):\
        self.assertEqual(target, [list(chains.getIndexGenerator(val)) for val in range( maxValue )])
    
    def _doChainsTest(self, target, valList, maxValue):
        fn = os.tempnam()
        path, prefix = os.path.dirname(fn), os.path.basename(fn)
        
        chains = SameValueIndexChainsFactory().generate(valList, len(valList), maxValue, path, prefix)
        self._assertChain(target, chains, maxValue)        

        chains = SameValueIndexChainsFactory().load(path, prefix)
        self._assertChain(target, chains, maxValue)        
        
        removeFile(fn + '.chains')
        removeFile(fn + '.starts')
    
    def testChains(self):
        #self._doChainsTest( [[],[]], [], 2 ) # Assertion error
        self._doChainsTest( [[0,2],[1],[],[3]], [0,1,0,3], 4 )
        self._doChainsTest( [[0,2,4],[1],[],[3]], [0,1,0,3,0], 4 )
        self._doChainsTest( [[0,2],[1],[],[5]], [0,1,0,None,None,3], 4 )
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestSameValueIndexChains().debug()
    unittest.main()
