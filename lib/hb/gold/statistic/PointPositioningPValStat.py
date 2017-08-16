from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.PointPositionsInSegsStat import PointPositionsInSegsStat
from gold.util.CustomExceptions import ShouldNotOccurError, NotSupportedError
from collections import OrderedDict

class PointPositioningPValStat(MagicStatFactory):
    pass

class PointPositioningPValStatUnsplittable(Statistic):
    def _init(self, tail='', **kwArgs):
        self._altHyp = tail
        if not self._altHyp in ['ha1','ha2','ha3','ha4']:
            raise NotSupportedError(self._altHyp)

    def _checkAssumptions(self, assumptions):
        if not assumptions == 'independentPoints':
            raise IncompatibleAssumptionsError
        #pass

    def _computeMc(self):
        return self._children[0].getResult()
    
    def _compute(self):
        assumptions = self._kwArgs['assumptions']
        if not assumptions == 'independentPoints':
            return self._computeMc()

        allRelPositions = self._children[0].getResult()
        
        scoreList = []
        for relPos in allRelPositions:
            score = PointPositioningPValStatUnsplittable._calcScore(relPos, self._altHyp)
            if score!=0:
                #scoreList.append( (abs(score), random(), score>0) ) #random number to avoid sign bias when sorting on absolute value
                scoreList.append( (abs(score), score>0) )
        
        wPlusMinus = {True:0, False:0}
        sortedScores = sorted(scoreList)
        curValPos = 0
        while curValPos < len(sortedScores):
            higherValPos = curValPos + 1
            while higherValPos < len(sortedScores) and \
                sortedScores[higherValPos][0] - sortedScores[curValPos][0] < 1.0e-7: #almost equal, to ignore representation errors
                    higherValPos += 1
            for pos in xrange(curValPos, higherValPos):
                wPlusMinus[sortedScores[pos][1]] += (curValPos+(higherValPos-1))/2.0 +1 #higherValPos-1 since end-exclusive, +1 since ranks start from 1
            curValPos = higherValPos
            
        #w = min(wPlusMinus[True], wPlusMinus[False]) #wouldn't this make it two-tailed?
        w = wPlusMinus[True]
                
        n = len(sortedScores)
        distribution = 'N/A'
        if n<2:
            pval = None
        elif n<30:
            from proto.RSetup import r
            #print 'w,n: ',w,n
            pval = r.psignrank(w,n)
            distribution = 'Wilcoxon'
        else:
            from proto.RSetup import r
            mean = n*(n+1)/4.0
            var = n*(n+1)*(2*n+1)/24.0
            pval = r.pnorm(w, mean, var**0.5)
            distribution = 'Normal approximation'
        
        return OrderedDict([ ('P-value', pval), ('Test statistic: ' + ('W12' if self._altHyp in ['ha1', 'ha2'] else \
                             ('W34' if self._altHyp in ['ha3', 'ha4'] else 'W5')), w), ('N', n) , ('Distribution',distribution), ('altHyp',self._altHyp)]) #fixme: remove althyp from here..
    
    @staticmethod
    def _calcScore(relPos, altHyp):
        if altHyp == 'ha1':
            return 1 - 4*abs(relPos-0.5)
        if altHyp == 'ha2':
            return -1 + 4*abs(relPos-0.5)
        elif altHyp == 'ha3':
            return -1 + 2.0 * relPos
        elif altHyp == 'ha4':
            return 1 - 2.0 * relPos
        else:
            raise ShouldNotOccurError
    
    def _createChildren(self):
        from gold.statistic.RandomizationManagerStat import RandomizationManagerStat
        from gold.statistic.AvgRelPointPositioningStat import AvgRelPointPositioningStat
        assumptions = self._kwArgs['assumptions']
        if not assumptions == 'independentPoints':
            #Bug: For minimalruns, altHyp=='ha1', which fails the assert.
            #     This leads to the MC-based null models to be removed from the list
            assert self._altHyp == 'ha3'
            from copy import copy
            kwArgs = copy(self._kwArgs)
            kwArgs['tail'] = 'less'
            self._addChild( RandomizationManagerStat(self._region, self._track, self._track2, **kwArgs) )
        else:
            self._addChild( PointPositionsInSegsStat(self._region, self._track, self._track2) )
