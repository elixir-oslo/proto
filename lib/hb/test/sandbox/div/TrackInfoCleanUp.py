

# kan bli statiske funksjoner i TrackInfo.py
print('inne i TrackInfoCleanUp')

# 1. Remove recordes in Trackinfo.shelve that does not have a track in Standardarized tracks.
import os
import re
import third_party.safeshelve as safeshelve
from gold.description.TrackInfo import TrackInfo
from quick.application.GalaxyInterface import GalaxyInterface
from gold.util.CommonFunctions import createOrigPath
from config.Config import DATA_FILES_PATH
from config.Config import ORIG_DATA_PATH
#SHELVE_FN = DATA_FILES_PATH + os.sep + 'TrackInfo.shelve'
#print ("SHELVE_FN=" , SHELVE_FN)
#SHELVE_FN = '/usit/titan/u1/vegardny/prosjekter/hyperbrowser/trackopprydding/testdata' + os.sep + 'TEST_TrackInfo.shelve'

#print ("Bruker shelve=" , SHELVE_FN)

# Checks that every record in TrackInfo.shelve is in the StandardarizedTracks - filesystem.
# Record is removed if not found.
# Returns (number of found records, number of removed records).
def removeUnusedRecords():
    trackInfoShelve = safeshelve.open(SHELVE_FN, 'w')
    iremoved = 0
    ifound = 0
    for key in trackInfoShelve.keys():
        try:
            ti = TrackInfo.createInstanceFromKey(key)
            fn = createOrigPath(ti.genome, ti.trackName)
            if not os.path.exists(fn):
                raise Exception('Should exclude nmer tracks and other tracks without standardized track (e.g. intensity tracks). How? Not sure..')
                ti.removeEntryFromShelve()
                iremoved = iremoved + 1
            else:
                ifound= ifound + 1
        except Exception, e:
            print "Something wrong with ", fn , ", ", e
    return ifound, iremoved


# 2. count subdirs and tracks for each folder.
# Done when preprocessing. Use os.walk on standaraizedTracks. bottom first.
# For each record, find out wether it is a folder or track.
# If it is a folder count subfolders and subtracks.
# also count cubfolders and tracks per genome
# not finished. Need updates for the trackinfo and genomeinfo classes.
def updateTrackFolderStatistics():
    print('inne i updateTrackFolderStatistics')
    #trackInfoShelve = safeshelve.open(SHELVE_FN, 'w')   
    for genomeinfo in GalaxyInterface.getAllGenomes():
        genome = genomeinfo[1]
        if genome=="hg18":
            genome="hg18"
        print "dirname=",genome
        thisntracks=0
        thisndirs=0
        for startparenttrack in GalaxyInterface.getMainTrackNames(genome):
            #print "startparenttrack=",startparenttrack
            firstparenttrack=[startparenttrack[0]]
            ndirs,ntracks = countSubTracks(genome,firstparenttrack , 0 )
            thisndirs=thisndirs+ndirs
            thisntracks=thisntracks+ntracks
        # put counts into genomeinfo.shelve?
        print('plan to update genomeinfo', genome, ' set number of folders to ', thisndirs, ' and number of tracks to ', thisntracks)


# Recursice count of tracks and folders.
def countSubTracks(genome, parentTrack, recursioncount):
    if recursioncount < 10:
        thissubs=GalaxyInterface.getSubTrackNames(genome, parentTrack, False)[0]
        tname=genome+":"+":".join( parentTrack)
        #ti = TrackInfo.
        if thissubs: # has subtrakcs, ie is a folder
            thisndirs=0
            thisntracks=0
            for a in thissubs:               
               nextparenttrack=parentTrack
               nextparenttrack.append(a[0])               
               ndirs, ntracks =countSubTracks(genome, nextparenttrack, recursioncount+1)
               thisndirs=thisndirs+ndirs
               thisntracks=thisntracks+ntracks
               nextparenttrack=nextparenttrack.remove(a[0])
            print('plan to update trackinfo', tname,' set number of folders to ', thisndirs, ' and number of tracks to ', thisntracks)
            return(thisndirs+1, thisntracks)
        else:# is a track.          
            return (0,1)
    else:
        print "to many recursions"





#print ('found and removed = ' ,removeUnusedRecords())

#updateTrackFolderStatistics()







### oppdatere metainfo for literature-derived som timet ut i browsertoolen.


print('Ferdig trackinfocleanup')






