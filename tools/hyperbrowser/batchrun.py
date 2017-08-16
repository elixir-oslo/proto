import sys, os, getopt,types

# NB: import eggs before galaxy.util
#import galaxy.eggs
#from galaxy.util import restore_text

from gold.application.GalaxyInterface import *
from config.Config import URL_PREFIX

import proto.hyperbrowser.hyper_gui as hg

def main():
    #print "running"
    filename = sys.argv[1]
    params = hg.fileToParams(filename)
    
    batch = params['batch'].split('\n')
    genome = params['dbkey']

    sys.stdout = open(filename, "w", 0)

    username = params['userEmail'] if params.has_key('userEmail') else ''
    GalaxyInterface.runBatchLines(batch, filename, genome, username)
    
if __name__ == "__main__":
    os.nice(10)
    main()
