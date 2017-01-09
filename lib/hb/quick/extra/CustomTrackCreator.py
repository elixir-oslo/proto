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

from copy import copy
import os
from config.Config import ORIG_DATA_PATH
from gold.extra.SlidingWindow import SlidingWindow, TrackViewBasedSlidingWindow
from gold.origdata.PreProcessTracksJob import PreProcessCustomTrackJob
from quick.origdata.CustomTrackGenomeElementSource import CustomTrackGenomeElementSource
from quick.util.GenomeInfo import GenomeInfo
from gold.track.Track import PlainTrack
from gold.track.GenomeRegion import GenomeRegion

class CustomTrackCreator:
    'Creates a custom track based on a supplied function that calculates one value per sliding window'
    
    @classmethod
    def _createTrackCommon(cls, genome, inTrackName, outTrackName, windowSize, func, username, chrList):
        regionList = [GenomeRegion(genome, chr, 0, GenomeInfo.getChrLen(genome, chr) ) for chr in chrList]
        PreProcessCustomTrackJob(genome, outTrackName, regionList, cls._getGeSourceForRegion, \
                                 username=username, inTrackName=inTrackName, windowSize=windowSize, func=func).process()
    
    @classmethod
    def createTrackGW(cls, genome, inTrackName, outTrackName, windowSize, func, username):
        cls._createTrackCommon(genome, inTrackName, outTrackName, windowSize, func, username, GenomeInfo.getChrList(genome))

    @classmethod
    def createTrackChr(cls, genome, inTrackName, outTrackName, windowSize, func, username, chr):
        cls._createTrackCommon(genome, inTrackName, outTrackName, windowSize, func, username, [chr])
    
class TrackViewBasedCustomTrackCreator(CustomTrackCreator):
    'Creates a custom track based on a supplied function that calculates one value per sliding window. '
    'Uses faster numpy-based solution.'
    
    @classmethod
    def _getGeSourceForRegion(cls, genome, outTrackName, region, inTrackName, windowSize, func):
        inTrackView = PlainTrack(inTrackName).getTrackView(region)
        geSource = CustomTrackGenomeElementSource(TrackViewBasedSlidingWindow(inTrackView, windowSize),\
                                                  genome, outTrackName, region.chr, func)
        return geSource

#class BpIter:
#    "Uses old interface with geSource in.."
#    def __init__(self, geSource):
#        self._geSource = geSource
#        
#    def __iter__(self):        
#        self._geSourceIter = self._geSource.__iter__()
#        return copy(self)
#    
#    def next(self):
#        return self._geSourceIter.next().val
#    
#    def __len__(self):
#        return len(self._geSource)
    

    
#class IncrementalCustomTrackCreator:
#    '''More efficient creation of custom tracks:
#    Creates a custom track based on a function that updates the track value
#    based on incrementally added and removed individual basepairs.
#    In start/end of genome sequence, the removed/added basepair is the empty string, correspondingly.
#    '''
