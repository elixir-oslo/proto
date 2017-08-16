'''
Created on Apr 27, 2015

@author: boris
'''
# @takes(GSuite)
# @returns(list(tuple(GSuiteTrack)))
def generateAllTrackPairsInGSuite(gSuite):
    '''
    Generator of track pairs in a GSuite
    '''
    assert gSuite.numTracks() > 1, 'GSuite must contain more than 1 track in order to generate pairs'
    from itertools import combinations
    for comb in combinations(list(gSuite.allTracks()), 2):
        yield comb
