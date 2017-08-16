import sys, os

from gold.application.GalaxyInterface import *


def main():
    result = sys.argv[1]
    output = sys.argv[2]
    print 'GalaxyInterface.generateGoogleMapFromHistoryResult', (result)
    sys.stdout = open(output, "w", 0)
    GalaxyInterface.generateGoogleMapFromHistoryResult(result)
    
if __name__ == "__main__":
    main()
