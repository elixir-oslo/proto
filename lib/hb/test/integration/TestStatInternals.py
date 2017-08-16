#!/usr/bin/env python
import ast
import sys
import unittest
from test.integration.GalaxyIntegrationTest import GalaxyIntegrationTest
from test.integration.ProfiledIntegrationTest import ProfiledIntegrationTest

class TestStatInternals(GalaxyIntegrationTest):
    def testTrackFormatMerging(self):
        self._assertBatchEqual([[[('Result', [119121])], [('Result', [0])]]],\
           ['TestGenome|chr21:10000001-11000000|500000|segsMany|ZipperStat(statClassList=CountStat)'])
        
        self._assertBatchEqual([[[('Result', [447,447])], [('Result', [0,0])]]],\
           ['TestGenome|chr21:10000001-11000000|500000|segsMany|ZipperStat(statClassList=CountStat^CountPointStat)'])
        
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestStatInternals().run()
    #TestStatInternals().debug()
    if len(sys.argv) == 2:
        TestStatInternals.VERBOSE = ast.literal_eval(sys.argv[1])
        sys.argv = sys.argv[:-1]
    unittest.main()
