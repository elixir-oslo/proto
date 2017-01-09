# Copyright (C) 2011, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
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

import sys, os
from urllib import quote, unquote

from quick.application.GalaxyInterface import *
from config.Config import URL_PREFIX

import proto.hyperbrowser.hyper_gui as hg


def main():
    filename = sys.argv[1]
    output = filename
    params = hg.fileToParams(filename)
    file_path = params.get('file_path')
    genome = params.get('dbkey')
    track1Name = params.get('track1')

    method = params.get('method')
    if method in ['binfile', '__history__']:
        binfile = params.get('binfile').split(',')
        binspec = hg.getDataFilePath(file_path, binfile[1])
        regspec = binfile[2]
    elif method != '__custom__':
        regspec = method
        binspec = params.get(method)
    else:
        regspec = params.get('region', '*')
        binspec = params.get('binsize', '*')

    intensityname = params.get('intensityname') if params.has_key('intensityname') else None

    track1File = params.get('track1file')
    if track1Name == 'galaxy' and track1File != None:
        tfa = track1File.split(',')
        tracks1 = ['galaxy', tfa[2], hg.getDataFilePath(file_path, tfa[1]), unquote(tfa[3])]
    else:
        tracks1 = track1Name.split(':')
    
    if intensityname not in [None, '']:
        intensityname = intensityname.split(':')
    else:
        intensityname = 'galaxy:hbfunction:'+filename+':Create intensity track'
        
    numctrltracks = int(params.get('numctrltracks'))
    ctrltracks = []
    for num in range(numctrltracks):
        trackName = params.get('track' + str(num+2))
        trackFile = params.get('track' + str(num+2) + 'file')
        if trackName == 'galaxy' and trackFile != None:
            tfa = trackFile.split(',')
            track = ['galaxy', tfa[2], hg.getDataFilePath(file_path, tfa[1]), unquote(tfa[3])]
        else:
            track = trackName.split(':')
        ctrltracks.append(track)

    sys.stdout = open(output, "w", 0)

    #print 'GalaxyInterface.createIntensityTrack', (tracks1, ctrltracks, intensityname, region, binSize, genome)
    GalaxyInterface.createIntensityTrack(tracks1, ctrltracks, intensityname, regspec, binspec, genome, output)


if __name__ == "__main__":
    main()
