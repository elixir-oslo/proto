import sys, os, getopt,types

from gold.application.GalaxyInterface import *
from hyperbrowser.hyper_gui import getDataFilePath,fileToParams

def trackNameForHistoryItem(field, params):
    item = params[field]
    file_path = params['file_path']
    gal,id,type,name = item.split(',')
    filename = getDataFilePath(file_path, id)
    return [gal, type, filename, name]

def main():
    os.umask(0002)
    filename = sys.argv[1]
    params = fileToParams(filename)

    username = params['userEmail'] if params.has_key('userEmail') else ''
    genome = params['dbkey']
    integratedTrackName = params['integratedname'].split(':')
    private = not params['access_public'] if params.has_key('access_public') else True
    
    historyTrackName = trackNameForHistoryItem('historyitem', params)
    
    sys.stdout = open(filename, "w", 0)
    #print 'GalaxyInterface.integrateTrackFromHistory',(genome, historyTrackName, integratedTrackName, private, username)
    GalaxyInterface.integrateTrackFromHistory(genome, historyTrackName, integratedTrackName, privateAccess=private, username=username)
    
if __name__ == "__main__":
    main()
