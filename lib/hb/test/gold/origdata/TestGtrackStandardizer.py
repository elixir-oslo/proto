import unittest
from tempfile import NamedTemporaryFile

from gold.origdata.GtrackStandardizer import standardizeGtrackFileAndReturnContents
from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
from gold.track.TrackFormat import TrackFormat
from test.gold.origdata.common.TestWithGeSourceData import TestWithGeSourceData
from test.util.Asserts import TestCaseWithImprovedAsserts

class TestGtrackStandardizer(TestWithGeSourceData, TestCaseWithImprovedAsserts):
    GENOME = 'TestGenome'
    TRACK_NAME_PREFIX = ['TestGenomeElementSource']
        
    def setUp(self):
        pass
    
    def testStandardizing(self):
        geSourceTest = self._commonSetup()
        
        for caseName in geSourceTest.cases:
            if not caseName.startswith('gtrack'):
                continue
                
            if 'no_standard' in caseName:
                print 'Test case skipped: ' + caseName
                continue
                
            print caseName
            print
            
            case = geSourceTest.cases[caseName]
            testFn = self._writeTestFile(case)
            print open(testFn).read()
            print
            
            stdContents = standardizeGtrackFileAndReturnContents(testFn, case.genome)
            print stdContents

            self.assertTrue('##track type: linked valued segments' in stdContents)
            self.assertTrue('\t'.join(['###seqid', 'start', 'end', 'value', 'strand', 'id', 'edges']) in stdContents)
            
            geSource = GtrackGenomeElementSource('', case.genome, strToUseInsteadOfFn=stdContents)
            for ge in geSource:
                pass
            
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestGtrackSorter().debug()
    unittest.main()
