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
from gold.statistic.Statistic import MultipleRawDataStatistic, StatisticSparseDictSumResSplittable
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.BinSizeStat import BinSizeStat
from gold.statistic.RawDBGStat import RawDBGStat
from _collections import defaultdict

import numpy as np
from quick.util.debug import DebugUtil


class MultitrackRawBinnedStat(MagicStatFactory):
    '''
    Counts the overlap for all track combinations.
    The result is a dict that where key is the int version of the binary number that represents the track combination
    E.G. for 3 tracks, the combination of the first and third track is in binary 101 and the key is 5. 
    For the combination of first and second track 011 and the key is 3.
    '''
    pass

class MultitrackRawBinnedStatSplittable(StatisticSparseDictSumResSplittable):
    pass


class MultitrackRawBinnedStatUnsplittable(MultipleRawDataStatistic):
    VERSION = '1.1'

    def _compute(self): #Numpy Version..
        print "HEI!---------------------------------------------------------------"

        T = self.children[0].getResult();
        res = defaultdict(int)
        res[0] = T;        
        return res;
 #               

    def _createChildren(self):
        #TODO: check solution!
        #For the tests to work with multiple tracks we must send Track objects in extraTracks.
        #Because of the Statistic.constructUniqueKey we must send in a tuple which is hashable.
        if 'extraTracks' in self._kwArgs:
            del self._kwArgs['extraTracks']
        self._addChild(RawDBGStat(self._region, self._track, self._track2, extraTracks = tuple(self._tracks[2:]), **self._kwArgs))
        
    def _getTrackFormatReq(self):
        return TrackFormatReq(dense=False,allowOverlaps=False)

#    def _createChildren(self):
#        #TODO: check solution!
#        #For the tests to work with multiple tracks we must send Track objects in extraTracks.
#        #Because of the Statistic.constructUniqueKey we must send in a tuple which is hashable.
#        MultipleRawDataStatistic._createChildren(self);
#        if 'extraTracks' in self._kwArgs:
#            del self._kwArgs['extraTracks']
#        
#        self._binSizeStat = self._addChild( BinSizeStat(self._region, self._track2))
