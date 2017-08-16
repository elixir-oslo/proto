import sys, os, getopt,types

import galaxy.eggs
from galaxy.util import restore_text

from gold.application.GalaxyInterface import *


def main():
    input = sys.argv[1]
    output = sys.argv[2]
    point_to_use = sys.argv[3]
    genome = sys.argv[4]
    
    print 'GalaxyInterface.convertSegmentsToPoints', (input, output, point_to_use)
    sys.stdout = open(output, "w", 0)
    GalaxyInterface.convertSegmentsToPoints(input, output, point_to_use)
    
if __name__ == "__main__":
    main()
