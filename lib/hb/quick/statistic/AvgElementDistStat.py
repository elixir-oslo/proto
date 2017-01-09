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

from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.AvgSegDistStat import AvgSegDistStatUnsplittable
from quick.statistic.ElementDistancesStat import ElementDistancesStat


class AvgElementDistStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class AvgElementDistStatSplittable(StatisticSumResSplittable):
#    pass
            
class AvgElementDistStatUnsplittable(AvgSegDistStatUnsplittable):    

    def _createChildren(self):
        self._addChild( ElementDistancesStat(self._region, self._track) )