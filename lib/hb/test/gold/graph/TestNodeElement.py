# NB: TrackFormat == TrackFormat is not tested

import unittest
from gold.graph.NodeElement import NodeElement
from test.gold.track.common.SampleTrackView import SampleTV

class TestNodeElement(unittest.TestCase):
    def setUp(self):
        pass

    def testNeighborTraversing(self):
        tv = SampleTV(starts=[1,2,3,5], ids=list('1234'), edges=[list('23'), list('14'), list('1'), list('2')])
        raise Exception   
        #graphView = 
        n = NodeElement(tv, 0, graphView)
        #e = Edge()
    
if __name__ == "__main__":
    unittest.main()
