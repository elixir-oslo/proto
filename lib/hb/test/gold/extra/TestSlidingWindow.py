import unittest
from gold.extra.SlidingWindow import SlidingWindow
from gold.util.CustomExceptions import NotSupportedError
from test.util.Asserts import AssertList

class TestSlidingWindow(unittest.TestCase):
    def setUp(self):
        pass
    
    def _assertSlide(self, targetWindows, windowSize, source):
        windows = SlidingWindow(source, windowSize)
        self.assertEqual(len(targetWindows), len([el for el in windows]))
        for i, window in enumerate(windows):
            AssertList(targetWindows[i], window, self.assertEqual)
    
    def testSlide(self):
        self._assertSlide([], 3, [])
        self._assertSlide([[0,1],[0,1,2],[1,2,3],[2,3]], 3, range(4))
        self.assertRaises(NotSupportedError, SlidingWindow, [], 4)
    
if __name__ == "__main__":
    unittest.main()
