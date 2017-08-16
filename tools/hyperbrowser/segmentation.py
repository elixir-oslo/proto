import sys, os, getopt,types

from gold.application.GalaxyInterface import *

import proto.hyperbrowser.hyper_gui as hg

def main():
    #print "running"
    filename = sys.argv[1]
    params = hg.fileToParams(filename)
    
    trackIn = params['intrack'].split(':')
    trackOut = params['outtrack'].split(':')
    methodLines = params['method'].split('\n')
    segLength = params['min_length']
    genome = params['dbkey']
    username = params['userEmail'] if params.has_key('userEmail') else ''

    print 'GalaxyInterface.createSegmentation', (genome, trackIn, trackOut, methodLines, segLength)
    sys.stdout = open(filename, "w", 0)

    GalaxyInterface.createSegmentation(genome, trackIn, trackOut, methodLines, segLength, username)

    
if __name__ == "__main__":
    main()
