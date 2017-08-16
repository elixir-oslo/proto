import sys, os, getopt,types

# NB: import eggs before galaxy.util
import galaxy.eggs
from galaxy.util import restore_text

from gold.application.GalaxyInterface import *

import proto.hyperbrowser.hyper_gui as hg

def main():
    filename = sys.argv[1]
    params = hg.fileToParams(filename)
    
    genome = params['dbkey']
    inTrackName = params['track1']
    trackName = params['customname']
    binSize = params['customwinsize']
    method = params['customfunction']
    output = filename
  
    inTracks = None  
    if inTrackName:
        inTracks = inTrackName.split(':')
    
    track = trackName.split(':')
    #funcStr = restore_text(method).replace('XX', '\n')
    funcStr = method
    
    print 'GalaxyInterface.createCustomTrack ',(genome, inTracks, track, binSize, funcStr)
    sys.stdout = open(output, "w", 0)
    GalaxyInterface.createCustomTrack(genome, inTracks, track, binSize, funcStr)
    
if __name__ == "__main__":
    main()
