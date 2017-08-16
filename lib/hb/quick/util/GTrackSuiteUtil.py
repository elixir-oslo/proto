'''
Created on Oct 2, 2014

Util class for working with GTrackSuite.

@author: boris
'''

from urlparse import urlparse

def readGenomeAndTracksFromGTrackSuite(fileName):
    genome = ''
    trackNames = []
    for line in open(fileName):
        hbURL = urlparse(line.strip())
        assert hbURL.scheme == 'hb'
        genome = hbURL.netloc
        trackName = hbURL.path.split('/')
        trackNames.append(trackName)
    
    return trackNames, genome