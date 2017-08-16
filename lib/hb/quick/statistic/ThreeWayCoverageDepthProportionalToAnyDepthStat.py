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
        
