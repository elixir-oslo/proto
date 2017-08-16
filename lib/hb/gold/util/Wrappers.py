from gold.origdata.GenomeElementSource import GenomeElementSource

class PositionIterGESource(GenomeElementSource):
    _hasOrigFile = False

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)
        
    def __init__(self, positionIter, genome, trackName, chr):
        GenomeElementSource.__init__(self, None, genome=genome, trackName=trackName)
        self._positionIter = positionIter
        self._genomeElement.chr = chr

    def __iter__(self):
        for pos in self._positionIter:
            self._genomeElement.start = pos
            yield self._genomeElement
    
    def getPrefixList(self):
        return ['start']
        
    def hasNoOverlappingElements(self):
        return True


class LowerOrderChainWrapper(object):
    def __init__(self, lowerOrderChain, nmerPrefix, fullNmer, genome, chr):
        self._lowerOrderChain = lowerOrderChain
        self._fullNmer = fullNmer
        self._nmerPrefix = nmerPrefix
        self._genome = genome
        self._chr = chr
        
    def __iter__(self):
        for pos in self._lowerOrderChain:
            from gold.track.Track import PlainTrack
            from quick.util.GenomeInfo import GenomeInfo
            from gold.track.GenomeRegion import GenomeRegion
            
            track = PlainTrack( GenomeInfo.getSequenceTrackName(self._genome) )
            region = GenomeRegion(self._genome, self._chr, pos, pos+len(self._fullNmer) )
            fullSubstring = (''.join(track.getTrackView(region).valsAsNumpyArray() )).lower()
            pl = len(self._nmerPrefix)
            assert self._fullNmer[0:pl] == fullSubstring[0:pl], 'The prefix of lower order does not match at the positions given by the chain. %s vs %s. Region: %s' % ( self._fullNmer[0:pl], fullSubstring[0:pl], region )
            #print 'Comparing nmers: %s VS %s (at pos:%i).' % (self._fullNmer, fullSubstring, pos)
            if self._fullNmer == fullSubstring:
                yield pos
