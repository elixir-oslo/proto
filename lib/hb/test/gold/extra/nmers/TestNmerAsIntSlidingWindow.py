import unittest
from gold.extra.nmers.NmerAsIntSlidingWindow import NmerAsIntSlidingWindow

class TestNmerAsIntSlidingWindow(unittest.TestCase):
    def setUp(self):
        pass
    
    def testIter(self):
        self.assertEqual([], list(NmerAsIntSlidingWindow(2,'')) )
        self.assertEqual([], list(NmerAsIntSlidingWindow(2,'n')) )
        self.assertEqual([], list(NmerAsIntSlidingWindow(2,'a')) )
        self.assertEqual([1,6,11,12,None,None,4], list(NmerAsIntSlidingWindow(2,'acGtaNca')) )
        self.assertEqual([6,27], list(NmerAsIntSlidingWindow(3,'acGt')) )
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    unittest.main()
