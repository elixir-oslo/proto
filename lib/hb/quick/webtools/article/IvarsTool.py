import numpy as np

from gold.description.AnalysisDefHandler import AnalysisDefHandler
from gold.description.AnalysisList import REPLACE_TEMPLATES
from gold.track.GenomeRegion import GenomeRegion
from gold.track.Track import PlainTrack
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.SummarizedInteractionWithOtherTracksStat import SummarizedInteractionWithOtherTracksStatUnsplittable
from quick.webtools.GeneralGuiTool import MultiGeneralGuiTool, GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin

# This is a template prototyping GUI that comes together with a corresponding
# web page.

snps = [[] for chromosome in range(0,25)]
peaks = [[] for chromosome in range(0,25)]
motif = None

BINDING_PROB_TRESHOLD = 0.5
BINDING_A_PRIORI_PROB = 0.01

class SNP():
    def __init__(self, chromosome, position, mutationFrom, mutationTo):
        self.chromosome = chromosome
        self.position = position
        self.mutationFrom = mutationFrom
        self.mutationTo = mutationTo
        
    def __repr__(self):
        return "Pos: %s %s - %s" % (self.position, self.mutationFrom, self.mutationTo)



"""
class Motif():
    sequence = ""
    sequence = [] # List of all possible sequences, with probability for each of them binding
    def __init__(self, sequence):
        self.sequence = sequence
        self.sequenceProbs = []
        
    def __repr__(self):
        return self.sequence

    # Returns the probability that for a given letter (A, C, G, T) at a given position
    def probabilityAtPosition(self, position, base):
        base = base.upper()
        if base not in ['A', 'G', 'C', 'T']:
            return 0

        return self.sequenceProbs[position][base.upper()]
    
    # Outdated: Returns the probability that a given motif sequence can bind
    # Current: Returns the probability of trans. fact. binding given sequence
    def probabilitySequence(self, sequence):
        sequence = list(sequence)
        i = 0
        prob = 1
        for s in sequence:
            prob *= self.probabilityAtPosition(i, s)
            i += 1

        a = BINDING_A_PRIORI_PROB
        transFacBindingProb = a * prob / (a * prob + (1-a) * 0.25**len(sequence))

            
        return transFacBindingProb
"""

            
# Builds the motif (stores all possible motif sequences with given probabilities            
def buildMotif(fastaFileObject, fastaFileContainsCnts = True):
    global motif
    f = fastaFileObject
    sequence = f.readline().split()[0].replace(">", "")
    motif = Motif(sequence)
    
    
    for line in f.readlines():
        probs = np.array([float(p) for p in line.split()])

        if not fastaFileContainsCnts:
            totalCnts = sum(probs)
            probs = probs / sum(probs)


        probDict = {"A": probs[0], "C": probs[1], "G": probs[2], "T": probs[3]}
    
        motif.sequenceProbs.append(probDict)



# Returns a tuple containing a list of all possible new sequences based on SNP mutations
# and a list of the positions that were mutated in order to create the new sequence
def newSequencesFromSnp(originalSequence, chromosome, start, end):
    # Simple case for now, only single mutations checked
    # TODO (Ivar 02.10.2015): Implement combinations of different mutations
    new = []
    mutations = []
    """
    posChanged = -1
    for snp in snps[chromosome]:
        if snp.position < end \
            and snp.position >= start:
            m = list(originalSequence)
            if m[snp.position - start].lower() != "n": # Do not change an n (not important)
                m[snp.position - start] = snp.mutationTo
                posChanged = snp.position
            new.append(''.join(m))
            
    return (new, posChanged)
    """
    
    # New way: Return all possible combinations of sequences from the possible SNPs
    # First: Get the list of all the relevant SNPs, and permute these
    relevantSnps = []
    for snp in snps[chromosome]:
        if snp.position < end and snp.position >= start:
            relevantSnps.append(snp)
    
    # Get combinations of SNPs
    from itertools import combinations
    snpCombinations = sum([map(list, combinations(relevantSnps, i))
                           for i in range(len(relevantSnps) + 1)], []) # Lazy one liner that gets combinations from relevantSnps
    

    
    for snpCombination in snpCombinations:
        mutationsHere = []
        m = list(originalSequence)
        for snp in snpCombination:
            mutationsHere.append(snp.position)
            if m[snp.position - start].lower() != "n": # Do not change an n (not important)
                m[snp.position - start] = snp.mutationTo

        newSequence = ''.join(m)
        if newSequence != originalSequence:
            new.append(''.join(m))

        mutations.append(mutationsHere)

        # print "New from " + originalSequence + ": " + ''.join(m)
    return (new, mutations)
        
    
def motifSearch(haystack, needle):
    
    possibleFoundPosition = -1
    
    for i in range(0, len(haystack) - len(needle) + 1):
        #print "Checking %d" % i
        possibleFoundPosition = i
        for j in range(i, i + len(needle)):
            if needle[j - i].lower() != haystack[j].lower() and needle[j - i] != "N":
                #print "  breaking at %d" % (j)
                break # Not found match starting at position i, try next
           
            if j == i + len(needle) - 1:
                # We have come to end without breaking, we have a match. Return
                return possibleFoundPosition
                # TODO (Ivar 02.10.2015): Return all found positions instead of only one
    return False
 
# Returns a "probability" that the motif (needle) will bind/fit in every possible position in the haystack sequence
# (Should do, but doesn't now: Also returns an overall probability that every possible motif binds anywhere in the haystack)
def motifProbabilitySearch(haystack, needle): 
    probs = []
    
    for i in range(0, len(haystack) - len(needle) + 1):
        probs.append(motif.probabilitySequence(list(haystack)[i:i + len(needle)]))
        
    return probs
        
class ChIPSeqSegment():
    
    
    def __init__(self, chromosome, start, end, sequence):
        self.chromosome = chromosome
        self.start = start
        self.end = end
        self.sequence = sequence
        
        self.hasSNP = False
        self.hasMotif = False # Has originally one or more motifs (before mutation)
        self.motifPosition = -1;
        self.motifPositions = []
        self.motifAfterMutation = False
        self.motifPositionAfterMutation = -1
        self.lostMotif = False
        self.replacedMotifOnSamePosition = False
        self.gainedMotif = False
        self.gainedMotifPosition = False
        self.gainedMotifPositions = []
        self.changedMotifPosition = False
        self.mutationPosition = []

        self.bindingsBeforeMutations = []
        self.bindingsAfterMutations = []
         
    def __repr__(self):
        return "Peak on chr%d [%d, %d]. Has snp: %d, hasMotif: %d, lostMotif: %d, changedMotifPosition: %d, gainedMotif: %d, gainedMotifPosition: %d" % \
                (self.chromosome, self.start, self.end, self.hasSNP, self.hasMotif, self.lostMotif, self.changedMotifPosition, self.gainedMotif, self.gainedMotifPosition)

    # Checks whether there are one or more SNPs inside this peak
    def checkSnpInside(self):
        for snp in snps[self.chromosome]:
            if snp.position >= self.start and snp.position < self.end:
                self.hasSNP = True
                
    def checkMotifInside(self):      

        #pos = motifSearch(self.sequence, motif.sequence)
        positions = motifProbabilitySearch(self.sequence, motif.sequence)
        i = 0
        for prob in positions:
            if prob > BINDING_PROB_TRESHOLD:
                self.hasMotif = True
                self.motifPositions.append([self.start + i, prob])

            #print "Has motif at position %d with prob %.3f" % (self.start + i, prob)
            i += 1
        """
        #print "Checking for motif %s in %s. Result: %d" % (motif.sequence, self.sequence, pos)

        if pos != False:
            self.hasMotif = True
            self.motifPosition = self.start + pos
        """


    




class IvarsTool(MultiGeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Ivars tool"


    @staticmethod
    def getSubToolClasses():
        return [TestTool, MutationsGeneRegulationGsuit, MatchTFsWithPWMs, PointsInTracksStat]


def chrToNum(chromosome):
    c = chromosome.replace("chr", "")
    if c == "X" or c == "x":
        c = 23
    if c == "Y" or c == "y":
        c = 24
        
    return int(c)


def initAnalysis(choices):
    print "Init analysis"
    global motif, snps, peaks
    # Process SNP file
    fileName = choices[0].split(":")[2] 
    f = open(fileName)
    for line in f.readlines():
        data = line.split()
        chromosome = chrToNum(data[0])
        position = int(data[1])
        mutation = data[3].split(">")
        
        snps[chromosome].append(SNP(chromosome, position, mutation[0], mutation[1]))
        
        
    # Add some fake mutations
    snps[1].append(SNP(1, 1708718, "C", "A"))
    snps[1].append(SNP(1, 1708720, "G", "C"))
    
    # Process ChIP-seq segment file
    fileName = choices[1].split(":")[2]  
    f = open(fileName)
    for line in f.readlines():
        data = line.split()
        chromosome = chrToNum(data[0])
        posFrom = int(data[1])
        posTo = int(data[2])
        sequence = data[10]
        
        peaks[chromosome].append(ChIPSeqSegment(chromosome, posFrom, posTo, sequence))
    
    
    # Process motif file
    fileName = choices[2].split(":")[2]
    f = open(fileName)
    buildMotif(f, False)
    #sequence = f.readline().split()[0].replace(">", "")
    #motif = Motif(sequence)
    #print "Motif: " + motif.sequence


# Contains information about specific binding of the motif to some sequence
# peak.sequence should equal sequence, except for when the sequence is a mutated sequence from peak.
class Binding:
    def __init__(self, position, probability, peak, sequence, posChanged):
        self.position = position
        self.probability = probability
        self.peak = peak
        self.sequence = sequence
        self.posChanged = posChanged

    def __repr__(self):

        mutations = ""
        relevantMutations = []
        if len(self.posChanged) > 0:
             # Only filter out those that actually are were the motif is binding
            for pos in self.posChanged:
                if pos >= self.position and pos < self.position + len(motif.sequence):
                    relevantMutations.append(pos)
            if len(relevantMutations) > 0:
                mutations = 'due to mutations at positions ' + ','.join([str(pos) for pos in relevantMutations])
            else:
                mutations = '(original binding, no mutations affected anything)'

        # Make a pretty sequence to display, where the binding positions are differently coloured, and mutations
        # are marked
        prettySequence = ""

        sequenceList = list(self.sequence)
        originalSequenceList = list(self.peak.sequence)
        rangeToShow = 10 # Number of bases outside the binding site we wish to include


        minBase = max(self.peak.start, self.position - rangeToShow)
        maxBase = min(self.peak.end, self.position + len(motif.sequence) + rangeToShow)

        for i in range(minBase, maxBase):
            posRelToSeq = i - self.peak.start # The position in the peak sequence (where 0 is the first base in the seq)
            #print "(" + str(posRelToSeq) + "<br>" + str(maxBase) + "<br>" + str(minBase) + "<br>" + self.sequence + "<br>" + self.peak.sequence + ")"
            base = sequenceList[posRelToSeq]
            baseHtml = base
            if i in relevantMutations:
                baseHtml = "<a title='Mutated from " + originalSequenceList[posRelToSeq] + "'><u>" + base + "</u></a>"

            if i >= self.position and i < self.position + len(motif.sequence):
                baseHtml = "<b>" + baseHtml + "</b>"

            prettySequence += baseHtml




        return "At pos %d with prob %.3f on sequence %s %s" % \
               (self.position, self.probability, prettySequence, mutations)




# Goes through all peaks, finds all bindings in this peak before and after mutations
def findMotifBindings():
    for chromosome in range(1, 3): #range(0,24):
        print "Finding bindings on chromosome %d" % (chromosome)
        for peak in peaks[chromosome]:
            peak.checkSnpInside()
            #peak.checkMotifInside()

            allPossibleSequences = []
            positionsChanged = []
            # Find all new motif binding positions, by checking all possible new sequences from mutations

            # First, append the original sequence
            allPossibleSequences.append(peak.sequence)
            positionsChanged.append([]) # No positions changed in the original

            # If peak has SNPs, add all possible mutated sequences
            if peak.hasSNP:
                (mutatedSequences, posChanged) = newSequencesFromSnp(peak.sequence, peak.chromosome, peak.start, peak.end)
                allPossibleSequences += mutatedSequences
                positionsChanged += posChanged


            # Iterate over all these sequences. For each, check if it leads to binding of motif
            j = 0



            for sequence in allPossibleSequences:

                newPositions = motifProbabilitySearch(sequence, motif.sequence)

                i = 0
                for prob in newPositions:
                    if prob > BINDING_PROB_TRESHOLD:
                        binding = Binding(i + peak.start, prob, peak, sequence, positionsChanged[j])

                        # This is either a binding happening after mutation, or before
                        if len(positionsChanged[j]) == 0:
                            #print "Adding peak before mutation at %d" % (i + peak.start)
                            # Before mutation
                            peak.bindingsBeforeMutations.append(binding)
                            peak.hasMotif = True
                        else:

                            # Do NOT add if there have been mutations, but they are not in the relevant area
                            doAdd = False
                            for pos in positionsChanged[j]:
                                if pos >= peak.start + i and pos < peak.start + i + len(motif.sequence):
                                    doAdd = True

                            if doAdd:
                                #print "Adding peak after mutation at %d" % (i + peak.start)
                                peak.bindingsAfterMutations.append(binding)


                    i += 1
                j += 1



def output():
    print "</pre>"
    for chromosome in range(1, 25):
        print "<h2>Chromosome %d:</h2>" % (chromosome)
        print "<p>In total %d ChIP-seq peak segments and %d SNPs</p>" % (len(peaks[chromosome]), len(snps[chromosome])) 
        print "<p>Peak segments where loss or gain of function happened:</p>"
        print """
        <table border='1' cellpadding='3'>
        <tr>
            <th>Chr</th>
            <th>Peak position</th>
            <th>Binding of transcription factors on original peak sequence</th>
            <th>Binding after SNP mutation of peak sequence</th>
            <th>Lost function due to mutation?</th>
            <th>Gained function due to mutation?</th>
        </tr>
        """
        
        for peak in peaks[chromosome]:
            # Only present peaks that either had motifs or gained motifs
            if len(peak.bindingsBeforeMutations) > 0 or len(peak.bindingsAfterMutations) > 0:

                print "<tr>"
                print "<td>Chr %d</td><td>%d-%d</td>" % (peak.chromosome, peak.start, peak.end);
                print "<td>"

                if peak.hasMotif > 0:
                    for binding in peak.bindingsBeforeMutations:
                        print binding
                        print "<br>"
                else:
                    print "No"
                print "</td>"


                print "<td>"
                if len(peak.bindingsAfterMutations) > 0:
                    for binding in peak.bindingsAfterMutations:
                        print binding
                        print "<br>"
                else:
                    if not peak.hasSNP:
                        print "No change, no mutations"
                    else:
                        print "No new bindings"
                print "</td>"

                print "<td>"
                # Lost function happens if mutation occurs and there are no new bindings other than the original after mutation
                if peak.hasSNP and peak.hasMotif and len(peak.bindingsAfterMutations) == 0:
                    print "<b>Yes</b>"
                else:
                    print "No"
                print "</td>"

                # Determine whether the peak gained a binding that it didn't have before
                gained = 0
                for newBinding in peak.bindingsAfterMutations:
                    found = 0
                    for oldBinding in peak.bindingsBeforeMutations:
                        if newBinding.position == oldBinding.position:
                            found += 1

                    if found == 0:
                        gained += 1

                print "<td>"
                if gained == 0:
                    print "No"
                else:
                    print "<b>Yes</b> (gained %d new bindings)" % (gained)
                print "</td>"

                """
                if peak.gainedMotif:
                    print "<td><b>Yes, new motif at %d-%d</b><br>(Due to mutation at %s)</td>" % \
                        (peak.start + peak.gainedMotifPosition, peak.start + len(motif.sequence) + 1, ','.join([str(p) for p in peak.mutationPosition]))
                else:
                    print "<td>No</td>"
                """
                
                #print peak

        print "</table><br><hr><br>"
        
    print "<pre>"


def output2():
    print "</pre>"
    for chromosome in range(1, 25):
        print "<h2>Chromosome %d:</h2>" % (chromosome)
        print "<p>In total %d ChIP-seq peak segments and %d SNPs</p>" % (len(peaks[chromosome]), len(snps[chromosome]))
        print "<p>Peak segments where loss or gain of function happened:</p>"
        print """
        <table border='1' cellpadding='3'>
        <tr>
            <th>Chr</th>
            <th>Peak position</th>
            <th>Binding of transcription factors on original peak sequence</th>
            <th>Binding after SNP mutation of peak sequence</th>
            <th>Lost function due to mutation?</th>
            <th>Gained function due to mutation?</th>
        </tr>
        """

        for peak in peaks[chromosome]:
            # Only present peaks that either had motifs or gained motifs
            if len(peak.bindingsBeforeMutations) > 0 or len(peak.bindingsAfterMutations) > 0:

                print "<tr>"
                print "<td>Chr %d</td><td>%d-%d</td>" % (peak.chromosome, peak.start, peak.end);
                print "<td>"

                if peak.hasMotif > 0:
                    for binding in peak.bindingsBeforeMutations:
                        print binding
                        print "<br>"
                else:
                    print "No"
                print "</td>"


                print "<td>"
                if len(peak.bindingsAfterMutations) > 0:
                    for binding in peak.bindingsAfterMutations:
                        print binding
                        print "<br>"
                else:
                    if not peak.hasSNP:
                        print "No change, no mutations"
                    else:
                        print "No new bindings"
                print "</td>"

                print "<td>"
                # Lost function happens if mutation occurs and there are no new bindings other than the original after mutation
                if peak.hasSNP and peak.hasMotif and len(peak.bindingsAfterMutations) == 0:
                    print "<b>Yes</b>"
                else:
                    print "No"
                print "</td>"

                # Determine whether the peak gained a binding that it didn't have before
                gained = 0
                for newBinding in peak.bindingsAfterMutations:
                    found = 0
                    for oldBinding in peak.bindingsBeforeMutations:
                        if newBinding.position == oldBinding.position:
                            found += 1

                    if found == 0:
                        gained += 1

                print "<td>"
                if gained == 0:
                    print "No"
                else:
                    print "<b>Yes</b> (gained %d new bindings)" % (gained)
                print "</td>"

                """
                if peak.gainedMotif:
                    print "<td><b>Yes, new motif at %d-%d</b><br>(Due to mutation at %s)</td>" % \
                        (peak.start + peak.gainedMotifPosition, peak.start + len(motif.sequence) + 1, ','.join([str(p) for p in peak.mutationPosition]))
                else:
                    print "<td>No</td>"
                """

                #print peak

        print "</table><br><hr><br>"

    print "<pre>"

class MutationsGeneRegulationGsuit(GeneralGuiTool, UserBinMixin, GenomeMixin):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Loss or gain of function depending on SNP mutation"

    @classmethod
    def getInputBoxNames(cls):
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase (e.g. "firstKey")
        '''

        return [('Genome', 'genome'), ('SNP data set','snp'),('Transcription factors (GSuite file from history)', 'gsuite')] #+\
                #cls.getInputBoxNamesForGenomeSelection() +\
                #UserBinSelector.getUserBinInputBoxNames()

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBoxGenome(): # Alternatively: getOptionsBox1()
        return '__genome__'

    @staticmethod
    def getOptionsBoxSnp(prevChoices): # Alternatively: getOptionsBox1()
         if prevChoices.genome or True:
            #return ('__history__', 'category.bed', 'bed')
            from gold.application.DataTypes import getSupportedFileSuffixesForPointsAndSegments #for example
            return ('__history__',) + tuple(getSupportedFileSuffixesForPointsAndSegments())
            #return '__history__', getSupportedFileSuffixesForPointsAndSegments()

    @staticmethod
    def getOptionsBoxGsuite(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return ('__history__',)

    @staticmethod
    def getOptionsBoxMotif(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return ('__history__',)

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        """
        print 'Some debug:'
        initAnalysis(choices)
        findMotifBindings()
        output()
        """
        import quick.webtools.article.MutationAffectingGeneRegulation as m
        analysis = m.MutationAffectingGeneRegulation(choices)
        html = analysis.presentResults()

        print str(html)
        #m.run()

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        return None


    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'


class TestTool(GeneralGuiTool, UserBinMixin, GenomeMixin):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Testing"

    @classmethod
    def getInputBoxNames(cls):
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase (e.g. "firstKey")
        '''

        return [] #+\
                #cls.getInputBoxNamesForGenomeSelection() +\
                #UserBinSelector.getUserBinInputBoxNames()

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None




    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        print "<h2>Test tool<h2>"
        fastaTrack = PlainTrack( ['Sequence', 'DNA'] )
        for i in range(0, 500):
            seqTv = fastaTrack.getTrackView(GenomeRegion("hg19", "chr1", 1000000, 1001000))
            sequence = seqTv.valsAsNumpyArray()
            print sequence

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        return None


class MatchTFsWithPWMs(GeneralGuiTool, UserBinMixin, GenomeMixin):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Match a suit of TFs with PWMs"

    @classmethod
    def getInputBoxNames(cls):
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase (e.g. "firstKey")
        '''

        return [('Gsuit file containing transcription factors', 'gsuite')] #+\
                #cls.getInputBoxNamesForGenomeSelection() +\
                #UserBinSelector.getUserBinInputBoxNames()

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None


    @staticmethod
    def getOptionsBoxGsuite(): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return ('__history__',)

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''

        import shelve
        mapper = shelve.open("/hyperbrowser/data/tfbs/tfNames2pwmIds.shelf")
        mapper["CTCF"] = ["REN_20"]
        print "Test"

        outfile = open(galaxyFn, "w")

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)

        fileName = choices.gsuite.split(":")[2]
        attributes_ordered = []

        metaFields = []

        # First: Write old headers to output file
        f = open(fileName, "r")
        headerLines = []
        for line in f.readlines():
            if line[0:3] == "###": # This is the field header line
                #headerLines.append([line.rstrip() + "\tpwm\n"]) # Add a pwm id field
                #attributes_ordered = line.replace("###", "").split('\t') # Fetch order list of attributes
                metaFields = line.replace("###", "").split("\t")[2:] # uri and title always first two fields?
                break # Break since this is the last header line
            else:
                headerLines.append(line)



        # Iterate over all TFs in gsuite file. Match to PWMs and write to output gusite file
        tflines = []
        attributes = []
        for x in gsuite.allTracks():
            print x
            #print "Processing " + x.attributes["table name"]
            if not "antibody" in x.attributes:
                print "Warning: TF is missing antibody meta data"
            elif not "cell" in x.attributes:
                print "Warning: TF is missing cell type meta data"
            else:
                if x.attributes["antibody"] in mapper:
                    line = x.uri + "\t" + x.title
                    pwms = []
                    for field in metaFields:
                        line += "\t"
                        if field.lower() in x.attributes:
                            line += x.attributes[field.lower()]
                        else:
                            line += "None"


                    for pwm in mapper[x.attributes["antibody"]]:
                        pwms.append(pwm)
                        #tflines.append(x.uri + "\t" + x.title + "\t" + '\t'.join(x.attributes.values()) + "\t" + pwm + "\n")

                    line += "\t" + ','.join(pwms) + "\n"
                    tflines.append(line)
                else:
                    print "Warning: Antibody is missing in mapper"
        print tflines


        # First write header lines
        outfile.writelines(headerLines)

        # Now get the correct meta data field names from attributes and write one line with those
        outfile.writelines(["###" + '\t'.join(["uri", "title"] + metaFields).rstrip() + "\tpwm" + "\n"])

        outfile.writelines(tflines)


    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return "gsuite"


    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        return None



class PointsInTracksStat(GeneralGuiTool):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Does a collection of tracks have more points/segments in one bin compared to the other bins?"

    @staticmethod
    def getInputBoxNames():
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('Genome:', 'genome'),
                ('GSuite tracks:','tracks'),
                ('Select statistic', 'stat'),
                ('Select MCFDR sampling depth', 'mcfdrDepth'),
                ('Select summary function', 'summaryFunc'),
                ('Select permutation strategy', 'permutationStrat'),
                ('Bin size', 'binSize'),
                ('Statistical question', 'question')]


    @staticmethod
    def getOptionsBoxGenome(): # Alternatively: getOptionsBox1()
        return '__genome__'

    @staticmethod
    def getOptionsBoxTracks(prevChoices): # Alternatively: getOptionsBox1()
        '''
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to other
        methods. These are lists of results, one for each input box (in the
        order specified by getInputBoxOrder()).

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - The contents is the default value shown inside the text area
        - Returns: string

        Raw HTML code:          '__rawstr__', 'HTML code'
        - This is mainly intended for read only usage. Even though more advanced
          hacks are possible, it is discouraged.

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.

        History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return ('__history__',)

    @staticmethod
    def getOptionsBoxBinSize(prevChoices): # Alternatively: getOptionsBox1()

        return ('1000000')

    @staticmethod
    def getOptionsBoxQuestion(prevChoices): # Alternatively: getOptionsBox1()
        return ['question 6', 'question 7', 'question 8']


    @staticmethod
    def getOptionsBoxStat(prevChoices):
        return [
                'PropOfReferenceTrackInsideTargetTrackStat',
                'PropOfReferenceTrackInsideUnionStat',
                'RatioOfIntersectionToGeometricMeanStat',
                'RatioOfOverlapToUnionStat'
                ]

    @staticmethod
    def getOptionsBoxSummaryFunc(prevChoices):
        return sorted(SummarizedInteractionWithOtherTracksStatUnsplittable.functionDict.keys())

    @staticmethod
    def getOptionsBoxPermutationStrat(prevChoices):
        #hardcoded for now to 'PermutedSegsAndIntersegsTrack'
        return None

    @staticmethod
    def getOptionsBoxMcfdrDepth(prevChoices):
        analysisSpec = AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDR$'])
        return analysisSpec.getOptionsAsText().values()[0]


    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        print "<pre>"
        print 'Success!'
        from PointsInTracksStat import PointsInTracksStat
        p = PointsInTracksStat(choices, galaxyFn, username)
        print "</pre>"

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        return None

    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    #@staticmethod
    #def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
    #
    #@staticmethod
    #def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    @staticmethod
    def isDynamic():
        '''
        Specifies whether changing the content of texboxes causes the page to
        reload.
        '''
        return True
    
    #@staticmethod
    #def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    #@staticmethod
    #def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    #@staticmethod
    #def getFullExampleURL():
    #    return None
    #
    #@classmethod
    #def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getOutputFormat(choices):
    #    '''
    #    The format of the history element with the output of the tool. Note
    #    that html output shows print statements, but that text-based output
    #    (e.g. bed) only shows text written to the galaxyFn file.In the latter
    #    case, all all print statements are redirected to the info field of the
    #    history item box.
    #    '''
    #    return 'html'
