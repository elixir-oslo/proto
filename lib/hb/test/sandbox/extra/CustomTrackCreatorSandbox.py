from quick.extra.CustomTrackCreator import CustomTrackCreator
#from rpy import r
from gold.description.TrackInfo import TrackInfo
from copy import copy
#from proto.RSetup import r
from gold.origdata.GenomeElement import GenomeElement
from quick.util.Wrappers import GenomeElementTvWrapper

#cachedDNorm = dict( zip(range(-5001,5001), [r.dnorm(x,0,2000) for x in range(-5001,5001)]) )

#genome, inTrackName, outTrackName, windowSize, func, chr
#CustomTrackCreator.createTrackChr('sacCer1', ['sequence'],['TestCreation1'],3,lambda x:1 if x[0]=="g" else 0,'chr1')
#CustomTrackCreator.createTrackChr('sacCer1', ['Genes and Gene Prediction Tracks','Exons'],['Test','TestCreation6'],1,lambda x: x[0].end if x[0] is not None else 0,'chr1')
#CustomTrackCreator.createTrackGW('sacCer1', ['Genes and Gene Prediction Tracks','Exons'],['TestCreation2'],3,lambda x: x[1].end if x[1] is not None else 0)
#func = lambda x: sum( [r.dnorm(i-len(x)/2.0,0,2)*x[i] for i in range(len(x))] ) / sum( [r.dnorm(i-len(x)/2.0,0,2)*1 for i in range(len(x)) if x[i]!=0] )
#func = lambda x: sum( [r.dnorm(i-len(x)/2.0,0,2)*x[i].val for i in range(len(x))] ) / sum( [r.dnorm(i-len(x)/2.0,0,2)*1 for i in range(len(x)) if x[i]!=None] )
#func = lambda x: ( sum( [r.dnorm(i-len(x)/2.0,0,2000)*x[i].end for i in range(len(x)) if x[i]!=None] ) / sum( [r.dnorm(i-len(x)/2.0,0,2000)*1 for i in range(len(x)) if x[i]!=None] ) ) if len([y for y in x if y!=None])>0 else 0
#func = lambda x: ( sum( [cachedDNorm[i-len(x)/2]*x[i].end for i in range(len(x)) if x[i]!=None] ) / sum( [cachedDNorm[i-len(x)/2]*1 for i in range(len(x)) if x[i]!=None] ) ) if len([y for y in x if y!=None])>0 else 0

#print func([0,0,1,0,2,0,0,0,0])
#print func([0,0,2,0,1,0,0,0,0])
#print func([0,0,0,2,1,0,0,0,0])
#print func([0,2,0,0,0,0,0,0,0])
#print func([0,2,0,0,0,2,0,0,0])
#

#CustomTrackCreator.createTrackChr('sacCer1', ['Genes and Gene Prediction Tracks','Exons'],['Test','TestCreation6'],101,func,'chr1')

def weightedValForWindowsYielder(slidingWindows,windowSize):
    from proto.RSetup import r
    for window in slidingWindows:
        midPos = len(window)/2
        midEl = window[midPos]
        if len(window) == windowSize:
            #print [x.start for x in window]
            #print window[0].start ,window[midPos].start
            assert abs(window[0].start - window[midPos].start) > 2500
            assert abs(window[-1].start - window[midPos].start) > 2500
        
        weightedValIntegral = sum( [r.dnorm(el.start-midEl.start,0,2000)*el.val for el in window if abs(el.start-midEl.start)<2500] )
        #weightedValIntegral = sum( [r.dnorm(el.start-midEl.start,0,2000)*el.end for el in window if abs(el.start-midEl.start)<2500] )
        normalizationIntegral = sum( [r.dnorm(el.start-midEl.start,0,2000)*1 for el in window if abs(el.start-midEl.start)<2500] )
        yield weightedValIntegral / normalizationIntegral
        
#PointSmoothing..:
def smoothPoints(genome, inTrackName, windowSize, chr):
    from gold.extra.SlidingWindow import SlidingWindow
    from quick.util.GenomeInfo import GenomeInfo
    from gold.track.Track import PlainTrack
    from gold.track.GenomeRegion import GenomeRegion
    
    #func = lambda x: ( sum( [r.dnorm(i-len(x)/2.0,0,2000)*x[i].end for i in range(len(x)) if x[i]!=None] ) / sum( [r.dnorm(i-len(x)/2.0,0,2000)*1 for i in range(len(x)) if x[i]!=None] ) ) if len([y for y in x if y!=None])>0 else 0    
    
    chrReg = GenomeRegion(genome, chr, 0, GenomeInfo.getChrLen(genome,chr) )
            #chrReg = GenomeElement(genome, chr, 0, 3000)
    inTrackView = PlainTrack(inTrackName).getTrackView(chrReg)
    print [x.end() for x in inTrackView]
    slidingWindows = SlidingWindow(GenomeElementTvWrapper(inTrackView), windowSize)
    print [x for x in weightedValForWindowsYielder(slidingWindows, windowSize)]
    
smoothPoints('sacCer1', ['Genes and Gene Prediction Tracks','Exons'],21,'chr1')
