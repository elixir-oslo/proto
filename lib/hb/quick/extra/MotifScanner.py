from third_party.MotifTools import Motif
from third_party.Fasta import load

class MotifScanner(object):
    def __init__(self, fn, fn2=None, fastaFn=None):
        from quick.webtools.tfbs.TestOverrepresentationOfPwmInDna import parseTransfacMatrixFile
        
        self.fastaFn = fastaFn
        self.countMatrices = parseTransfacMatrixFile(fn)
        if fn2:
            temp = parseTransfacMatrixFile(fn2)
            self.countMatrices.update(temp)
    
    def scanMotifInSequence(self, motifId, fastaFn=None):
        if fastaFn:
            self.fastaFn = fastaFn
        motif = Motif(backgroundD={'A': 0.25, 'C': .25, 'G': .25, 'T': .25} )
        motif.compute_from_counts(self.countMatrices[motifId],0.1)
        motif.name = motifId
        seqs = load(self.fastaFn,lambda x:x)
        bestScores = [motif.bestscore(seq.upper()) for seq in seqs.values()]
            
        return dict([(str(key),score) for key,score in zip(seqs.keys(), bestScores)])
    
    def scanMotifInTwoSequences(self, motifId, fastaFn, mutFastFn ):
        if fastaFn:
            self.fastaFn = fastaFn
        motif = Motif(backgroundD={'A': 0.25, 'C': .25, 'G': .25, 'T': .25} )
        motif.compute_from_counts(self.countMatrices[motifId],0.1)
        motif.name = motifId
        seqs = load(self.fastaFn,lambda x:x)
        mSeqs = load(mutFastFn,lambda x:x)
        #print seqs.keys(), sorted(seqs)
        #print mSeqs.keys(), sorted(mSeqs)
        bestScores = [motif.dualBestScoreSeqEnd(seqs[key].upper(), mSeqs[key].upper()) for key in seqs]
            
        return dict([(str(key),score) for key,score in zip(seqs.keys(), bestScores)])
    
    def scanMotifInSequenceWithTreshold(self, motifId, fastaStr=None):
        
        motif = Motif(backgroundD={'A': 0.25, 'C': .25, 'G': .25, 'T': .25} )
        motif.compute_from_counts(self.countMatrices[motifId],0.1)
        motif.name = motifId
        seqs = loadFastFromStr(self.fastaFn)
        for key, seq in seqs.items():
            yield (key, seqs, motif.scan(seq.upper()))
            
        #return dict([(str(key),score) for key,score in zip(seqs.keys(), bestScores)])

    def loadFastFromStr(fastaStr):
        D = {}
        chunks = FH.read().split('>')
        for chunk in chunks[1:]:
            lines  = chunk.split('\n')
            raw_id = lines[0].replace(' ','_')
            seq    = ''.join(lines[1:])
            D[key] = seq
        return D