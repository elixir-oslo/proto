class NmerTools:
    @classmethod
    def allNmers(cls, n):
        for i in xrange(4**n):
            yield cls.intAsNmer(i, n)
        
    @staticmethod
    def nmerAsInt(nmer):
        bpDict = dict( zip('acgt', range(4)) )
        revNmer = list(reversed(nmer.lower()))
        return sum( 4**i * bpDict[revNmer[i]] for i in range(len(revNmer)) )

    @staticmethod
    def intAsNmer(val, n):
        bpRevDict = dict( zip(range(4), 'acgt') )
        nmer = ''
        while val>0:
            nmer = bpRevDict[val%4] + nmer
            val = val/4
        nmer = bpRevDict[0]*(n-len(nmer)) + nmer #pad a's to beginning..
        return nmer

    @staticmethod
    def isNmerString(nmer):
        import re
        nmer = nmer.strip()
        return re.search('[^acgtACGT]', nmer) is None
        
    @staticmethod
    def getNotNmerErrorString(nmer):
        return 'Nmer contains symbols other than a, c, g, t, A, C, G or T: ' + nmer
        
    @staticmethod
    def getNmerAndCleanedNmerTrackName(genome, trackName):
        from quick.util.GenomeInfo import GenomeInfo
        from copy import copy
        tn = copy(trackName)
        tn[-1] = tn[-1].lower()
        nmer = tn[-1]
        if len(tn) == len(GenomeInfo.getNmerTrackName(genome)) + 1:
            tn = tn[0:-1] + [str(len(nmer))+'-mers'] + tn[-1:]
        return nmer, tn
