import sys, os, getopt,types

from gold.application.GalaxyInterface import *


def main():
    input = sys.argv[1]
    output = sys.argv[2]
    gap = sys.argv[3]    
    print 'GalaxyInterface.convertBedGraphToWigVStepFillingGaps', (input, output, gap)
    sys.stdout = open(output, "w", 0)
    GalaxyInterface.convertBedGraphToWigVStepFillingGaps(input, output, gap)
    
if __name__ == "__main__":
    main()
