import sys

from gold.application.GalaxyInterface import *
#from quick.extra.GoogleMapsInterface import *
#from config.Config import *

def main():
    print sys.argv
    scriptName, output, track = sys.argv

    GalaxyInterface.extractTrackManyBins('hg18', track.split(':'), '*', '*', True, 'gtrack', True, True, output)

if __name__ == "__main__":
    main()


