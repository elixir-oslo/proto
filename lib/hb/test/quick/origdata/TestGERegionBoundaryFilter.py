import unittest
from quick.origdata.GERegionBoundaryFilter import GERegionBoundaryFilter
from quick.application.UserBinSource import GlobalBinSource
from test.gold.origdata.common.Asserts import assertDecorator
from functools import partial

class TestGERegionBoundaryFilter(unittest.TestCase):
    def setUp(self):
        pass    
    
    def _assertFilter(self, filteredList, unfilteredList):
        assertDecorator(partial(GERegionBoundaryFilter, regionBoundaryIter=GlobalBinSource('TestGenome')), \
                                self.assertEqual, filteredList, unfilteredList)
    
    def testFilter(self):
        self._assertFilter([['TestGenome','chr21',2,5],['TestGenome','chrM',3,8]], [['TestGenome','chr21',2,5],['TestGenome','chrM',3,8]])
        self._assertFilter([['TestGenome','chrM',3,8]], [['Test','chr21',2,5],['TestGenome','chrM',3,8]])
        self._assertFilter([['TestGenome','chr21',2,5]], [['TestGenome','chr21',2,5],['TestGenome','chrTest',3,8]])
        self._assertFilter([['TestGenome','chrM',3,8]], [['TestGenome','chr21',-2,5],['TestGenome','chrM',3,8]])
        
if __name__ == "__main__":
    unittest.main()
