import numpy as np
from collections import OrderedDict
from copy import copy
from gold.graph.NodeElement import NodeElement
from gold.graph.Edge import Edge
from bisect import bisect

class BaseGraphView(object):
    MAX_COORDINATE_MAPPING_CACHE_SIZE = 1e7
    
    def __init__(self, trackViewDict, id2index, isDirected):
        'Typically called with the members of a graphview (typically protoGraphView) object as input, mainly only setting these same member variables'
        self._trackViewDict = trackViewDict
        self._id2index = id2index
        self._id2nodes = {}
        self._isDirected = isDirected
        
        #Caches
        self._cachedCoordinateMappings = {}
        self._cachedSortedNodeStartsAndIds = None
        self._genomeRegion2ids = None
        
class GraphView(BaseGraphView):
    #def __init__(self, graphView,idFilter=None):    
    def hasNode(self, nodeId):
        return nodeId in self._id2index
    
    def filterNodes(self, idFilter):
        if idFilter != None:
            self._id2index = {id:self._id2index[id] for id in idFilter} 
            self._id2nodes = {id:self._id2nodes[id] for id in idFilter if id in self._id2nodes}
            
    def getNewSubGraphFromNodeIdSet(self, nodeIds):
        """
        Returns a GraphView object corresponding to the nodes provided in nodeIds, with edges between these nodes.
        The underlying numpy arrays are not copied, but the _id2index will be filtered by nodeIds. 
        """
        subGraph = GraphView(self._trackViewDict, self._id2index, self._isDirected)
        subGraph.filterNodes(nodeIds)
        return subGraph
    
    def applyFunctionToWeightsInGraph(self, functionToApply, allowLoops=True, isDirected=None):
        """
        functionToApply: the function to apply to a matrix consiting of all the weights in this graph.
        allowLoops: if True, then looping edges are counted. Otherwise they are ignored.
        isDirected: if True we assume the weight of node1->node2 is the same as
                    the weight of node2->node1, and we only count one of these weights. If no value is given,
                    self.isDirected() is used.
        """
        if isDirected == None:
            isDirected = self.isDirected()
        #node_ids is a list of all nodes that are interesting 
        node_ids = self._id2index.keys()
        #the reason for sorting has to do with the way the datasets have been stored:
        # for inter-edges the edge is only stored in the first chromosome, so it is
        # important to look up in the edge-lists of the chromosomes in ascending order (from 1 to X).
        # Sorting handles this, but it is not a good solution in the long run as it depends on sensible
        # values/names.
        node_ids.sort()
        collected_matrices = self._add_nodes_to_mask(node_ids, isDirected, allowLoops)
        collected_matrices_as_numpy_array = self._create_new_matrix_from_collected_matrices(collected_matrices)
        result = functionToApply(collected_matrices_as_numpy_array)
        return result    
    
    @staticmethod
    def _add_neighbour_nodes_to_mask(node_ids, isDirected, allowLoops, mask, edges, i, node_id):
        #eliminate duplicates if the graph is undirected
        for node_id2 in node_ids if isDirected else node_ids[i:]:
            #if allowLoops is false, we have to verify that the two nodes
            #are not the same befor including them in the mask
            if allowLoops or node_id2 != node_id:
                mask = np.logical_or( mask, edges == node_id2)
        return mask
    
    def _add_nodes_to_mask(self, node_ids, isDirected, allowLoops):
        collected_matrices = []
        for i, node_id  in enumerate(node_ids):
            genome_region, index = self._id2index[node_id]
            trackView = self._trackViewDict[genome_region]
            edges = trackView.edgesAsNumpyArray()[index]
            weights = trackView.weightsAsNumpyArray()
            if weights == None:
                #if there are no weights on this graph, return a matrix with only one element: 0.0
                #TODO: how should this case be handled? Exception? 
                collected_matrices = []
                break
            weights = weights[index]
            mask = np.zeros_like(edges, dtype='bool')
            mask = self._add_neighbour_nodes_to_mask(node_ids, isDirected, allowLoops, mask, edges, i, node_id)
            #remove nan-values from mask
            nan_mask = np.isnan(weights)
            mask = np.logical_and(np.logical_not(nan_mask), mask)
            #print "should contain all edges so far", edges[mask]
            #add the chosen weights to the collection of matrixes
            collected_matrices.extend(weights[mask])
        return collected_matrices
        
    @staticmethod
    def _create_new_matrix_from_collected_matrices(collected_matrices):
        return np.array(collected_matrices)
    
    def getSumOfWeightsInGraph(self, allowLoops=True, isDirected=None):
        return self.applyFunctionToWeightsInGraph(np.sum, allowLoops=allowLoops, isDirected=isDirected)
    
    def getMeanOfWeightsInGraph(self, allowLoops=True, isDirected=None):
        return self.applyFunctionToWeightsInGraph(np.mean, allowLoops=allowLoops, isDirected=isDirected)

    def getSumOfWeightsInGraphUsingEdgeIter(self):
        return sum([e.weight for e in self.getEdgeIter()])
    
    def getRandomNode(self):
        from gold.util.RandomUtil import random
        index = random.randint(0, len(self._id2index))
        return self.getNode( self._id2index.keys()[index])
        
    def getNode(self, ident):
        if not ident in self._id2nodes:
            reg, pos = self._id2index[ident]
            #te = TrackElement(self._trackViewDict[reg],index=pos)            
            self._id2nodes[ident] = NodeElement(self._trackViewDict[reg], pos, self)
        return self._id2nodes[ident]
           
    def getNodeIter(self):
        for ident in self._id2index:
            yield self.getNode(ident)

    def _getSortedNodeStartsAndIds(self):
        if self._cachedSortedNodeStartsAndIds is None:            
            nodestarts = []
            nodeids = []
            for node in self.getNodeIter():
                pos = node.start()
                ident = node.id()
                nodestarts.append(pos)
                nodeids.append(ident)
            # nodestarts are not sorted at this point
            nodelist = zip(nodestarts, nodeids)
            nodelist.sort() # sort nodelist on nodestarts
            self._cachedSortedNodeStartsAndIds = zip(*nodelist)
        return self._cachedSortedNodeStartsAndIds #nodestarts, nodeids
    
    #from quick.application.SignatureDevianceLogging import takes
    #from gold.track.GenomeRegion import GenomeRegion
    #@takes(GraphView, GenomeRegion)
    def getNodeIdFromGenomeCoordinate(self, coordinate):
        if coordinate in self._cachedCoordinateMappings:
            return self._cachedCoordinateMappings[coordinate]
        else:
            nodestarts, nodeids = self._getSortedNodeStartsAndIds()
            # nodestarts are now sorted, and nodeids correspond to nodestarts
    
            # Map points to ID (in subgraph)
            nodeid = nodeids[bisect(nodestarts, coordinate)-1]
            #node = self.getNode(nodeid)
            if len(self._cachedCoordinateMappings) < self.MAX_COORDINATE_MAPPING_CACHE_SIZE:
                self._cachedCoordinateMappings[coordinate] = nodeid
            return nodeid
           
    def getEdgeIter(self):
        for node in self.getNodeIter():
            for neighbor in node.getNeighborIter():
                #if hash(node) == hash(neighbor.node):
                #    assert node == neighbor.node
                #    
                #if hash(node)<=hash(neighbor.node):
                #    yield Edge(node, neighbor.node, neighbor.weight) 

                if self.isDirected() or node.id() <= neighbor.toNode.id():
                    yield Edge(node, neighbor.toNode, neighbor.weight, self.isDirected())
    
    def isDirected(self):
        return self._isDirected
    
    def resetColoring(self):
        for node in self.getNodeIter():
            node.color = None
            
    @staticmethod
    def getMatrixFromCompleteSubGraph(indices, matrix, copy=True):
        '''
        Returns a matrix consisting only of the rows/colums defined in indices.
        If copy is false, a view is returned, rather than a new array
        
        TODO: implement if copy=False (return a view instead)
        TODO: change name of this method?
        '''
        sub_matrix = matrix.take(indices, axis=0).take(indices, axis=1)
        return sub_matrix

    def getMatrixFromCompleteGraph(self):
        return self.getMatrixAndIdsFromCompleteGraph()["matrix"]

    def getMatrixAndIdsFromCompleteGraph(self):
        """
        Returns a 2-dimensional numpy.array() representing the complete graph with weights between every pair of nodes.
        This is an example of the result from this function:
        np.array([ [0,1], [4,0] ])

        The matrix is stored in a dict with key "matrix", so to get the matrix
        use getMatrixAndIdsFromCompletegraph["matrix"].
        In addition to the matrix a dictionary with mappings from IDs to index (within the matrix) is returned. To get
        it use getMatrixAndIdsFromCompletegraph["ids"].
        
        Assumptions:
        - the numpy-arrays are complete (all nodes have edges to all other nodes);
        - there are loops in the graph (all nodes have edges to themselves).
        
        Getting a matrix from the underlying numpy-arrays seems trivial, but
        the important thing to remember is that this GraphView could be a subgraph. In that case
        the nodes from the supergraph have been filtered, but the underlying trackviews are the same.
        As you can see in filterNodes() the nodes are simply removed from the _id2index. This means that
        we have to find the nodes from _id2index and then look those nodes up in the numpy-arrays.
        
        TODO: in the case where there are multiple genome regions, each genome region
        should only be read once and all nodes within this genome region should be handled simulatinously.
        This requires building up a "reverse" of _trackViewDict, with mappings from genomeRegion to node ids
        """
        node_ids = self._id2index.keys()
        #from the first node, find the indexes of all nodes in this graph (for reasons explained in the docstring):
        node_ids.sort()
        #this is to prevent failing from the initial "test-run" performed on
        #all tools:
        if node_ids == None or len(node_ids) == 0:
            #print "node_ids is None or its length is 0."
            return {"matrix": np.array([]), "ids": {}}
        unique_genome_regions = set([i[0] for i in self._id2index.itervalues()])
        #print "number of (unique) genome regions:", len(unique_genome_regions)
        indices_for_genome_region = {} # genome_region, [node_indices]
        for genome_region in unique_genome_regions:
            trackView = self._trackViewDict[genome_region]
            edges = trackView.edgesAsNumpyArray()[0]
            node_indices = self._find_indices_of_elements_in_array(node_ids, edges)    
            indices_for_genome_region.update({genome_region: node_indices})
        #genome_region, index = self._id2index[node_ids[0]]
        #trackView = self._trackViewDict[genome_region]
        #edges = trackView.edgesAsNumpyArray()[index]
        #find the index of each node from node_ids in edges
        #node_indices = self._find_indices_of_elements_in_array(node_ids, edges)
        #print "node_indices:", node_indices
        #TODO: replace collected_weights list with a numpy-stacked array 
        collected_weights = []
        id2index = {}
        for i, node_id in enumerate(node_ids):
            genome_region, index = self._id2index[node_id]
            node_indices = indices_for_genome_region[genome_region]
            trackView = self._trackViewDict[genome_region]
            weights = trackView.weightsAsNumpyArray()[index][node_indices]
            id2index.update({node_id: i})
            #print "edges from", node_id, ":", trackView.edgesAsNumpyArray()[index][node_indices]
            collected_weights.append(weights)
        res = np.array(collected_weights)
        #print "Shape of matrix:", res.shape
        return {"matrix": res, "ids": id2index}


    @staticmethod
    def _find_indices_of_elements_in_array(numpy_elements, numpy_array):
        """
        Returns an np.array of indices for the 'elements' in 'array'
        
        example:
        elements = np.array([1,9,3])
        array = np.array([1,2,3,4,5,6,7,8,9])
        _find_indices_of_elements_in_array(elements, array)
        >> [0, 8, 2]
        
        TODO: improve this terribly inefficient method. Looping through numpy-arrays are 
        """
        all_indices = []
        numpy_elements = np.array(numpy_elements)
        numpy_array = np.array(numpy_array)
        for element in numpy_elements:
            new_indices = np.where(element == numpy_array)[0]
            all_indices.extend(list(new_indices))
        return np.array(all_indices)
            

    def _commonGetMatrixRepresentation(self, completeMatrix, rowsAsFromNodes, hasWeights, missingEdgeWeight):
        ''' Returns a matrix representation of this graph.
            completeMatrix: true if the graph is complete, false otherwise.
            rowsAsFromNodes: true if the rows in the resulting matrix is considered as "from node X" and the columns as "to node Y".
            hasWeights: flag to indicate if the resulting matrix should contain weights or just indicate the presence of an edge.
            missingEdgeWeight: the default value for edge weights.
        '''
        if completeMatrix:
            #compute the number of rows and columns needed for this matrix:
            rows = np.unique( np.array([(edge.fromNode.id(), edge.toNode.id()) for edge in self.getEdgeIter()], dtype='S').flatten() )
            cols = copy(rows)
        else:
            #compute the number of rows and columns needed for this matrix:
            rows = np.unique( np.array([edge.fromNode.id() for edge in self.getEdgeIter()], dtype='S') )
            cols = np.unique( np.array([edge.toNode.id() for edge in self.getEdgeIter()], dtype='S') )
            if not rowsAsFromNodes:
                rows, cols = cols, rows
        #compute the shape of the matrix to be created
        shape = (len(rows), len(cols)) if len(rows) > 0 and len(cols) > 0 else (0,)
        #create an empty matrix with a shape given as rows x cols, and fill it with zeros
        matrix = np.zeros(shape=shape, dtype='float64' if hasWeights else 'bool8')
        if missingEdgeWeight != 0:
            #set all edge weights to 'missingEdgeWeight', as a default
            matrix[:] = missingEdgeWeight
        #fill in the matrix:
        for edge in self.getEdgeIter():
            if rowsAsFromNodes:
                matrix[rows == edge.fromNode.id(), cols == edge.toNode.id()] = edge.weight if hasWeights else 1
            else:
                matrix[rows == edge.toNode.id(), cols == edge.fromNode.id()] = edge.weight if hasWeights else 1
        return OrderedDict([('Matrix', matrix), ('Rows', rows), ('Cols', cols)])

    def _commonOptimizedGetMatrixRepresentation(self, completeMatrix, rowsAsFromNodes, hasWeights, missingEdgeWeight):
        """
        This is an experimental version of _commonGetMatrixRepresentation.

        Returns a matrix representation of this graph.
            completeMatrix: true if the graph is complete, false otherwise.
            rowsAsFromNodes: true if the rows in the resulting matrix is considered as "from node X" and the columns as "to node Y".
            hasWeights: flag to indicate if the resulting matrix should contain weights or just indicate the presence of an edge.
            missingEdgeWeight: the default value for edge weights.
        """
        #caching all the edges in memory
        all_edges = [(edge.fromNode.id(), edge.toNode.id(), edge.weight) for edge in self.getEdgeIter()]
        if completeMatrix:
            #compute the number of rows and columns needed for this matrix:
            rows = np.unique( np.array([(fromNodeId, toNodeId) for (fromNodeId, toNodeId, weight) in all_edges], dtype='S').flatten() )
            cols = copy(rows)
        else:
            #compute the number of rows and columns needed for this matrix:
            rows = np.unique( np.array([fromNodeId for (fromNodeId, toNodeId, weight) in all_edges], dtype='S') )
            cols = np.unique( np.array([toNodeId for (fromNodeId, toNodeId, weight) in all_edges], dtype='S') )
            if not rowsAsFromNodes:
                rows, cols = cols, rows
        #compute the shape of the matrix to be created
        shape = (len(rows), len(cols)) if len(rows) > 0 and len(cols) > 0 else (0,)
        #create an empty matrix with a shape given as rows x cols, and fill it with zeros
        matrix = np.zeros(shape=shape, dtype='float64' if hasWeights else 'bool8')
        if missingEdgeWeight != 0:
            #set all edge weights to 'missingEdgeWeight', as a default
            matrix[:] = missingEdgeWeight
            #fill in the matrix:
        for (fromNodeId, toNodeId, weight) in all_edges:
            if rowsAsFromNodes:
                matrix[rows == fromNodeId, cols == toNodeId] = weight if hasWeights else 1
            else:
                matrix[rows == toNodeId, cols == fromNodeId] = weight if hasWeights else 1
        return OrderedDict([('Matrix', matrix), ('Rows', rows), ('Cols', cols)])

        
    def getBinaryMatrixRepresentation(self, completeMatrix=False, rowsAsFromNodes=True):
        '''
        Computes a boolean matrix representation of the graph, where i,j is True if there is an edge between node i and node j.
        Returns this as a dict of two numpy arrays ('Rows' and 'Cols') and one numpy matrix ('Matrix').
        Rows and Cols contain the row and column names, respectively, while Matrix contains the binary
        matrix, where matrix[nodeIdi][nodeIdj] gives the value for i,j
        '''
        return self._commonGetMatrixRepresentation(completeMatrix, rowsAsFromNodes, hasWeights=False, missingEdgeWeight=0)
        
    def getEdgeWeightMatrixRepresentation(self, completeMatrix=False, rowsAsFromNodes=True, missingEdgeWeight=0):
        '''
        Computes a matrix representation of the weights of all edges of the graph, where i,j is the weight of an edge between node i and node j.
        Entries corresponding to lacking edges is filled in with missingEdgeWeight.
        Returns this as a dict of two numpy arrays ('Rows' and 'Cols') and one numpy matrix ('Matrix').
        'Rows' and 'Cols' contain the row and column names, respectively, while 'Matrix' contains the binary
        matrix, where matrix[nodeIdi][nodeIdj] gives the value for i,j
        '''
        return self._commonGetMatrixRepresentation(completeMatrix, rowsAsFromNodes, hasWeights=True, missingEdgeWeight=missingEdgeWeight)
        #return self._commonOptimizedGetMatrixRepresentation(completeMatrix, rowsAsFromNodes, hasWeights=True, missingEdgeWeight=missingEdgeWeight)
    
            
class ProtoGraphView(BaseGraphView):            
    def getClosedGraphVersion(self):
        '''Simply returns a corresponding GraphView-objects, as this in a lazy fashion will
        apply a filter to NodeNeighbors, so that all neighbors outside the node set are filtered out'''
        return GraphView(self._trackViewDict, self._id2index, self._isDirected)
    

class LazyProtoGraphView(ProtoGraphView):
    @classmethod
    def createInstanceFromTrackView(cls, trackView, isDirected=True):
        gReg = trackView.genomeAnchor
        trackViewDict = {gReg:trackView}
        ids = trackView.idsAsNumpyArray()
        isDirected = isDirected #trackView.trackFormat.isDirectedGraph()
        
        #operate with mapping to tuples of tvId (GenomeRegion) and posId (position within tv)
        indexes = zip([gReg]*len(ids), range(len(ids)) )
        id2index = dict(zip(ids, indexes))
        return LazyProtoGraphView(trackViewDict, id2index, isDirected)
    
        #operate directly with simple lists        
        #self._id2nodeIndex = dict(zip(ids, xrange(len(ids)))) #the values of this dict indexes against the two following lists..
        #self._nodeIndex2tvNumber = [gReg]*xrange(len(ids))
        #self._nodeIndex2tvPos = xrange(len(ids))
                              

    @classmethod
    def mergeProtoGraphViews(cls, pgvList):
        #operate with mapping to tuples of tvId and posId
        mergedTrackViewDict = {}
        mergedId2index = {}
        mergedIsDirected = None
        for pgv in pgvList:
            if pgv is not None:
                mergedTrackViewDict.update(pgv._trackViewDict)
                mergedId2index.update(pgv._id2index)
                if mergedIsDirected is None:
                    mergedIsDirected  = pgv._isDirected
                else:
                    assert mergedIsDirected  == pgv._isDirected
                
        pgv = LazyProtoGraphView(mergedTrackViewDict, mergedId2index, mergedIsDirected)
        #operate directly with simple lists
        #mergedId2nodeIndex = {}
        #mergedTrackViewDict = []
        #mergedNodeIndex2tvNumber = []
        #mergedNodeIndex2tvPos = []
        #
        #for i,pgv in enumerate(pgvList):
        #    mergedId2nodeIndex = mergedId2nodeIndex.update(pgv._id2nodeIndex)
        #    mergedTrackViewDict += pgv._trackViewDict[0]
        #    #mergedNodeIndex2tvNumber += [i]*xrange(len(ids))
        #    mergedNodeIndex2tvNumber += pgv._nodeIndex2tvNumber
        #    mergedNodeIndex2tvPos += pgv._nodeIndex2tvPos
        return pgv

#class ExplicitProtoGraphView(ProtoGraphView):
#    def __init__(self, trackView):
#        self._ids = trackView.getIdsAsNumpyArray()
#        self._protoNodes = [trackView.getProtoNodeElement(i) for i in len(trackView)]
#        
#        #not needed, as part of nodes..
#        #edges = trackView.getEdgesAsNumpyArray()
#        #weights = trackView.getWeightsAsNumpyArray()
#
#    @classmethod
#    def mergeProtoGraphViews(cls, pgvList):
#        pass
