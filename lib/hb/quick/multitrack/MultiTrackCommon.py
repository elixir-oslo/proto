from quick.application.ExternalTrackManager import ExternalTrackManager
'''
Created on Nov 21, 2014

@author: boris
'''


def getGSuiteDataFromGSuite(gSuite):
    assert gSuite.isPreprocessed(), 'GSuite file contains tracks that are not preprocessed'
    genome = gSuite.genome
    trackTitles = gSuite.allTrackTitles()
    internalTracks = [track.trackName for track in gSuite.allTracks()]
    return trackTitles, internalTracks, genome

def getGSuiteDataFromGalaxyTN(galaxyTn):
    gSuite = getGSuiteFromGalaxyTN(galaxyTn)
    return getGSuiteDataFromGSuite(gSuite)

def getGSuiteFromGalaxyTN(galaxyTn):
    gSuiteFn = ExternalTrackManager.extractFnFromGalaxyTN(galaxyTn)
    return getGSuiteFromGSuiteFile(gSuiteFn)

def getGSuiteFromGSuiteFile(gSuiteFn):
    from gold.gsuite import GSuiteParser
    return GSuiteParser.parse(gSuiteFn)

def getGSuiteDataFromGSuiteFile(gSuiteFn):
    gSuite = getGSuiteFromGSuiteFile(gSuiteFn)
    return getGSuiteDataFromGSuite(gSuite)

def getSingleTrackGSuiteDataFromGalaxyTN(galaxyTn):
    titles, tracks, genome = getGSuiteDataFromGalaxyTN(galaxyTn)
    assert len(titles) > 0, 'GSuite must contain at least one track'
    return titles[0], tracks[0], genome
