import unittest
from tempfile import NamedTemporaryFile

from gold.origdata.GenomeElementSource import GenomeElementSource
from gold.origdata.GtrackSorter import UnsortedGtrackGenomeElementSource, sortGtrackFileAndReturnContents
from gold.origdata.GEDependentAttributesHolder import GEDependentAttributesHolder
from gold.track.TrackFormat import TrackFormat
from test.gold.origdata.common.TestWithGeSourceData import TestWithGeSourceData
from test.util.Asserts import TestCaseWithImprovedAsserts

class TestGtrackSorter(TestWithGeSourceData, TestCaseWithImprovedAsserts):
    GENOME = 'TestGenome'
    TRACK_NAME_PREFIX = ['TestGenomeElementSource']
        
    def setUp(self):
        pass
    
    def testSorting(self):
        geSourceTest = self._commonSetup()
        
        for caseName in geSourceTest.cases:
            if not caseName.startswith('gtrack'):
                continue
                
            if 'no_sort' in caseName:
                print 'Test case skipped: ' + caseName
                continue
                
            print caseName
            print
            
            case = geSourceTest.cases[caseName]
            testFn = self._writeTestFile(case)
            print open(testFn).read()
            print
            
            sortedContents = sortGtrackFileAndReturnContents(testFn, case.genome)
            print sortedContents

            sourceClass = GenomeElementSource if case.sourceClass is None else case.sourceClass
            forPreProcessor = True if case.sourceClass is None else False
            sortedGeSource = GEDependentAttributesHolder(sourceClass('sortedFile.gtrack', case.genome, \
                                                                     forPreProcessor=forPreProcessor, \
                                                                     printWarnings=False, \
                                                                     strToUseInsteadOfFn=sortedContents))
            
            
            reprIsDense = TrackFormat.createInstanceFromGeSource(sortedGeSource).reprIsDense()
            
            if not reprIsDense:
                self.assertEquals(sorted(case.assertElementList), [ge for ge in sortedGeSource])
            else:
                for ge in sortedGeSource:
                    pass
            
            self.assertEquals(sorted(case.boundingRegionsAssertList), [br for br in sortedGeSource.getBoundingRegionTuples()])
            
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestGtrackSorter().debug()
    unittest.main()
