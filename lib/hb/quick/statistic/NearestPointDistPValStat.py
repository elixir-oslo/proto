from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.track.TrackFormat import TrackFormatReq
from gold.statistic.NearestPointDistsStat import NearestPointDistsStat
from gold.statistic.RawDataStat import RawDataStat

class NearestPointDistPValStat(MagicStatFactory):
    pass

#class NearestPointDistPValStatSplittable(StatisticSumResSplittable):
#    pass
            
class NearestPointDistPValStatUnsplittable(Statistic):    
    def __init__(self, region, track, track2, distDirection='both', **kwArgs):
        assert( distDirection in ['both']) #only supported now..
        
        self._distDirection = distDirection
        Statistic.__init__(self, region, track, track2, distDirection=distDirection, **kwArgs)

    def _compute(self):
        #now assumes first track is stochastic, and second is fixed.
        #ignores strands..
        #assumes points are sorted..
        
        #first computes null distribution
        bDists = self._getSortedBDists()
        if bDists == None:
            return {'P-value':None}
        
        uniqueBDists, revCumPoints, totalArea = self._getNullDistr(bDists)
        
        observedMean = self._getObservedMean()
        
        areaToObservation = 0
        prevBorder = 0
        for stepBorder in uniqueBDists:
            areaToObservation += ( min(stepBorder,observedMean) -prevBorder)\
                * revCumPoints[stepBorder]
            prevBorder = stepBorder
            if prevBorder > observedMean:
                break
            
        return {'P-value':1.0 * areaToObservation / totalArea}
        
    def _getObservedMean(self):
        dists = self._children[0].getResult()
        return 1.0 * sum(dists ) / len(dists)
        
    def _getNullDistr(self, bDists):                
        #the number of bDists being equal or lower to a specific distance value.
        uniqueBDists = sorted(list(set(bDists)))

        revCumPoints = {}
        for bIndex,dist in enumerate(bDists):
            if not dist in revCumPoints: #to count towards the first bDist when many dists are equal..
                revCumPoints[dist] = len(bDists) - bIndex
        
        #find area of un-normalized stepwise uniform distribution
        area = 0
        prevBorder = 0
        for stepBorder in uniqueBDists:
            area += (stepBorder-prevBorder) * revCumPoints[stepBorder]
            prevBorder = stepBorder
            
        return uniqueBDists, revCumPoints, area
        
        
    def _getSortedBDists(self):
        "get a sorted list of all distances b_i as defined in the note for the test"
        fixedPoints = [x.start() for x in self._children[1].getResult()]
        if len(fixedPoints) < 1:
            return None
        
        
        bDists = []
        #first add all inter-point distances two times:
        for dummy in [1,2]:
            bDists += [ (fixedPoints[i]-fixedPoints[i-1]) / 2 for i in range(1, len(fixedPoints)) ]
        #then add start- and end-dist:
        bDists.append( fixedPoints[0] / 2)
        bDists.append( (len(self._region) - fixedPoints[-1]) / 2)
        return sorted(bDists)
    
    def _createChildren(self):
        #self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(name='points')) )
        self._addChild( NearestPointDistsStat(self._region, self._track, self._track2, distDirection = self._distDirection) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, interval=False)) )
