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
from quick.util.RandomizationUtils import getRandTrackClassList, createRandomizedStat

class GenericMCSamplesStat(MagicStatFactory):
    '''
    Takes in a null model (randomization class), a test statistic (rawStatistic) and a desired number of MC samples (numMcSamples),
    then applies the test statistic (rawStatistic) on data from the null model (randomized by the provided randomization class)
    a pre-specified number of times (numMcSamples)
    Returns a list of MC samples (the resulting test statistic/rawStatistic value per randomized sample)
    '''
    pass

#class GenericMCSamplesStatSplittable(StatisticSumResSplittable):
#    pass
            
class GenericMCSamplesStatUnsplittable(Statistic):    
    IS_MEMOIZABLE = False #as it should return new random samples each time it is called

    def _init(self, rawStatistic, randTrackClassList=None, assumptions=None, numMcSamples=1, **kwArgs):
    #def _init(self, rawStatistic, randTrackClassList, numMcSamples, **kwArgs):
        self._rawStatistic = self.getRawStatisticClass(rawStatistic)
        self._numMcSamples = int(numMcSamples)
        
        assert (randTrackClassList is None) ^ (assumptions is None) # xor, corresponding to two alternative specs of the same
        if assumptions is not None:
            randTrackClassList = assumptions.split('_')
        self._randTrackClassList = getRandTrackClassList(randTrackClassList)                    

    
    def _createRandomizedStat(self, i):
        #Refactor the first argument after a better track input handling is in place..
        return createRandomizedStat([self._track, self._track2], self._randTrackClassList, self._rawStatistic, self._region, self._kwArgs, i)
        
    def _compute(self):
        #print 'TEMP1: computing %i samples' % self._numMcSamples
        return [self._createRandomizedStat(i).getResult() for i in range(self._numMcSamples)]                    
    
    def _createChildren(self):
        #Actually just ignored the way it is now. Also consider future simplification.
        #pass
        self._addChild( self._createRandomizedStat(0) )
