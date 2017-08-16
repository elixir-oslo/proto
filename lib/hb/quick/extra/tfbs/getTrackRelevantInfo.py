from gold.track.Track import PlainTrack
from quick.util.GenomeInfo import GenomeInfo
from gold.track.GenomeRegion import GenomeRegion
import numpy
'''
Created on Feb 27, 2015
@author: Antonio Mora
Last update: Antonio Mora; Feb 27, 2015
'''

class getTrackRelevantInfo:

    @staticmethod
    def getNumberElements(genome, trackName):
        track = PlainTrack(trackName)
        numElements = []
        for chrom in GenomeInfo.getChrList(genome):
            chromLen = GenomeInfo.getChrLen(genome, chrom)
            region = GenomeRegion(genome, chrom, 0, chromLen)
            tv = track.getTrackView(region)
            numElements = numElements + [len(tv.startsAsNumpyArray())]
            
        return numElements

    @staticmethod
    def getSegmentSizes(genome, trackName):
        track = PlainTrack(trackName)
        segmentSize = []; sumSegmentSize = []
        for chrom in GenomeInfo.getChrList(genome):
            chromLen = GenomeInfo.getChrLen(genome, chrom)
            region = GenomeRegion(genome, chrom, 0, chromLen)
            tv = track.getTrackView(region)
            sizeSegments = tv.endsAsNumpyArray() - tv.startsAsNumpyArray()
            sumSizes = sizeSegments.sum()
            segmentSize = segmentSize + [sizeSegments.tolist()]
            sumSegmentSize = sumSegmentSize + [sumSizes.tolist()]
            
        return sumSegmentSize

    @staticmethod
    def getAnchor(genome, trackName):
        track = PlainTrack(trackName)
        anchor = []
        for chrom in GenomeInfo.getChrList(genome):
            chromLen = GenomeInfo.getChrLen(genome, chrom)
            region = GenomeRegion(genome, chrom, 0, chromLen)
            tv = track.getTrackView(region)
            anchor = anchor + [str(tv.genomeAnchor)]
        
        return anchor

    @staticmethod
    def getGenomicElements(genome, trackName):
        track = PlainTrack(trackName)
        genElements = []
        for chrom in GenomeInfo.getChrList(genome):
            chromLen = GenomeInfo.getChrLen(genome, chrom)
            region = GenomeRegion(genome, chrom, 0, chromLen)
            tv = track.getTrackView(region)
            for el in tv:
                #print chrom, el.start(), el.end() #, el.name()
                genElements = genElements + [[chrom, el.start(), el.end()]]
                
        return genElements
    
        #print numpy.version.version # 1.7.1 !!
        #unique, counts = numpy.unique(segmentSize, return_counts=True) # This is for numpy 1.9
        #print numpy.asarray((unique, counts)).T
        
        '''track.setFormatConverter('SegmentToMidPointFormatConverter')
        for chrom in GenomeInfo.getChrList(genome):
            chromLen = GenomeInfo.getChrLen(genome, chrom)
            region = GenomeRegion(genome, chrom, 0, chromLen)
            tv2 = track.getTrackView(region)
            for el in tv2:
                print el.start(), el.end(), el.name()'''

