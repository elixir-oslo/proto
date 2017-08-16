#class Neighbor(object):
#    def __init__(self, node, weight):
#        self.node = node
#        self.weight = weight
            

       
    
#ProtoGraphStatUnsplittable:
'Creates a local ProtoGraphView from a TrackView'
#ProtoGraphStatSplittable:
'Creates a glboal ProtoGraphView from a set of local ProtoGraphView objects'

#GraphStat
'Creates a closed version of a ProtoGraphView (i.e. GraphView) at local/global level'

#i.e. in connection with local bins in 3D space
#here assumes node objects, which has links to neighbors as other node objects
def findConnectedComponent(sourceNode, graph, maxDepth):
    if maxDepth<0:
        return []
    sourceNode.color = True

    #assuming node has explicit links to other node objects in member variable neighbors
    #nodes = concatenate([findConnectedComponent(node, graph, maxDepth-1) for node in sourceNode.neighbors if not graph.isColored(node)] ) #should return empty list if no neighbors..
    #assuming node has method neighbors() that can provide link to explicit other node objects 
    nodes = concatenate([findConnectedComponent(node, graph, maxDepth-1) for node in sourceNode.getNeighbors() if not node.color==True] ) #should return empty list if no neighbors..
    #assuming node has neighbors in the form of ID list..
    #nodes = concatenate([findConnectedComponent(graph.getNodeObject(nodeId), graph, maxDepth-1) for nodeId in sourceNode.neighbors() if not graph.isColored(node)] ) #should return empty list if no neighbors..

    nodes.append(sourceNode)
    return nodes

#graph = ..
#sourceId = ..
#sourceNode = graph.getNode(sourceId)
#findConnectedComponent(sourceNode, graph, 5)

def traverseEulerPath(graph):
    node = graph.getRandomNode()
    path = []
    edgeColoring = {}
    while node is not None:
        
    
#without assuming node objects..
def findConnectedComponent(sourceNode, graph, maxDepth):
    if maxDepth<0:
        return []
    graph.color(sourceNode)
    nodes = concatenate([findConnectedComponent(node, graph, maxDepth-1) for node in sourceNode.neighbors if not graph.isColored(node)] ) #should return empty list if no neighbors..
    nodes.append(sourceNode)
    return nodes

#Moved to separate statistic..
#from gold.statistic.Statistic import Statistic
#class AvgEdgeWeightDifferenceForBinsWithHighCoverageVsAllBinsStatUnsplittable: #LowerEdgeWeightsForBinsWithHighCoverageStatUnsplittable:
#    def _compute(self):
#        nodeValThreshold = 5 #from init..
#        nodeValues = self._nodeValueStat.getResult()
#        qualifiedNodes = [x for x,val in nodeValues.iteritems() if val>nodeValThreshold]
#        fullGraph = self._graphStat.getResult()
#        subGraph = fullGraph.getSubGraphFromNodeIdSet(qualifiedNodes)
#        return subGraph.getAvgEdgeWeight() - fullGraph.getAvgEdgeWeight() 
#            
#    def _createChildren(self):
#        #self._track: 3D data
#        #self._track2: analysis data, segments (e.g. repeats)
#        self._graphStat = self._addChild(GraphStat(self._track) )
#        #self._nodeValueStat = self._addChild(NodeCoverageValueStat(self._track, self._track2) )
#        self._nodeValueStat = self._addChild(GenericNodeValueStat(self._track, self._track2, rawStatistic=CoverageProportionStat) )
        
        
class AvgEdgeWeightDifferenceForBinsWithSimilarCoverageVsAllBinsStatUnsplittable: 
    def _compute(self):
        nodeValThresholds = [1,5] #from init..
        nodeValues = self._nodeValueStat.getResult()
        caseNodes = [x for x,val in nodeValues.iteritems() if val<nodeValThreshold[0]]
        controlNodes = [x for x,val in nodeValues.iteritems() if val>nodeValThreshold[1]]
        fullGraph = self._graphStat.getResult()
        caseGraph = fullGraph.getSubGraphFromNodeIdSet(caseNodes)
        controlGraph = fullGraph.getSubGraphFromNodeIdSet(controlNodes)
        #unionGraph = GraphView.createMergedGraph( [caseGraph, controlGraph]), would not work, because there would be no edges between nodes originating from the two graphs..
        unionNodes = caseNodes+controlNodes        
        unionGraph = fullGraph.getSubGraphFromNodeIdSet(unionNodes)
        
        avgIntraEdgeWeight = (caseGraph.getAvgEdgeWeight() + controlGraph.getAvgEdgeWeight()) /2.0
        avgUnionEdgeWeight = unionGraph.getAvgEdgeWeight()
        return avgUnionEdgeWeight - avgIntraEdgeWeight
            
    def _createChildren(self):
        #self._track: 3D data
        #self._track2: analysis data, segments (e.g. repeats)
        self._graphStat = self._addChild(GraphStat(self._track) )
        #self._nodeValueStat = self._addChild(NodeCoverageValueStat(self._track, self._track2) )
        self._nodeValueStat = self._addChild(GenericNodeValueStat(self._track, self._track2, rawStatistic=CoverageProportionStat) )
        

class NodeValueCorrelationForHighWeightEdgesStatUnsplittable:
    def _compute(self):
        weightThreshold = 5 #from init..
        nodeValues = self._nodeValueStat.getResult() #e.g. coverage

        fullGraph = self._graphStat.getResult()
        edges = fullGraph.getEdgeList()
        qualifiedEdges = [edge for edge in edges if edge.weight>weightThreshold]
        xList = [nodeValues[edge.fromNode.id()] for edge in qualifiedEdges]
        yList = [nodeValues[edge.toNode.id()] for edge in qualifiedEdges]
        return r.corr(xList, yList)
            
    def _createChildren(self):
        #self._track: 3D data
        #self._track2: analysis data, segments (e.g. repeats)
        self._graphStat = self._addChild(GraphStat(self._track) )
        #self._nodeValueStat = self._addChild(NodeCoverageValueStat(self._track, self._track2) )
        self._nodeValueStat = self._addChild(GenericNodeValueStat(self._track, self._track2, rawStatistic=CoverageProportionStat) )