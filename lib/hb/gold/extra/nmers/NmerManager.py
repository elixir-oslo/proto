#!/usr/bin/env python

#from quick.util.Wrappers import FuncValTvWrapper
from config.Config import NMER_CHAIN_DATA_PATH
from gold.extra.nmers.NmerAsIntSlidingWindow import NmerAsIntSlidingWindow
from gold.extra.nmers.NmerTools import NmerTools
from gold.extra.nmers.SameValueIndexChains import SameValueIndexChainsFactory
from gold.origdata.PreProcessTracksJob import PreProcessCustomTrackJob
from gold.track.GenomeRegion import GenomeRegion
from gold.track.Track import PlainTrack
from gold.util.CustomExceptions import EmptyGESourceError
from gold.util.Wrappers import PositionIterGESource, LowerOrderChainWrapper
from quick.util.GenomeInfo import GenomeInfo

import sys
import os

class NmerManager(object):
    GE_SOURCE = PositionIterGESource

    def __init__(self, genome):
        self._genome = genome
        self._prefixList = None
        self._chains = None
        self._curChr = None
    
    def createNmerChains(self, n):
        for chr in GenomeInfo.getChrList(self._genome):
            print 'Creating chains of nmers of length ', n, ' for chromosome ', chr
            chrLen = GenomeInfo.getChrLen(self._genome,chr)
            chrReg = GenomeRegion( self._genome, chr, 0, chrLen )
            seqTV = PlainTrack( GenomeInfo.getSequenceTrackName(self._genome) ).getTrackView(chrReg)
            
            #nmersAsInts = NmerAsIntSlidingWindow(n, FuncValTvWrapper(seqTV))
            nmersAsInts = NmerAsIntSlidingWindow(n, seqTV.valsAsNumpyArray())
            SameValueIndexChainsFactory.generate( nmersAsInts, chrLen, 4**n, self._createPath(n), chr )
        
            
    def _createNmerTrack(self, nmerList, lowerOrder=None):
        nmerLengths = list(set([len(nmer) for nmer in nmerList]))
        assert len(nmerLengths)==1
        
        chainOrder = lowerOrder if lowerOrder is not None else nmerLengths[0]
        
        regionList = GenomeInfo.getStdChrRegionList(self._genome)
        
        for region in regionList:
            print '|',
            
            chains = SameValueIndexChainsFactory.load(self._createPath(chainOrder), region.chr)
            
            for nmer in nmerList:
                if len(nmerList) > 1:
                    print '.',
                
                if lowerOrder is not None:
                    nmerPrefix = nmer[0:chainOrder]
                    rawIndexGenerator = chains.getIndexGenerator(NmerTools.nmerAsInt(nmerPrefix))             
                    indexGenerator = LowerOrderChainWrapper(rawIndexGenerator, nmerPrefix, nmer, self._genome, region.chr)
                else:
                    indexGenerator = chains.getIndexGenerator(NmerTools.nmerAsInt(nmer)) 
        
                #print 'Length of lower order chain: %i and %i' % (sum(1 for x in indexGenerator), sum(1 for x in indexGenerator))
                #print 'Length of wrapped chain: %i and %i' % (sum(1 for x in wrappedIndexGenerator), sum(1 for x in wrappedIndexGenerator))            
                
                PreProcessCustomTrackJob(self._genome, self._createTrackName(nmer), [region], \
                                         self._getNmerGeSourceForChr, finalize=False, preProcess=True, \
                                         indexGenerator=indexGenerator).process()
                    
        for nmer in nmerList:
            try:
                PreProcessCustomTrackJob(self._genome, self._createTrackName(nmer), regionList, \
                                         self._getNmerGeSourceForChr, preProcess=False, finalize=True, \
                                         indexGenerator=[0]).process()
            except EmptyGESourceError:
                PreProcessCustomTrackJob(self._genome, self._createTrackName(nmer), [GenomeRegion(self._genome, regionList[0].chr, -1, 0)], \
                                         self._getNmerGeSourceForChr, preProcess=True, finalize=True, \
                                         indexGenerator=[-1]).process()
        
        return
        
    def _getNmerGeSourceForChr(self, genome, trackName, region, indexGenerator):
        return self.GE_SOURCE(indexGenerator, genome, trackName, region.chr)
    
    def createNmerTrack(self, nmer):
        self._createNmerTrack([nmer])

    def createNmerTracks(self, n):
        print 'Creating tracks for nmers of length ', n        
        self._createNmerTrack(list(NmerTools.allNmers(n)))

    def nmerChainExists(self, n):
        return os.path.exists( self._createPath(n) )
    
    def getHighestExistingChainOrderLessThanN(self, n):
        for k in range(n,0,-1):
            if self.nmerChainExists(k):
                return k
        return None
    
    def createNmerTrackFromLowerOrderChain(self, fullNmer, chainOrder):
        print 'Using nmer prefix (%s) as seed. ' % fullNmer[0:chainOrder]
        self._createNmerTrack([fullNmer], chainOrder)
    
    def _createTrackName(self, nmer):
        return GenomeInfo.getNmerTrackName(self._genome) + [str(len(nmer)) + '-mers', nmer]
    
    def _createPath(self, n):
        return os.sep.join([NMER_CHAIN_DATA_PATH, self._genome, str(n)])

#NmerManager('sacCer1').createNmerTrack('ac')

if __name__ == "__main__":
    if not len(sys.argv) == 4:
        print 'Syntax: NmerManager.py chains|tracks genome n|nMin-nMax'
    else:
        mode, genome, nSpec= sys.argv[1:]        
        if '-' in nSpec:
            nSpec = nSpec.split('-')
            nMin, nMax = int(nSpec[0]), int(nSpec[1])+1
            allNs = range(nMin, nMax)
        else:
            allNs = [int(nSpec)]
        
        for n in allNs:
            if mode == 'chains':
                NmerManager(genome).createNmerChains(n)
            elif mode == 'tracks':
                NmerManager(genome).createNmerTracks(n)
            else:
                print 'Invalid option..'
                break
    
