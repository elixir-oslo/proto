from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import RatioDictSingleDenomStatUnsplittable
from quick.statistic.ThreeWayCoverageDepthStat import ThreeWayCoverageDepthStat
from quick.statistic.BinSizeStat import BinSizeStat


class ThreeWayCoverageDepthProportionalStat(MagicStatFactory):
    pass

class ThreeWayCoverageDepthProportionalStatUnsplittable(RatioDictSingleDenomStatUnsplittable):
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)
        
    def _createChildren(self):
        self._addChild( ThreeWayCoverageDepthStat(self._region, self._track, self._track2, **self._kwArgs) )
        self._addChild( BinSizeStat(self._region, self._track) )
        
