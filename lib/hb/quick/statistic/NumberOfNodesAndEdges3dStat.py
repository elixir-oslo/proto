# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.GraphStat import GraphStat

class NumberOfNodesAndEdges3dStat(MagicStatFactory):
    pass
            
class NumberOfNodesAndEdges3dStatUnsplittable(Statistic):    
    def _compute(self):
        graph = self._graphStat.getResult()
        #assert not graph.isDirected()
        numNeighbors = []
        i = 0

        numNodes = sum(1 for node in graph.getNodeIter())
        numEdges = sum(1 for edge in graph.getEdgeIter())
        #for node in graph.getNodeIter():
            #numNeighbors.append( sum(1 for neighbor in node.getNeighborIter() if graph.isDirected() or node.id() <= neighbor.node.id()) )#len(list(node.getNeighborIter()))
        #    i = i+1
        #res = {"totNeig" : sum(numNeighbors), "totNodes":i}
        res = {"totNodes" : numNodes, 'totEdges':numEdges}
        return res
    
    def _createChildren(self):
        self._graphStat = self._addChild(GraphStat(self._region, self._track) )
        
