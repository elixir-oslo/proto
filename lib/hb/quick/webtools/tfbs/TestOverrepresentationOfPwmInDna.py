import math
import os
from itertools import combinations

from quick.webtools.GeneralGuiTool import GeneralGuiTool
from third_party.Fasta import load
from third_party.MotifTools import Motif


class TestOverrepresentationOfPwmInDna(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Test overrepresentation of PWM in DNA"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        #can have two syntaxes: either a list of stings or a list of tuples where each tuple has two items(Name of box on webPage, name of getOptionsBox)
        return ['Motifs (Transfac PWMs)', 'Observed fasta sequence', 'Random sequences', 'Test statistic']

    @staticmethod    
    def getOptionsBox1():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return ('__history__',)
    
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return ('__history__','fasta')
    
        
    @staticmethod    
    def getOptionsBox3(prevChoices):
        return ('__history__',)

    @staticmethod    
    def getOptionsBox4(prevChoices):
        return ['Average of max score per sequence','Sum of scores across all positions of all sequences','Score of Frith et al. (2004)', 'Product of max per sequence']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        from time import time
        startTime = time()
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile

        motifFn = ExternalTrackManager.extractFnFromGalaxyTN( choices[0].split(':'))
        observedFasta = ExternalTrackManager.extractFnFromGalaxyTN( choices[1].split(':'))

        randomGalaxyTN = choices[2].split(':')
        randomName = ExternalTrackManager.extractNameFromHistoryTN(randomGalaxyTN)
        randomGalaxyFn = ExternalTrackManager.extractFnFromGalaxyTN( randomGalaxyTN)
        randomStatic = GalaxyRunSpecificFile(['random'],randomGalaxyFn) #finds path to static file created for a previous history element (randomFn), and directs to a folder containing several files..
        #print os.listdir(randomStatic.getDiskPath())
        randomFastaPath = randomStatic.getDiskPath()

        #motifFn, observedFasta, randomFastaPath = '/Users/sandve/egne_dokumenter/_faglig/NullModels/DnaSeqExample/liver.pwm', 'liver.fa', 'randomFastas'
        testStatistic = choices[3]
        if testStatistic == 'Average of max score per sequence':
            scoreFunc = scoreMotifOnFastaAsAvgOfBestScores
        elif testStatistic == 'Sum of scores across all positions of all sequences':
            scoreFunc = scoreMotifOnFastaAsSumOfAllScores
        elif testStatistic == 'Score of Frith et al. (2004)':
            scoreFunc = lr4
        elif testStatistic == 'Product of max per sequence':
            scoreFunc = scoreMotifOnFastaAsProductOfBestScores
        else:
            raise
        
        pvals = mcPvalFromMotifAndFastas(motifFn, observedFasta, randomFastaPath, scoreFunc)
        print 'Pvals for motifs (%s) against observed (%s) vs random (%s - %s) sequences.' % (motifFn, observedFasta, randomName, randomFastaPath)
        for motif,pval in sorted(pvals.items()):
            print motif+'\t'+('%.4f'%pval)
            
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
        from proto.RSetup import robjects
        histStaticFile = GalaxyRunSpecificFile(['pvalHist.png'],galaxyFn)
        #histStaticFile.openRFigure()
        histStaticFile.plotRHist(pvals.values(), [x/40.0 for x in range(41)], 'Histogram of p-values', xlim=robjects.FloatVector([0.0, 1.0]))
        #r.hist(robjects.FloatVector(pvals.values()), breaks=robjects.FloatVector([x/40.0 for x in range(41)]), xlim=robjects.FloatVector([0.0, 1.0]), main='Histogram of p-values' )
        #histStaticFile.closeRFigure()
        print histStaticFile.getLink('Histogram')
        print 'Time (s):', time()-startTime
        
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        return None
    
    #@staticmethod
    #def isPublic():
    #    return False
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    #@staticmethod
    #def isHistoryTool():
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    return []
    #
    #@staticmethod
    #def getToolDescription():
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
    #
    #@staticmethod    
    #def getOutputFormat(choices):
    #    '''The format of the history element with the output of the tool.
    #    Note that html output shows print statements, but that text-based output
    #    (e.g. bed) only shows text written to the galaxyFn file.
    #    '''
    #    return 'html'
    #


def parseTransfacMatrixFile(fn):
    'Parses a transfac file into a dict of ID->CountMatrix. CountMatrix is in the form of a list of columns, where each column is a dict from acgt to corresponding count values for that column.'
    countMats = []
    for line in open(fn):
        if line.startswith('>'):
            countMats.append([line[1:].strip(), []])
        else:
            countMats[-1][1].append( dict(zip('ACGT',[float(x) for x in line.split()]) ) )
            assert len(countMats[-1][1][-1])==4
    
    return dict(countMats)
        
def scoreMotifOnFastaAsSumOfAllScores(motif, fastaFn, verbose=False):
    seqs = load(fastaFn,lambda x:x)
    concatSeq = ''.join(seqs.values()).upper()
    
    score = motif.scansum(concatSeq)[3]
    #print 'Sum score: ', score
    return score    

def scoreMotifOnFastaAsAvgOfBestScores(motif, fastaFn, verbose=False):
    seqs = load(fastaFn,lambda x:x)
    #concatSeq = ''.join(seqs.values()).upper()
    #print motif.ll
    #print motif.bestscore(seqs[0]), motif.bestscanseq(seqs[0]), motif._scan(seqs[0])
    bestScores = [motif.bestscore(seq.upper()) for seq in seqs.values()]
    score = 1.0*sum(bestScores) / len(seqs)
    if verbose:
        print 'Best-scores per seq for motif %s: %s' % (motif.name, bestScores)
    return score    

def scoreMotifOnFastaAsProductOfBestScores(motif, fastaFn, verbose=False):
    seqs = load(fastaFn,lambda x:x)
    #concatSeq = ''.join(seqs.values()).upper()
    #print motif.ll
    #print motif.bestscore(seqs[0]), motif.bestscanseq(seqs[0]), motif._scan(seqs[0])
    bestScores = [motif.bestscore(seq.upper()) for seq in seqs.values()]
    score = 1.0*reduce(lambda x,y:x*y, bestScores) 
    if verbose:
        print 'Best-scores per seq for motif %s: %s' % (motif.name, bestScores)
    return score    

def mcPvalFromMotifAndFastas(motifFn, observedFasta, randomFastaPath, scoreFunc):
    countMats = parseTransfacMatrixFile(motifFn)
    from gold.application.StatRunner import Progress
    progress = Progress(len(countMats))        
    
    pvals = {}
    for motifId, countMat in countMats.items():
        motif = Motif(backgroundD={'A': 0.25, 'C': .25, 'G': .25, 'T': .25} )
        motif.compute_from_counts(countMat,0.1)
        motif.name = motifId
    
        obsScore = scoreFunc(motif, observedFasta, verbose=False)
        
        randomScores = []
        for relFn in os.listdir(randomFastaPath):
            fn = randomFastaPath + os.sep + relFn
            randomScores.append( scoreFunc(motif, fn) )
        #print motifId
        #print obsScore
        #print randomScores
        pvals[motifId] = float(1+sum([x>=obsScore for x in randomScores])) / (1+ len(randomScores))
        progress.addCount()
    
    return pvals

#LR2_CACHE = {} #Instead set in lr4, to ensure reset between fasta files..
def lr2(motif,sequence, seqId):
    cacheKey = (motif.name, seqId)
    if not cacheKey in LR2_CACHE:
        scanRes = motif.scansum(sequence)
        LR2_CACHE[cacheKey] = math.exp(scanRes[3])/scanRes[1]
    return LR2_CACHE[cacheKey]

def lr3(motif, sequenceDict, i):
    combCount = 0
    score = 0
    seqIds = sequenceDict.keys()
    for seqComb in combinations(seqIds,i):
        score += reduce(lambda x,y:x*y, [lr2(motif,sequenceDict[seqId], seqId) for seqId in seqComb])
        combCount += 1
    return 1.0*score/combCount

def lr4(motif, fastaFn, verbose=False):
    global LR2_CACHE
    LR2_CACHE = {} 
    sequenceDict = load(fastaFn)
    for id in sequenceDict:
        sequenceDict[id] = sequenceDict[id].upper()
        
    score = sum( lr3(motif, sequenceDict, i) for i in range(1,len(sequenceDict)+1))
        
    return math.log(1.0*score/len(sequenceDict))
        
#motifFn, observedFasta, randomFastaPath = '/Users/sandve/egne_dokumenter/_faglig/NullModels/DnaSeqExample/liver.pwm', 'liver.fa', 'randomFastas'    
#pvals = mcPvalFromMotifAndFastas(motifFn, observedFasta, randomFastaPath)
#print 'Pvals for motifs (%s) against observed (%s) vs random (%s) sequences.' % (motifFn, observedFasta, randomFastaPath)
#for motif,pval in sorted(pvals.items()):
#    print motif+'\t'+('%.4f'%pval)
