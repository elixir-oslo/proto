#!/usr/bin/env python
#from proto.RSetup import r
from quick.util.GenomeInfo import GenomeInfo
from quick.util.CommonFunctions import ensurePathExists
from gold.util.CommonFunctions import createOrigPath
from gold.track.GenomeRegion import GenomeRegion
from gold.track.Track import PlainTrack
import os
import sys

class OrigWriter:
    numPrintedDots = 0
    
    @classmethod
    def writeChr(cls, genome, chr, trackName, elTupleIter):
        outFn = createOrigPath(genome, trackName, chr+cls._getEnding() )
        ensurePathExists(outFn)
        outF = open(outFn,'w')
        cls._writeHeader(outF, chr)
        numPrintedDots = 0
        for el in elTupleIter:
            cls._writeEl(outF, el, chr)
        outF.close()
        
    @classmethod
    def writeChrAdd(cls, genome, chr, trackName, elTupleIter, outFn):
        #outFn = createOrigPath(genome, trackName, chr+cls._getEnding() )
        #ensurePathExists(outFn)
        #print elTupleIter
        
        outF = open(outFn,'w')
        cls._writeHeader(outF, chr)
        numPrintedDots = 0
        
        for el in elTupleIter:
            cls._writeEl(outF, el, chr)
            
        outF.close()

    @classmethod
    def _printProgressDots(cls, pos):
        numDots = pos/10**6
        if numDots > cls.numPrintedDots:
            for i in range(numDots - cls.numPrintedDots):
                print '.',
            cls.numPrintedDots = numDots
    
class OrigBedWriter(OrigWriter):
    @classmethod
    def _writeEl(cls, outF, el, chr):
        start,end = el
        cls._printProgressDots(start)
        outF.write( '\t'.join([str(x) for x in [chr,start,end] ]) +os.linesep)

    @staticmethod
    def _writeHeader(outF, chr):
        return
    
    @staticmethod
    def _getEnding():
        return '.bed'
    
class OrigPointBedWriter(OrigBedWriter):
    @staticmethod
    def _getEnding():
        return '.point.bed'

class OrigWigFixedWriter(OrigWriter):
    @classmethod
    def _writeEl(cls, outF, el, chr):
        OrigWigFixedWriter.pos += 1
        val = el
        cls._printProgressDots(OrigWigFixedWriter.pos)
        outF.write( '%.3f' % val +os.linesep)

    @staticmethod
    def _writeHeader(outF, chr):
        OrigWigFixedWriter.pos = 0
        outF.write('track type=wiggle_0'+os.linesep)
        outF.write('\t'.join(['fixedStep','chrom='+chr, 'start=1', 'step=1']) +os.linesep)
        
    @staticmethod
    def _getEnding():
        return '.wig'

    
class ElIter(object):
    def _getChrLen(self):
        return GenomeInfo.getChrLen(self.genome, self.chr)

class PointIterInterval(ElIter):
    def __init__(self, genome, chr, interRate, intraRate, interProb, chrMin, chrMax):
        self.genome, self.chr = genome, chr
        self.interRate, self.intraRate, self.interProb  = float(interRate), float(intraRate), float(interProb)
        self.chrMin, self.chrMax = int(chrMin), int(chrMax)
        assert interProb > 0

    def __iter__(self):
        from proto.RSetup import r

        #maxPos = self._getChrLen()
        maxPos = self.chrMax
        minPos = self.chrMin

        pos = minPos

        while True:
            runif = r.runif(1)

            if runif < self.interProb:
                rexp = r.rexp(1,self.interRate)
                pos += int( max(1,rexp)) # among clusters
            else:
                rexp = r.rexp(1,self.intraRate) # inside cluster
                pos += int( max(1,rexp))


            if pos < maxPos:
                yield [pos,pos+1]
            else:
                break
            
    def getTrackName(self):
        maintype = 'Independent' if self.interProb == 1 else 'Clustered'
        if self.interProb == 1:
            params = 'avgDist%i' % (1.0/self.interRate)
        else:
            params = 'avgInClustDist%i_avgBetClustDist%i_clustProb%.2f' % ((1.0/self.intraRate), (1.0/self.interRate), self.interProb)
        return ['Sample data','Simulated','Points',maintype,params]

class PointIter(ElIter):
    def __init__(self, genome, chr, interRate, intraRate, interProb):
        self.genome, self.chr = genome, chr
        self.interRate, self.intraRate, self.interProb  = float(interRate), float(intraRate), float(interProb)
        assert interProb > 0

    def __iter__(self):
        from proto.RSetup import r
        pos = 0
        maxPos = self._getChrLen()
        while True:
            if r.runif(1) < self.interProb:
                pos += int( max(1,r.rexp(1,self.interRate)))
            else:
                pos += int( max(1,r.rexp(1,self.intraRate)))

            if pos < maxPos:
                yield [pos,pos+1]
            else:
                break

    def getTrackName(self):
        maintype = 'Independent' if self.interProb == 1 else 'Clustered'
        if self.interProb == 1:
            params = 'avgDist%i' % (1.0/self.interRate)
        else:
            params = 'avgInClustDist%i_avgBetClustDist%i_clustProb%.2f' % ((1.0/self.intraRate), (1.0/self.interRate), self.interProb)
        return ['Sample data','Simulated','Points',maintype,params]


    
class SegIter(PointIter):
    def __init__(self, genome, chr, interRate, intraRate, interProb, minSegLen, maxSegLen):
        PointIter.__init__(self, genome, chr, interRate, intraRate, interProb)
        self.minSegLen, self.maxSegLen = int(minSegLen), int(maxSegLen)
        
    def __iter__(self):
        from proto.RSetup import r
        pos = 0
        maxPos = self._getChrLen()
        while True:
            #dist between segs
            if r.runif(1) < self.interProb:
                pos += int( max(1,r.rexp(1,self.interRate)))
            else:
                pos += int( max(1,r.rexp(1,self.intraRate)))
            start = pos
    
            #segLen
            pos+= int(r.runif(1,self.minSegLen, self.maxSegLen))
            end = pos
            
            if pos < maxPos:
                yield [start,end]
            else:
                break
            
    def getTrackName(self):
        pointBasedName = PointIter.getTrackName(self)
        pointBasedName[1] = 'Segments'
        pointBasedName[3] += '_segLen%ito%i' % (self.minSegLen, self.maxSegLen)
        return pointBasedName
    
class FunctionIterOneLevel(ElIter):
    def __init__(self, genome, chr, a, b, s):
        self.genome, self.chr = genome, chr
        self.a, self.b, self.s = float(a), float(b), float(s)
        self.repeatTimes = 1
        
    def __iter__(self):
        from proto.RSetup import r
        a, b, s = self.a, self.b, self.s
        
        val = r.rnorm(1,a,1.0*s/(1-b**2)**0.5 )
                                      
        #for i in xrange(self._getChrLen() ):
        assert self.repeatTimes >= 1
        chrLen = self._getChrLen() 
        i = 0
        while True:
            for rep in xrange(self.repeatTimes):
                yield val
                i+=1
                if i >= chrLen:
                    return
            
            e = r.rnorm(1,0,s)
            val = a + b*(val-a) + e
    
    def getTrackName(self):
        maintype = 'OneLevel'
        params = 'a%.1f_b%.3f_s%.1f' % (self.a, self.b, self.s)
        return ['Sample data','Simulated','Function',maintype,params]
    
class FunctionIterOneLevelAtPlatou(FunctionIterOneLevel):
    "Like FunctionIterOneLevel, but gives the same value many times. Is really a step function disguised as a function for ad hoc convenience reasons.."
    def __init__(self, genome, chr, a, b, s, repeatTimes):
        FunctionIterOneLevel.__init__(self, genome, chr, a, b, s)
        self.repeatTimes = int(repeatTimes)

    def getTrackName(self):
        tn = FunctionIterOneLevel.getTrackName(self)
        tn[-1] += '_rep%i' % self.repeatTimes
        return tn
        
class PointSampledByIntensityIter:
    def __init__(self, genome, chr, trackName1, factor, outTrackNamePart):
        self.trackName1, self.genome, self.chr = \
            trackName1.split(':'), genome, chr
        self.outTrackNamePart = outTrackNamePart
        self.factor = float(factor)
        assert self.factor<1
        
    def __iter__(self):
        from proto.RSetup import r
        chr = self.chr
        trackName1, genome = self.trackName1, self.genome
        factor = self.factor
        region = GenomeRegion(genome, chr, 0, GenomeInfo.getChrLen(genome, chr) )

        track1 = PlainTrack(trackName1)
        tv1 = track1.getTrackView(region)
        vals1 = tv1.valsAsNumpyArray()
        
        #scale between 0 and 1..:
        minVal, maxVal = vals1.min(), vals1.max()
        vals1 = (vals1 - minVal) * (1/(maxVal-minVal))
        for pos in xrange(len(vals1)):
            #print r.runif(1), vals1[pos]
            if r.runif(1) < factor*vals1[pos]:
                yield [pos,pos+1]

    def getTrackName(self):
        return ['Sample data','Simulated','Points','ByIntensity', self.outTrackNamePart]

class TrackCombinerIter:
    def __init__(self, genome, chr, trackName1, trackName2, w1, w2, outTrackName):
        self.trackName1, self.trackName2, self.w1, self.w2, self.genome, self.chr = \
            trackName1.split(':'), trackName2.split(':'), float(w1), float(w2), genome, chr
        self.outTrackName = outTrackName.split(':')

    def getTrackName(self):
        return self.outTrackName
    
    #def __iter__(self):
    #    for chr in GenomeInfo.getChrList(self.genome):
    #        for val in self.combineTracksAtChr(chr):
    #            yield val
                        
class FunctionTrackCombinerIter(TrackCombinerIter):
    #def combineTracksAtChr(self, chr):#, trackName1, trackName2, w1, w2, genome, chr):
    def __iter__(self):
        chr = self.chr
        trackName1, trackName2, w1, w2, genome = self.trackName1, self.trackName2, self.w1, self.w2, self.genome
        
        region = GenomeRegion(genome, chr, 0, GenomeInfo.getChrLen(genome, chr) )

        track1 = PlainTrack(trackName1)
        tv1 = track1.getTrackView(region)
        vals1 = tv1.valsAsNumpyArray()
        
        track2 = PlainTrack(trackName2)
        tv2 = track2.getTrackView(region)
        vals2 = tv2.valsAsNumpyArray()
        
        for i in xrange(len(vals1)):
            yield w1*vals1[i] + w2*vals2[i]
    
class SimulationManager:
    @classmethod
    def createGwTrack(cls, genome, iterClass, *iterParams):
        for chr in GenomeInfo.getChrList(genome):
            cls.createChrTrack(genome, chr, iterClass, *iterParams)
            
    @staticmethod
    def createChrTrack(genome, chr, iterClass, *iterParams):
        
        iter = iterClass(genome, chr, *iterParams)
        
        
        if iterClass == PointIter:
            writerClass = OrigPointBedWriter
        elif iterClass == SegIter:
            writerClass = OrigBedWriter
        elif iterClass == FunctionIterOneLevel:
            writerClass = OrigWigFixedWriter
        elif iterClass == FunctionTrackCombinerIter:
            writerClass = OrigWigFixedWriter
        elif iterClass == PointSampledByIntensityIter:
            writerClass = OrigPointBedWriter
        elif iterClass == FunctionIterOneLevelAtPlatou:
            writerClass = OrigWigFixedWriter            
        else:
            raise AssertionError
        
        writerClass.writeChr(genome, chr, iter.getTrackName(), iter)
        
if __name__ == '__main__':
    if not len(sys.argv) >= 4:
        print 'syntax: python SimulationTools genome chr iterClass [iterParams..]'
        print 'supported iterClasses with params:'
        print 'python SimulationTools genome PointIter interRate intraRate interProb'
        print 'python SimulationTools genome SegIter interRate intraRate interProb minSegLen maxSegLen'
        print 'python SimulationTools genome FunctionIterOneLevel a b s'
        print 'python SimulationTools genome FunctionIterOneLevelAtPlatou a b s repeatTimes'
        print 'python SimulationTools genome FunctionTrackCombinerIter trackName1 trackName2 w1 w2 outTN'
        print 'python SimulationTools genome PointSampledByIntensityIter trackName1 factor outTNPart'
        
        sys.exit()
        
    genome, iterClassName = sys.argv[1:3]
    iterClass = globals()[iterClassName]
    
    iterParams = sys.argv[3:]
    
    SimulationManager.createGwTrack( genome, iterClass, *iterParams)

class SimulationPointIter:
    @classmethod
    def createGwTrack(cls, genome, iterClass, outFn, paramInterRate, paramIntraRate, paramInterProb):
        for chr in GenomeInfo.getChrList(genome):
            cls.createChrTrack(genome, chr, iterClass, outFn, paramInterRate, paramIntraRate, paramInterProb)
            
    @staticmethod
    def createChrTrack(genome, chr, iterClass, outFn, paramInterRate, paramIntraRate, paramInterProb, chrMin, chrMax):
        iter = PointIterInterval(genome, chr, paramInterRate, paramIntraRate, paramInterProb, chrMin, chrMax)
        writerClass = OrigPointBedWriter
        writerClass.writeChrAdd(genome, chr, 'trackName', iter, outFn)




#def createClusteredPointTrack(outFn, interRate, intraRate):
#    pos = 0
#    maxPos = 247249719#GenomeInfo.getChrLen('hg18','chr1')
#    outF = open(outFn,'w')
#    while True:
#        pos += int( max(1,r.rexp(1,interRate)))
#        if pos >= maxPos:
#            return
#        outF.write( '\t'.join([str(x) for x in ['chr1',pos,pos+1] ]) +os.linesep)
#        
#        for i in range(2):
#            pos+=int( max(1,r.rexp(1,intraRate)))
#            if pos >= maxPos:
#                return
#            outF.write( '\t'.join([str(x) for x in ['chr1',pos,pos+1] ]) +os.linesep)
#            
#def createSegTrack(outFn, interRate, meanSegLen, sdSegLen):
#    pos = 0
#    outF = open(outFn,'w')
#    maxPos = 247249719#GenomeInfo.getChrLen('hg18','chr1')
#
#    while True:
#        pos += int( max(1,r.rexp(1,interRate)))
#        length = max( int(r.rnorm(1,meanSegLen, sdSegLen)), 2)
#        if pos+length >maxPos:
#            return
#        outF.write( '\t'.join([str(x) for x in ['chr1',pos,pos+length] ]) +os.linesep)
#        pos+=length
#
#def createFuncTrack(outFn, mean, sd):
#    ensurePathExists(outFn)
#    outF = open(outFn,'w')
#    outF.write('track type=wiggle_0'+os.linesep)
#    outF.write('\t'.join(['fixedStep','chrom=chr1','start=1','step=1']) +os.linesep)
#    chunkSize= 10**6
#    randVals = []
#    
#    for pos in xrange(247249719):
#        if len(randVals)==0:
#            randVals = r.rnorm(chunkSize,mean,sd)
#            print '.',
#        outF.write('%.3f' % randVals.pop() + os.linesep)
#        
#def createFuncByConcatingReal(outFn, inFn1, inFn2):
#    ensurePathExists(outFn)
#    outF = open(outFn,'w')
#    outF.write('track type=wiggle_0'+os.linesep)
#    outF.write('\t'.join(['fixedStep','chrom=chr1','start=1','step=1']) +os.linesep)
#    wantedChrSize = 247249719
#    chrSizeCount=0
#    for fn in [inFn1, inFn2]:
#        headerCount=2
#        for line in open(fn):
#            if headerCount>0:
#                headerCount-=1
#                continue
#        
#            outF.write(line)
#            chrSizeCount+=1
#            if chrSizeCount>=wantedChrSize:
#                return
#    
#createFuncTrack('/xanadu/project/rrresearch/standardizedTracks/hg18/Simulated/Function/normMean50Sd10',50,10)
#createFuncByConcatingReal('/xanadu/project/rrresearch/standardizedTracks/hg18/Simulated/Function/FromOtherRealChroms/vals.wig' ,'/xanadu/project/rrresearch/standardizedTracks/hg18/DNA Structure/DNA melting/Meltmap/chr1.dat.wig','/xanadu/project/rrresearch/standardizedTracks/hg18/DNA Structure/DNA melting/Meltmap/chr2.dat.wig')
#createClusteredPointTrack('/Users/sandve/Desktop/simulated/points_expMean100_3clusteredMean10.point.bed',0.01,0.1)
#createClusteredPointTrack('/Users/sandve/Desktop/simulated/points_expMean100.point.bed',0.01,0.01)
#createSegTrack('/Users/sandve/Desktop/simulated/segs_distExpMean200_lenNormMean50Sd10.bed', 0.005, 50,10)
#createSegTrack('/Users/sandve/Desktop/simulated/distExpMean200_lenNormMean30Sd5.bed', 0.005, 30,5)
#createSegTrack('/Users/sandve/Desktop/simulated/distExpMean50_lenNormMean10Sd2.bed', 0.02, 10,2)
#createSegTrack('/Users/sandve/Desktop/simulated/distExpMean50_lenNormMean5Sd1.bed', 0.02, 5,1)
