from gold.track.Track import PlainTrack
from gold.track.GenomeRegion import GenomeRegion

#def getTrackDataForSingleRegion(pt, gr):
    #pass

#def getTrackDataForMultipleRegions(pt, gri):
    #pass

#create a track
track = PlainTrack(['Genes and gene subsets','Genes','Refseq'])
#track = PlainTrack(['DNA structure','Bendability'])

#create a region of interest
region = GenomeRegion('hg18','chr1',1000,900000)

#Could instead have been iterator of regions, e.g. genome-wide:
#from quick.application.UserBinSource import UserBinSource
#regionIter = UserBinSource('*','*','hg18')
#for region in regionIter:
#    track.getTrackView(region):
#print 'Last region of iter: ', region

#iterate through elements of the track in this region
trackView = track.getTrackView(region)
for element in trackView:
    #just print the intervals for now..
    print element.start(), element.end()
    
tv = track.getTrackView(region)
print 'Number of elements in region, the slow way: ', len([element for element in tv])
print 'Number of elements in region, the fast way: ', len(tv.startsAsNumpyArray())

print 'Bp coverage by elements in the region, the slow way: ', sum(element.end()-element.start() for element in tv)
print 'Bp coverage by elements in the region, the fast way: ', tv.endsAsNumpyArray().sum() - tv.startsAsNumpyArray().sum()
    
trackExplanation = \
'''
A Track object loads the appropriate preprocessed data based on a track name.
Calling the method getTrackView gives an object (really of class TrackView) that is used simply to iterate through all track elements of the given genome region.
A track element (of class TrackElement) has methods start,end,val,strand. Some of these will typically be None, depending on the format of the requested track (e.g. for Segments the method val will return None..)
'''

