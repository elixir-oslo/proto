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

from gold.track.Track import PlainTrack
from gold.track.GenomeRegion import GenomeRegion
from gold.statistic.CountStat import CountStat

#create a track
track = PlainTrack(['Genes and gene subsets','Genes','Refseq'])

#create a region of interest
region = GenomeRegion('hg18','chr1',1000,900000)

#create a statistic
stat = CountStat(region, track)

print stat.getResult()

#What happens now:
#CountStat inherits MagicStatFactory
#MagicStatFactory determines that region may be splitted to smaller bins and looks for a CountStatSplittable.
#CountStatSplittable exists, and is instantiated.
#getResults first calls createChildren. CountStatSplittable now creates a new CountStat for a smaller first region.
#This times, when MagicStatFactory handles CountStat-creation it sees that the region in question should not be splitted.
#MagicStatFactory thus instantiates a CountStatUnsplittable, which loads track data, and does the count for its small bin.
#This is repeated for each small bin, and results are collected by CountStatSplittable.
#Finally, the method combineResults (of CountStatSplittable) computes the total results for the queried region and returns this.
