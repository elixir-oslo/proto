import sys

#from gold.application.GalaxyInterface import *
from quick.extra.GoogleMapsInterface import *
#from config.Config import *

def main():
    print sys.argv
    scriptName, output, map, col, row, mapid = sys.argv

    info = MarkInfo(map, int(col), int(row), mapid)
    
    info._writeTrackForGeneListWithHits(output)

if __name__ == "__main__":
    main()


