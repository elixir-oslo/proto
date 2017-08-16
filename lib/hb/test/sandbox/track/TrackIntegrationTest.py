from gold.track.Track import Track
from gold.track.GenomeRegion import GenomeRegion
from gold.track.TrackFormat import TrackFormatReq

if __name__ == "__main__":
    track = Track(['test'])
    #trackView = track.getTrackView(None, GenomeRegion('hg18','chrM',1000,10000))
    #trackView2 = track.getTrackView(None, GenomeRegion('hg18','chrM',4000,4000))
    trackView = track.getTrackView(GenomeRegion('TestGenome','chr1',-1,1000))

    count=0
    for el in trackView:
        print el.start(), el.end()
        count+=1
        if count>50:
            break
        
    print len([el for el in trackView])
    #print len([el for el in trackView2])
    
