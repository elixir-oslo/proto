import sys, os, getopt,types

import galaxy.eggs
from galaxy.util import restore_text

from gold.application.GalaxyInterface import *


def main():
    input = sys.argv[1]
    output = sys.argv[2]
    criteria = sys.argv[3]
    genome = sys.argv[4]
    
    criteria = restore_text(criteria).replace('XX', '\n')

    print 'GalaxyInterface.filterMarkedSegments', (input, output, criteria, genome)
    sys.stdout = open(output, "w", 0)
    GalaxyInterface.filterMarkedSegments(input, output, criteria, genome)
    
if __name__ == "__main__":
    main()
