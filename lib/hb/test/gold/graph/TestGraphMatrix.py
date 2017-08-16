import unittest
import numpy as np
from gold.graph.GraphMatrix import GraphMatrix
from collections import OrderedDict
from gold.graph.GraphView import GraphView, LazyProtoGraphView
from gold.graph.Edge import Edge
from test.gold.track.common.SampleTrackView import SampleTV
from test.util.Asserts import TestCaseWithImprovedAsserts

class TestGraphMatrix(TestCaseWithImprovedAsserts):
    def setUp(self):
        self.tv = SampleTV(starts=[1,2,3,5], ids=list('1235'), edges=[list('236'), list('125'), [], list('26')], anchor = [10,100])
        self.pgv = LazyProtoGraphView.createInstanceFromTrackView(self.tv)
        self.gv = self.pgv.getClosedGraphVersion()

        self.wtv = SampleTV(starts=[1,2,3,5], ids=list('1235'), edges=[list('236'), list('125'), [], list('26')], weights=[[1,2,3],[4,5,6],[],[7.,8.]], anchor = [10,100])
        self.wpgv = LazyProtoGraphView.createInstanceFromTrackView(self.wtv)
        self.wgv = self.wpgv.getClosedGraphVersion()

        #undirected/symmetrical complete graph, with loops:
        self.ucgtv_weights = [[0, 3, 9, 5], [3, 0, 9, 1], [9, 9, 0, 3], [5, 1, 3, 0]]
        self.ucgtv = SampleTV(starts=[1,2,3,4], ids=list('1234'), edges=[list('1234')]*4, weights=self.ucgtv_weights, anchor = [10,100])
        self.ucgpgv = LazyProtoGraphView.createInstanceFromTrackView(self.ucgtv, isDirected=False)
        self.ucgv = self.ucgpgv.getClosedGraphVersion()

    def test__str___(self):
        graphMatrix = GraphMatrix()
        self.assertIsNotNone(str(graphMatrix))

    def test__eq__(self):
        #empty
        gm1 = GraphMatrix()
        gm2 = GraphMatrix()
        self.assertTrue(gm1 == gm2)

        gm3 = GraphMatrix(weights=np.array([[0.0, 3.0],[3.0, 0.0]]), ids={'a':0, 'b': 3})
        self.assertFalse(gm1 == gm3)

        gm4 = GraphMatrix(weights=np.array([[0.0, 3.0],[3.0, 0.0]]), ids={'a':0, 'b': 3})
        self.assertTrue(gm3 == gm4)

        #different ids
        gm5 = GraphMatrix(weights=np.array([[0.0, 3.0],[3.0, 0.0]]), ids={'a':1, 'b': 3})
        self.assertFalse(gm5 == gm4)

        #different weights
        gm6 = GraphMatrix(weights=np.array([[0.0, 3.0],[3.0, 7.0]]), ids={'a':0, 'b': 1})
        self.assertFalse(gm6 == gm5)


        #same values, but at different positions in the matrix:
        gm7 = GraphMatrix(weights=np.array([[9., 3.],[5., 2.]]), ids={'a':0, 'b': 1})
        gm8 = GraphMatrix(weights=np.array([[2., 5.],[3., 9.]]), ids={'a':1, 'b': 0})
        self.assertTrue(gm7 == gm8)

        #different names on ids:
        gm9 = GraphMatrix(weights=np.array([[2., 5.],[3., 9.]]), ids={'a':1, 'c': 0})
        self.assertFalse(gm9 == gm8)

    def test__ne___(self):
        #empty, and equal
        gm1 = GraphMatrix()
        gm2 = GraphMatrix()
        self.assertFalse(gm1 != gm2)

        #empty compared to non-empty
        gm3 = GraphMatrix(weights=np.array([[0.0, 3.0],[3.0, 0.0]]), ids={'a':0, 'b': 3})
        self.assertTrue(gm1 != gm3)

        #two equal graph matrices
        gm4 = GraphMatrix(weights=np.array([[0.0, 3.0],[3.0, 0.0]]), ids={'a':0, 'b': 3})
        self.assertFalse(gm3 != gm4)

        #different ids
        gm5 = GraphMatrix(weights=np.array([[0.0, 3.0],[3.0, 0.0]]), ids={'a':1, 'b': 3})
        self.assertTrue(gm5 != gm4)

        #different weights
        gm6 = GraphMatrix(weights=np.array([[0.0, 3.0],[3.0, 7.0]]), ids={'a':0, 'b': 1})
        self.assertTrue(gm6 != gm5)

    def test_translate(self):
        gm1 = GraphMatrix(weights=np.array([[0.0, 3.0],[3.0, 7.0]]), ids={'a':0, 'b': 1})
        self.assertTrue(gm1._translate(['a', ['a']]) == [0, [0]])
        self.assertTrue(gm1._translate(['a', ['a', ['b']]]) == [0, [0, [1]]])


    def test__getitem__(self):
        #test indexing by a tuple ('a', 'b')
        gm1 = GraphMatrix(weights=np.array([[0.0, 3.0],[9.0, 7.0]]), ids={'a':0, 'b': 1})
        self.assertTrue(gm1['b','b'] == 7.0)
        self.assertTrue(gm1['a', 'b'] == 3.0)

        #test indexing by a list of IDs:
        self.assertTrue((gm1[['a']] == np.array([0.0, 3.0])).all())
        self.assertTrue((gm1[['b']] == np.array([9.0, 7.0])).all())
        self.assertTrue((gm1[['b', 'a']] == np.array([[9.0, 7.0], [0.0, 3.0]])).all())
        self.assertTrue((gm1[['b', ['b']]] == np.array([7.0])).all())




if __name__ == "__main__":
    unittest.main()
