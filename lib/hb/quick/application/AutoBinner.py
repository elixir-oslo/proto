#should be moved to tested, with tests developed
#binLen of -1 gives whole chromosomes as bins
from quick.util.GenomeInfo import GenomeInfo 
from gold.track.GenomeRegion import GenomeRegion

class AutoBinner(object):
    def __init__(self, userBinSource, binLen, genome=None):
        self.genome = userBinSource.genome if hasattr(userBinSource, 'genome') else genome
        
        #if region.chr == None:
        #    assert( (not region.start) and (not region.end) )
        #    self.chromosomes = GenomeInfo.getChrList(self.genome)
        #    
        #else:
        #    self.chromosomes = [region.chr]
        #if not region.start:
        #    self.start = 0
        #else:
        #    self.start = region.start
        #
        #self.end = region.end
        self._userBinSource = userBinSource
        self._binLen = binLen

    def __iter__(self):
        return self.nextBin()
    
    def nextBin(self):
        #start = self.start
        #for chr in self.chromosomes:
        #    if self.genome:
        #        chrLen = GenomeInfo.getChrLen(self.genome, chr)
        #    else:
        #        chrLen = self.end
        #        assert chrLen is not None
        #    
        #    if self.end is None:
        #        chrEnd = chrLen
        #    else:
        #        chrEnd = min(self.end, chrLen)
        #    #chrLen = 3100000
        #    
        #    while (start < chrEnd):
        #        if self.binLen is not None:
        #            end = min(start+self.binLen, chrEnd)
        #        else:
        #            end = chrEnd
        #        #print 'YIELDING: ',start, end, chrEnd
        #        yield GenomeRegion(self.genome, chr, start, end)
        #        if self.binLen is not None:
        #            start += self.binLen
        #        else:
        #            start = chrLen
        #
        #    #in case of more chromosomes, reset start:
        #    start = 0
        for region in self._userBinSource:
            start = region.start if region.start is not None else 0

            chrLen = GenomeInfo.getChrLen(region.genome, region.chr) if region.genome is not None else None
            regEnd = min([x for x in [region.end, chrLen] if x is not None])
            
            if self._binLen is None:
                yield GenomeRegion(region.genome, region.chr, start, regEnd)
            else:
                while start < regEnd:
                    end = min(start + self._binLen, regEnd)
                    yield GenomeRegion(region.genome, region.chr, start, end)
                    start += self._binLen

    def __len__(self):
        return sum(1 for bin in self)        
