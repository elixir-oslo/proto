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
from quick.statistic.ThreeWayCoverageDepthStat import ThreeWayCoverageDepthStat


class ThreeWayCoverageDepthProportionalToAnyDepthStat(MagicStatFactory):
    pass

class ThreeWayCoverageDepthProportionalToAnyDepthStatUnsplittable(Statistic):
#     from gold.util.CommonFunctions import repackageException
#     from gold.util.CustomExceptions import ShouldNotOccurError
#     @repackageException(Exception, ShouldNotOccurError)
    
    def _compute(self):
        res = {}
        depthRes = self._children[0].getResult()
        relevantDepths = [val for key, val in depthRes.iteritems() if key not in ('Depth 0', 'BinSize')]
        depthSum = sum(relevantDepths)
        if depthSum > 0:
            res = dict([(key, val*1.0/depthSum) for key,val in depthRes.iteritems()  if key not in ('Depth 0', 'BinSize')])
#         else:
#             #TODO: should we add this or just send an empty result?
#             res['Total depth'] = 0
        
        return res
            
    def _createChildren(self):
        self._addChild( ThreeWayCoverageDepthStat(self._region, self._track, self._track2, **self._kwArgs) )
        
