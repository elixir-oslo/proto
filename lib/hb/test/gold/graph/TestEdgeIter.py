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

        self.wtv = SampleTV(starts=[1,2,3,5], ids=list('1235'), edges=[list('236'), list('125'), [], list('26')], weights=[[1,2,3],[4,5,6],[],[7,8]], anchor = [10,100])
        self.wpgv = LazyProtoGraphView.createInstanceFromTrackView(self.wtv)
        self.wgv = self.wpgv.getClosedGraphVersion()

        self.uwtv = SampleTV(starts=[1,2,3,5], ids=list('1235'), edges=[list('256'), list('15'), [], list('126')], weights=[[1,2,3],[1,4],[],[2,4,5]], anchor = [10,100])
        self.uwpgv = LazyProtoGraphView.createInstanceFromTrackView(self.uwtv, isDirected=False)
        self.uwgv = self.uwpgv.getClosedGraphVersion()
        
    
    #def testEdgeIteration(self):
    #    edges = set( self.emptyGv.getEdgeIter() )
    #    self.assertEqual( edges, set() )
    #
    #    #test edges on unweighted graph
    #    n1, n2, n3, n5 = [self.gv.getNode(i) for i in list('1235')]
    #    edges = set(self.gv.getEdgeIter())
    #    self.assertEqual( edges, set([Edge(n1,n2), Edge(n1,n3), Edge(n2,n1), Edge(n2,n2), Edge(n2,n5), Edge(n5,n2)]) )
    #
    #    #test edges on weighted graph    
    #    n1, n2, n3, n5 = [self.wgv.getNode(i) for i in list('1235')]
    #    edges = set(self.wgv.getEdgeIter())
    #    answerEdges = set([ Edge(n1,n2,1), Edge(n1,n3,2), Edge(n2,n1,4), Edge(n2,n2,5), Edge(n2,n5,6), Edge(n5,n2,7) ])
    #    #self.assertEqual( [str(x) for x in edges], [str(x) for x in answerEdges])
    #    self.assertEqual( edges, answerEdges)
        
        #test edges on undirected weighted graph
        #n1, n2, n3, n5 = [self.uwgv.getNode(i) for i in list('1235')]
        #edges = set(self.uwgv.getEdgeIter())
        #answerEdges = set([ Edge(n1,n2,1), Edge(n1,n5,2), Edge(n2,n5,4) ])
        #self.assertEqual( [str(x) for x in edges], [str(x) for x in answerEdges])
        #self.assertEqual( edges, answerEdges)

    #    
    #def testGetBinaryMatrixRepresentation(self):
    #    self.assertListsOrDicts(OrderedDict([('Rows', np.array([], dtype='S')), \
    #                                         ('Cols', np.array([], dtype='S')), \
    #                                         ('Matrix', np.array([], dtype='bool8'))]), \
    #                            self.emptyWgv.getBinaryMatrixRepresentation())
    #    
    #    self.assertListsOrDicts(OrderedDict([('Rows', np.array([], dtype='S')), \
    #                                         ('Cols', np.array([], dtype='S')), \
    #                                         ('Matrix', np.array([], dtype='bool8'))]), \
    #                            self.emptyWgv.getBinaryMatrixRepresentation(rowsAsFromNodes=False))
    #    
    #    self.assertListsOrDicts(OrderedDict([('Rows', np.array([], dtype='S')), \
    #                                         ('Cols', np.array([], dtype='S')), \
    #                                         ('Matrix', np.array([], dtype='bool8'))]), \
    #                            self.emptyWgv.getBinaryMatrixRepresentation(completeMatrix=True))
    #    
    #    self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('125'))), \
    #                                         ('Cols', np.array(list('1235'))), \
    #                                         ('Matrix', np.array([[0,1,1,0], [1,1,0,1], [0,1,0,0]], dtype='bool8'))]), \
    #                            self.wgv.getBinaryMatrixRepresentation())
    #
    #    self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('1235'))), \
    #                                         ('Cols', np.array(list('125'))), \
    #                                         ('Matrix', np.array([[0,1,0], [1,1,1], [1,0,0], [0,1,0]], dtype='bool8'))]), \
    #                            self.wgv.getBinaryMatrixRepresentation(rowsAsFromNodes=False))
    #    
    #    self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('1235'))), \
    #                                         ('Cols', np.array(list('1235'))), \
    #                                         ('Matrix', np.array([[0,1,1,0], [1,1,0,1], [0,0,0,0], [0,1,0,0]], dtype='bool8'))]), \
    #                            self.wgv.getBinaryMatrixRepresentation(completeMatrix=True))
    #
    #    self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('1235'))), \
    #                                         ('Cols', np.array(list('1235'))), \
    #                                         ('Matrix', np.array([[0,1,0,0], [1,1,0,1], [1,0,0,0], [0,1,0,0]], dtype='bool8'))]), \
    #                            self.wgv.getBinaryMatrixRepresentation(completeMatrix=True, rowsAsFromNodes=False))
    #    
    #def testGetEdgeWeightMatrixRepresentation(self):
    #    self.assertListsOrDicts(OrderedDict([('Rows', np.array([], dtype='S')), \
    #                                         ('Cols', np.array([], dtype='S')), \
    #                                         ('Matrix', np.array([], dtype='float64'))]), \
    #                            self.emptyWgv.getEdgeWeightMatrixRepresentation())
    #    
    #    self.assertListsOrDicts(OrderedDict([('Rows', np.array([], dtype='S')), \
    #                                         ('Cols', np.array([], dtype='S')), \
    #                                         ('Matrix', np.array([], dtype='float64'))]), \
    #                            self.emptyWgv.getEdgeWeightMatrixRepresentation(rowsAsFromNodes=False))
    #    
    #    self.assertListsOrDicts(OrderedDict([('Rows', np.array([], dtype='S')), \
    #                                         ('Cols', np.array([], dtype='S')), \
    #                                         ('Matrix', np.array([], dtype='float64'))]), \
    #                            self.emptyWgv.getEdgeWeightMatrixRepresentation(completeMatrix=True))
    #    
    #    self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('125'))), \
    #                                         ('Cols', np.array(list('1235'))), \
    #                                         ('Matrix', np.array([[0,1,2,0], [4,5,0,6], [0,7,0,0]], dtype='float64'))]), \
    #                            self.wgv.getEdgeWeightMatrixRepresentation())
    #
    #    self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('1235'))), \
    #                                         ('Cols', np.array(list('125'))), \
    #                                         ('Matrix', np.array([[0,4,0], [1,5,7], [2,0,0], [0,6,0]], dtype='float64'))]), \
    #                            self.wgv.getEdgeWeightMatrixRepresentation(rowsAsFromNodes=False))
    #    
    #    self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('1235'))), \
    #                                         ('Cols', np.array(list('1235'))), \
    #                                         ('Matrix', np.array([[0,1,2,0], [4,5,0,6], [0,0,0,0], [0,7,0,0]], dtype='float64'))]), \
    #                            self.wgv.getEdgeWeightMatrixRepresentation(completeMatrix=True))
    #
    #    self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('1235'))), \
    #                                         ('Cols', np.array(list('1235'))), \
    #                                         ('Matrix', np.array([[np.nan,4,np.nan,np.nan], [1,5,np.nan,7], \
    #                                                              [2,np.nan,np.nan,np.nan], [np.nan,6,np.nan,np.nan]], dtype='float64'))]), \
    #                            self.wgv.getEdgeWeightMatrixRepresentation(completeMatrix=True, rowsAsFromNodes=False, missingEdgeWeight=np.nan))
    #    
    def testGetEdgeWeightMatrixRepresentationOptimized(self):
        print "Testing GetEdgeWeightMatrixRepresentationOptimized:"
        self.assertListsOrDicts(OrderedDict([('Rows', np.array([], dtype='S')), \
                                             ('Cols', np.array([], dtype='S')), \
                                             ('Matrix', np.array([], dtype='float64'))]), \
                                self.emptyWgv.getEdgeWeightMatrixRepresentationOptimized())
        
        self.assertListsOrDicts(OrderedDict([('Rows', np.array([], dtype='S')), \
                                             ('Cols', np.array([], dtype='S')), \
                                             ('Matrix', np.array([], dtype='float64'))]), \
                                self.emptyWgv.getEdgeWeightMatrixRepresentationOptimized(rowsAsFromNodes=False))
        
        self.assertListsOrDicts(OrderedDict([('Rows', np.array([], dtype='S')), \
                                             ('Cols', np.array([], dtype='S')), \
                                             ('Matrix', np.array([], dtype='float64'))]), \
                                self.emptyWgv.getEdgeWeightMatrixRepresentationOptimized(completeMatrix=True))
        
        self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('125'))), \
                                             ('Cols', np.array(list('1235'))), \
                                             ('Matrix', np.array([[0,1,2,0], [4,5,0,6], [0,7,0,0]], dtype='float64'))]), \
                                self.wgv.getEdgeWeightMatrixRepresentationOptimized())

        self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('1235'))), \
                                             ('Cols', np.array(list('125'))), \
                                             ('Matrix', np.array([[0,4,0], [1,5,7], [2,0,0], [0,6,0]], dtype='float64'))]), \
                                self.wgv.getEdgeWeightMatrixRepresentationOptimized(rowsAsFromNodes=False))
        
        self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('1235'))), \
                                             ('Cols', np.array(list('1235'))), \
                                             ('Matrix', np.array([[0,1,2,0], [4,5,0,6], [0,0,0,0], [0,7,0,0]], dtype='float64'))]), \
                                self.wgv.getEdgeWeightMatrixRepresentationOptimized(completeMatrix=True))

        self.assertListsOrDicts(OrderedDict([('Rows', np.array(list('1235'))), \
                                             ('Cols', np.array(list('1235'))), \
                                             ('Matrix', np.array([[np.nan,4,np.nan,np.nan], [1,5,np.nan,7], \
                                                                  [2,np.nan,np.nan,np.nan], [np.nan,6,np.nan,np.nan]], dtype='float64'))]), \
                                self.wgv.getEdgeWeightMatrixRepresentationOptimized(completeMatrix=True, rowsAsFromNodes=False, missingEdgeWeight=np.nan))
        
        
if __name__ == "__main__":
    unittest.main()
