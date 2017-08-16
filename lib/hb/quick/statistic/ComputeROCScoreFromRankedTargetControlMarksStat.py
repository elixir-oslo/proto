from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.MarksSortedBySegmentOverlapStat import MarksSortedBySegmentOverlapStat
from quick.statistic.MarksSortedByFunctionValueStat import MarksSortedByFunctionValueStat

class ComputeROCScoreFromRankedTargetControlMarksStat(MagicStatFactory):
    pass

class ComputeROCScoreFromRankedTargetControlMarksStatUnsplittable(Statistic):
    def __init__(self, region, track, track2, rankType='funcval', **kwArgs):
        assert(rankType in ['funcval', 'overlap'])
        self._rankType = rankType
        
        Statistic.__init__(self, region, track, track2, rankType=rankType, **kwArgs)
        

    def _compute(self):        
        allMarks = [int(x) for x in self._children[0].getResult()[0]]
        totalCounts = [ sum(1 for x in allMarks if x==markType) for markType in [0,1] ]
        curCounts = [0,0]

        #If not samples of both classes, the area is given as the neutral (random) ROC-score..
        if 0 in totalCounts:
            return 0.5

        #The area under the curve, where tp-rate is y-axis and fp-rate is x-axis
        #Area is found as the sum of bars along the x-axis, whose height are the current tp-rate and the widt is the size of a single increment of fp-rate
        area = 0
        for mark in allMarks:
            if mark==0:
                #area of new bar = height of bar * width of bar
                area += (1.0 * curCounts[1] / totalCounts[1]) * (1.0/totalCounts[0])
            curCounts[mark] += 1
        return area
        
    def _createChildren(self):
        if self._rankType == 'funcval':
            self._addChild( MarksSortedByFunctionValueStat(self._region, self._track, self._track2, markReq='tc' ) )
        elif self._rankType == 'overlap':
            self._addChild( MarksSortedBySegmentOverlapStat(self._region, self._track, self._track2, markReq='tc') )            
