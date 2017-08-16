# NB: TrackFormat == TrackFormat is not tested

import unittest
import numpy as np
from collections import OrderedDict
from gold.graph.GraphView import GraphView, LazyProtoGraphView
from gold.graph.Edge import Edge
from test.gold.track.common.SampleTrackView import SampleTV
from test.util.Asserts import TestCaseWithImprovedAsserts

class TestGraphView(TestCaseWithImprovedAsserts):
    def setUp(self):
        self.emptyTv = SampleTV(starts=[], ids=[], edges=[], anchor = [10,100])
        self.emptyPgv = LazyProtoGraphView.createInstanceFromTrackView(self.emptyTv)
        self.emptyGv = self.emptyPgv.getClosedGraphVersion()

        self.emptyWtv = SampleTV(starts=[], ids=[], edges=[], weights=[], anchor = [10,100])
        self.emptyWpgv = LazyProtoGraphView.createInstanceFromTrackView(self.emptyTv)
        self.emptyWgv = self.emptyPgv.getClosedGraphVersion()

        self.tv = SampleTV(starts=[1,2,3,5], ids=list('1235'), edges=[list('236'), list('125'), [], list('26')], anchor = [10,100])
        self.pgv = LazyProtoGraphView.createInstanceFromTrackView(self.tv)
        self.gv = self.pgv.getClosedGraphVersion()

        self.wtv = SampleTV(starts=[1,2,3,5], ids=list('1235'), edges=[list('236'), list('125'), [], list('26')], weights=[[1,2,3],[4,5,6],[],[7.,8.]], anchor = [10,100])
        self.wpgv = LazyProtoGraphView.createInstanceFromTrackView(self.wtv)
        self.wgv = self.wpgv.getClosedGraphVersion()

        self.uwtv = SampleTV(starts=[1,2,3,5], ids=list('1235'), edges=[list('256'), list('15'), [], list('126')], weights=[[1,2,3],[1,4],[],[2,4,5]], anchor = [10,100])
        self.uwpgv = LazyProtoGraphView.createInstanceFromTrackView(self.uwtv, isDirected=False)
        self.uwgv = self.uwpgv.getClosedGraphVersion()
        
        #undirected weighted trackView/protographView/graphView with nan-values
        self.uwtvwn = SampleTV(starts=[1,2,3,5], ids=list('1235'), edges=[list('256'), list('15'), [], list('126')], weights=[[1,2,np.nan],[1,4,],[],[2,4,np.nan]], anchor = [10,100])
        self.uwpgvwn = LazyProtoGraphView.createInstanceFromTrackView(self.uwtvwn, isDirected=False)
        self.uwgvwn = self.uwpgvwn.getClosedGraphVersion()
        
        #small undirected weighted 
        self.small_uwtv = SampleTV(starts=[1,2,3], ids=list('123'), edges=[list('123')]*3, weights=[[4,np.nan,9],[np.nan,20,5],[9, 5, 0]], anchor = [10,100])        
        self.small_uwpgv = LazyProtoGraphView.createInstanceFromTrackView(self.small_uwtv, isDirected=False)
        self.small_uwgv = self.small_uwpgv.getClosedGraphVersion()
        
        #undirected/symmetrical complete graph, with loops:
        self.ucgtv_weights = [[0, 3, 9, 5], [3, 0, 9, 1], [9, 9, 0, 3], [5, 1, 3, 0]]
        self.ucgtv = SampleTV(starts=[1,2,3,4], ids=list('1234'), edges=[list('1234')]*4, weights=self.ucgtv_weights, anchor = [10,100])
        self.ucgpgv = LazyProtoGraphView.createInstanceFromTrackView(self.ucgtv, isDirected=False)
        self.ucgv = self.ucgpgv.getClosedGraphVersion()
        
        #two protoGraphs combined into a graphView:
        """
        TODO: make this work! Right now SampleTV does not allow edges to nodes ouside the trackview, although ProtoGraph does.
        self.both_protographs_weights = [[0, 3, 9, 5], [3, 0, 9, 1], [9, 9, 0, 3], [5, 1, 3, 0]]
        self.protograph1_tv = SampleTV(starts=[1,2,3,4], ids=list('1234'), edges=[list('1234')]*4, weights=self.both_protographs_weights, anchor=[10,100])
        self.protograph2_tv = SampleTV(starts=[1,2,3,4], ids=list('1234'), edges=[list('1234')]*4, weights=self.both_protographs_weights, anchor=[10,100])
        self.protograph1_pg = LazyProtoGraphView.createInstanceFromTrackView(self.protograph1_tv, isDirected=False)
        self.protograph2_pg = LazyProtoGraphView.createInstanceFromTrackView(self.protograph2_tv, isDirected=False)
        self.pg_1_and_2_combined_pg = LazyProtoGraphView.mergeProtoGraphViews([self.protograph1_pg, self.protograph2_pg])
        self.combined_protographs = self.pg_1_and_2_combined_pg.getClosedGraphVersion()
        """


        
        
    def testNodeAccessAndIteration(self):
        self.assertRaises( KeyError, self.emptyGv.getNode, '3' )
        nodes = set( self.emptyGv.getNodeIter() )
        self.assertEqual( set(), nodes )
    
        self.assertEqual( self.gv.getNode('3').id(), '3')    
        nodes = set( self.gv.getNodeIter() )
        self.assertEqual( set([n.id() for n in nodes]), set(list('1235')) )
        
    def test_find_indices_of_elements_in_array(self):
        self.assertListsOrDicts(GraphView._find_indices_of_elements_in_array
                                    (np.array([1,9]), #elements
                                    np.array([0,1,2,3,4,5,6,7,8,9])), #array
                                np.array([1,9])) #correct answer
        self.assertListsOrDicts(GraphView._find_indices_of_elements_in_array
                                    (np.array([100,200]), #elements
                                    np.array([0,1,2,3,4,5,6,7,8,9])), #array
                                np.array([])) #correct answer
        self.assertListsOrDicts(GraphView._find_indices_of_elements_in_array
                                    (np.array([70]), #elements
                                    np.array([0,1,2,3,70,5,6,7,8,9])), #array
                                np.array([4])) #correct answer
        

    def testGetMatrixFromCompleteSubGraph(self):
        indices = np.array([0, 3])
        matrix = np.array([[0, 3, 9, 5], [3, 0, 9, 1], [9, 9, 0, 3], [5, 1, 3, 0]])
        correct = np.array([[0,5],[5,0]])
        res = GraphView.getMatrixFromCompleteSubGraph(indices, matrix)
        self.assertListsOrDicts(res, correct)
        
    def testEdgeIteration(self):
        edges = set( self.emptyGv.getEdgeIter() )
        self.assertEqual( edges, set() )

        #test edges on unweighted graph
        n1, n2, n3, n5 = [self.gv.getNode(i) for i in list('1235')]
        edges = set(self.gv.getEdgeIter())
        self.assertEqual( edges, set([Edge(n1,n2), Edge(n1,n3), Edge(n2,n1), Edge(n2,n2), Edge(n2,n5), Edge(n5,n2)]) )

        #test edges on weighted graph    
        n1, n2, n3, n5 = [self.wgv.getNode(i) for i in list('1235')]
        edges = set(self.wgv.getEdgeIter())
        answerEdges = set([ Edge(n1,n2,1), Edge(n1,n3,2), Edge(n2,n1,4), Edge(n2,n2,5), Edge(n2,n5,6), Edge(n5,n2,7) ])
        #self.assertEqual( [str(x) for x in edges], [str(x) for x in answerEdges])
        self.assertEqual( edges, answerEdges)
        
        #test edges on undirected weighted graph
        n1, n2, n3, n5 = [self.uwgv.getNode(i) for i in list('1235')]
        edges = set(self.uwgv.getEdgeIter())
        answerEdges = set([ Edge(n1,n2,1,directed=False), Edge(n1,n5,2,directed=False), Edge(n2,n5,4,directed=False) ])
        #self.assertEqual( set([str(x) for x in edges]), set([str(x) for x in answerEdges]))
        self.assertEqual(edges, answerEdges)

    def testNodeNeighborIteration(self):
        n1, n2, n3, n5 = [self.gv.getNode(i) for i in list('1235')]
        #basic neighbor list
        self.assertEqual( set(n2.getNeighborIter()), set([Edge(n2,n1,None), Edge(n2,n2,None), Edge(n2,n5,None)]))

        n1, n2, n3, n5 = [self.wgv.getNode(i) for i in list('1235')]
        #basic neighbor list with weights
        self.assertEqual( set(n2.getNeighborIter()), set([Edge(n2,n1,4), Edge(n2,n2,5), Edge(n2,n5,6)]))
        
        #assert that edges to nodes outside graph gets pruned away (in lazy manner)
        self.assertEqual( set(n1.getNeighborIter()),  set([Edge(n1,n2,1), Edge(n1,n3,2)]) )
        
    def testGetNewSubGraphFromNodeIdSet(self):
        subGv = self.emptyWgv.getNewSubGraphFromNodeIdSet([])
        self.assertEqual( set(subGv.getNodeIter()), set() )
    
        subGv = self.wgv.getNewSubGraphFromNodeIdSet(list('235'))
        self.assertEqual( set([n.id() for n in subGv.getNodeIter()]), set(list('235')) )

        n2, n3, n5 = [subGv.getNode(i) for i in list('235')]
        edges = set(subGv.getEdgeIter())
        answerEdges = set([Edge(n2,n2,5), Edge(n2,n5,6), Edge(n5,n2,7), ])
        #self.assertEqual( [str(x) for x in edges], [str(x) for x in answerEdges])
        self.assertEqual( edges, answerEdges )
        
    def testGetBinaryMatrixRepresentation(self):
        self.assertListsOrDicts(OrderedDict([('Rows', np.array([], dtype='S')), \
                                             ('Cols', np.array([], dtype='S')), \
                                             ('Matrix', np.array([], dtype='bool8'))]), \
                                self.emptyWgv.getBinaryMatrixRepresentation())
        
        self.assertListsOrDicts(OrderedDict([('Rows', np.array([], dtype='S')), \
                                             ('Cols', np.array([], dtype='S')), \
                                             ('Matrix', np.array([], dtype='bool8'))]), \
                                self.emptyWgv.getBinaryMatrixRepresentation(rowsAsFromNodes=False))
        
        self.assertListsOrDicts(OrderedDict([('Rows', np.array([], dtype='S')), \
                                             ('Cols', np.array([], dtype='S')), \
                                             ('Matrix', np.array([], dtype='bool8'))]), \
                                self.emptyWgv.getBinaryMatrixRepresentation(completeMatrix=True))
        
        self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('125'))), \
                                             ('Cols', np.array(list('1235'))), \
                                             ('Matrix', np.array([[0,1,1,0], [1,1,0,1], [0,1,0,0]], dtype='bool8'))]), \
                                self.wgv.getBinaryMatrixRepresentation())

        self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('1235'))), \
                                             ('Cols', np.array(list('125'))), \
                                             ('Matrix', np.array([[0,1,0], [1,1,1], [1,0,0], [0,1,0]], dtype='bool8'))]), \
                                self.wgv.getBinaryMatrixRepresentation(rowsAsFromNodes=False))
        
        self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('1235'))), \
                                             ('Cols', np.array(list('1235'))), \
                                             ('Matrix', np.array([[0,1,1,0], [1,1,0,1], [0,0,0,0], [0,1,0,0]], dtype='bool8'))]), \
                                self.wgv.getBinaryMatrixRepresentation(completeMatrix=True))

        self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('1235'))), \
                                             ('Cols', np.array(list('1235'))), \
                                             ('Matrix', np.array([[0,1,0,0], [1,1,0,1], [1,0,0,0], [0,1,0,0]], dtype='bool8'))]), \
                                self.wgv.getBinaryMatrixRepresentation(completeMatrix=True, rowsAsFromNodes=False))
    
        
    def testGetEdgeWeightMatrixRepresentation(self):
        self.assertListsOrDicts(OrderedDict([('Rows', np.array([], dtype='S')), \
                                             ('Cols', np.array([], dtype='S')), \
                                             ('Matrix', np.array([], dtype='float64'))]), \
                                self.emptyWgv.getEdgeWeightMatrixRepresentation())
        
        self.assertListsOrDicts(OrderedDict([('Rows', np.array([], dtype='S')), \
                                             ('Cols', np.array([], dtype='S')), \
                                             ('Matrix', np.array([], dtype='float64'))]), \
                                self.emptyWgv.getEdgeWeightMatrixRepresentation(rowsAsFromNodes=False))
        
        self.assertListsOrDicts(OrderedDict([('Rows', np.array([], dtype='S')), \
                                             ('Cols', np.array([], dtype='S')), \
                                             ('Matrix', np.array([], dtype='float64'))]), \
                                self.emptyWgv.getEdgeWeightMatrixRepresentation(completeMatrix=True))
        
        self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('125'))), \
                                             ('Cols', np.array(list('1235'))), \
                                             ('Matrix', np.array([[0,1,2,0], [4,5,0,6], [0,7,0,0]], dtype='float64'))]), \
                                self.wgv.getEdgeWeightMatrixRepresentation())

        self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('1235'))), \
                                             ('Cols', np.array(list('125'))), \
                                             ('Matrix', np.array([[0,4,0], [1,5,7], [2,0,0], [0,6,0]], dtype='float64'))]), \
                                self.wgv.getEdgeWeightMatrixRepresentation(rowsAsFromNodes=False))
        
        self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('1235'))), \
                                             ('Cols', np.array(list('1235'))), \
                                             ('Matrix', np.array([[0,1,2,0], [4,5,0,6], [0,0,0,0], [0,7,0,0]], dtype='float64'))]), \
                                self.wgv.getEdgeWeightMatrixRepresentation(completeMatrix=True))

        self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('1235'))), \
                                             ('Cols', np.array(list('1235'))), \
                                             ('Matrix', np.array([[np.nan,4,np.nan,np.nan], [1,5,np.nan,7], \
                                                                  [2,np.nan,np.nan,np.nan], [np.nan,6,np.nan,np.nan]], dtype='float64'))]), \
                                self.wgv.getEdgeWeightMatrixRepresentation(completeMatrix=True, rowsAsFromNodes=False, missingEdgeWeight=np.nan))

    
    def testGetSumOfWeightsInGraph(self):
        self.assertEqual( self.emptyGv.getSumOfWeightsInGraph(),  0.)
        self.assertEqual( self.emptyWgv.getSumOfWeightsInGraph(), 0.)
        self.assertEqual( self.gv.getSumOfWeightsInGraph(), 0.)
        #TODO: now, we assume the result of getSumOfWeightsInGraphUsingEdgeIter is correct. Create tests comparing
        # the result to pre-defined result as well by calculating it manually
        self.assertEqual( self.wgv.getSumOfWeightsInGraph(), self.wgv.getSumOfWeightsInGraphUsingEdgeIter())
        self.wgv_filtered = self.wgv.getNewSubGraphFromNodeIdSet(['1','2'])
        self.assertEqual( self.wgv_filtered.getSumOfWeightsInGraph(), self.wgv_filtered.getSumOfWeightsInGraphUsingEdgeIter())
        self.assertEqual( self.uwgv.getSumOfWeightsInGraph(), self.uwgv.getSumOfWeightsInGraphUsingEdgeIter())
        self.uwgv_filtered = self.uwgv.getNewSubGraphFromNodeIdSet(['1','2'])
        self.assertEqual( self.uwgv_filtered.getSumOfWeightsInGraph(), self.uwgv_filtered.getSumOfWeightsInGraphUsingEdgeIter())
        self.uwgv_filtered2 = self.uwgv.getNewSubGraphFromNodeIdSet(['3'])
        self.assertEqual( self.uwgv_filtered2.getSumOfWeightsInGraph(), self.uwgv_filtered2.getSumOfWeightsInGraphUsingEdgeIter())
        self.uwgv_filtered3 = self.uwgv.getNewSubGraphFromNodeIdSet(['1','2','3','5'])
        self.assertEqual( self.uwgv_filtered3.getSumOfWeightsInGraph(), self.uwgv_filtered3.getSumOfWeightsInGraphUsingEdgeIter())
        #Testing with nan-values as weights
        self.assertEqual( self.uwgvwn.getSumOfWeightsInGraph(), 7. )
        self.assertEqual( self.small_uwgv.getSumOfWeightsInGraph(allowLoops=False), 14. )
        self.small_uwgv_filtered = self.small_uwgv.getNewSubGraphFromNodeIdSet(['1','3'])
        self.assertEqual( self.small_uwgv_filtered.getSumOfWeightsInGraph(allowLoops=False), 9.)
        
        
    def testGetMeanOfWeightsInGraph(self):
        self.assertEqual( self.emptyGv.getMeanOfWeightsInGraph(), np.nan)
        self.assertEqual( self.emptyWgv.getMeanOfWeightsInGraph(), np.nan)
        self.assertEqual( self.gv.getMeanOfWeightsInGraph(), np.nan)
        #self.assertEqual( self.wgv.getMeanOfWeightsInGraph(), )

    def testGetMatrixAndIdsFromCompleteGraph(self):
        res = self.ucgv.getMatrixAndIdsFromCompleteGraph()
        correct_matrix = np.array(self.ucgtv_weights, dtype="float64")
        correct_ids = {'1': 0, '2': 1, '3': 2, '4': 3}
        self.assertListsOrDicts(res["matrix"], correct_matrix)
        self.assertListsOrDicts(res["ids"], correct_ids)
        
    def testGetMatrixFromCompleteGraph(self):
        res = self.ucgv.getMatrixFromCompleteGraph()
        correct = np.array(self.ucgtv_weights, dtype="float64")
        self.assertListsOrDicts(res, correct)
        
        #from a subgraph:
        ucgv_subgraph = self.ucgv.getNewSubGraphFromNodeIdSet(['1','4'])
        res = ucgv_subgraph.getMatrixFromCompleteGraph()
        correct = np.array([[0, 5], [5, 0]], dtype="float64")
        self.assertListsOrDicts(res, correct)
        
        #from another subgraph
        ucgv_subgraph2 = self.ucgv.getNewSubGraphFromNodeIdSet(['2', '3', '4'])
        res = ucgv_subgraph2.getMatrixFromCompleteGraph()
        correct = np.array([[0, 9, 1], [9, 0, 3],[1, 3, 0]], dtype="float64")
        self.assertListsOrDicts(res, correct)
        
        #combining two protographs:
        '''
        As soon as the protograph in setUp works, enable this test:
        res = self.combined_protographs.getMatrixFromCompleteGraph()
        correct = np.array(self.both_protographs_weights, dtype="float64")
        self.assertListsOrDicts(res, correct)
        '''

        
class TestProtoGraphView(unittest.TestCase):
    def setUp(self):
        self.emptyTv = SampleTV(starts=[], ids=[], edges=[], anchor = [10,100])
        self.emptyPgv = LazyProtoGraphView.createInstanceFromTrackView(self.emptyTv)

        self.emptyTv2 = SampleTV(starts=[], ids=[], edges=[], anchor = [100,200])
        self.emptyPgv2 = LazyProtoGraphView.createInstanceFromTrackView(self.emptyTv2)
        
        self.tv = SampleTV(starts=[1,2,3,5], ids=list('1235'), edges=[list('236'), list('125'), [], list('26')], anchor = [10,100])
        self.pgv = LazyProtoGraphView.createInstanceFromTrackView(self.tv)

        self.tv2 = SampleTV(starts=[0,99], ids=list('69'), edges=[list('3'), list('6')], anchor = [100,200])
        self.pgv2 = LazyProtoGraphView.createInstanceFromTrackView(self.tv2)

    def testCreateInstanceFromTrackView(self):
        self.assertEqual( self.emptyPgv._id2index, {} )
        self.assertEqual( self.emptyPgv._isDirected, True)
        self.assertEqual( self.emptyPgv._id2nodes, {})
        
        greg = self.tv.genomeAnchor
        self.assertEqual( self.pgv._id2index, {'1':(greg,0), '2':(greg,1), '3':(greg,2), '5':(greg,3)} )
        self.assertEqual( self.pgv._isDirected, True)
        self.assertEqual( self.pgv._id2nodes, {})
        
    def testMergeProtoGraphViews(self):
        #Merging a single pgv, should give same result as the single pgv itself
        
        combinedPgv = LazyProtoGraphView.mergeProtoGraphViews([self.emptyPgv])
        self.assertEqual( combinedPgv._id2index, self.emptyPgv._id2index )
        
        combinedPgv = LazyProtoGraphView.mergeProtoGraphViews([self.pgv])
        self.assertEqual( combinedPgv._id2index, self.pgv._id2index )   

        #Merging two pgvs
        
        combinedPgv = LazyProtoGraphView.mergeProtoGraphViews([self.emptyPgv, self.emptyPgv2])
        self.assertEqual( combinedPgv._id2index,  {} )
        
        greg = self.tv.genomeAnchor
        greg2 = self.tv2.genomeAnchor
        combinedPgv = LazyProtoGraphView.mergeProtoGraphViews([self.pgv, self.pgv2])
        self.assertEqual( combinedPgv._id2index,  {'1':(greg,0), '2':(greg,1), '3':(greg,2), '5':(greg,3), '6':(greg2,0), '9':(greg2,1)} )
        
    
if __name__ == "__main__":
    unittest.main()
