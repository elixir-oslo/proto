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
'''
Created on Feb 24, 2016

@author: boris
'''

from gold.statistic.CountElementStat import CountElementStat
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import RatioStatUnsplittable
from quick.statistic.BinSizeStat import BinSizeStat


class ProportionElementCountStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class ProportionElementCountStatSplittable(StatisticSumResSplittable):
#    pass
            
class ProportionElementCountStatUnsplittable(RatioStatUnsplittable):    
    
    def _createChildren(self):
        self._addChild( CountElementStat(self._region, self._track, **self._kwArgs) )
        self._addChild( BinSizeStat(self._region, self._track) )