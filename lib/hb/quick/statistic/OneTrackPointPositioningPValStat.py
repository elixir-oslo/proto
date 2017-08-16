from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.PointPositioningPValStat import PointPositioningPValStatUnsplittable
from quick.statistic.RelPositionsInBinStat import RelPositionsInBinStat

class OneTrackPointPositioningPValStat(MagicStatFactory):
    pass

class OneTrackPointPositioningPValStatUnsplittable(PointPositioningPValStatUnsplittable):
    
    def _createChildren(self):
        #from gold.statistic.RandomizationManagerStat import RandomizationManagerStat
        #from gold.statistic.AvgRelPointPositioningStat import AvgRelPointPositioningStat
        #assumptions = self._kwArgs['assumptions']
        #if not assumptions == 'independentPoints':
        #    assert self._altHyp == 'ha3'
        #    self._addChild( RandomizationManagerStat(self._region, self._track, self._track2, AvgRelPointPositioningStat, None, self._kwArgs['assumptions'], 'less', self._kwArgs['numResamplings']) )
        #else:
        self._addChild( RelPositionsInBinStat(self._region, self._track) )
