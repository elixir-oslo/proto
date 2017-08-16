import numpy as np

from config.Config import HB_SOURCE_CODE_BASE_DIR
from gold.track.GenomeRegion import GenomeRegion
from gold.track.Track import Track, PlainTrack
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.UserBinSource import GlobalBinSource
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN

snps = [[] for chromosome in range(0,25)]
snpsTrack = None

peaks = [[] for chromosome in range(0,25)]
transcription_factors = []
motif = None
motifs = {} # Dict holding all the motifs
regions = []
genome = None
fastaTrack = PlainTrack( ['Sequence', 'DNA'] )

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

# Represents a motif with a PWM. Every transcription factor will have Motif
class Motif():
    sequence = "" # Consensus sequence, only used for printing

    def __init__(self):
        self.sequenceProbs = []

    def __len__(self):
        return len(self.sequenceProbs)

    def __repr__(self):
        out = "Motif: " + self.name + "\n"
        for p in self.sequenceProbs:
            out += str(p)
            out += "\n"

        return out

    # Returns the probability for a given letter (A, C, G, T) occurring at a given position
    def probabilityAtPosition(self, position, base):
        base = base.upper()
        if base not in ['A', 'G', 'C', 'T']:
            return 0

        return self.sequenceProbs[position][base.upper()]

    # Old version of this function: Returns the probability that a given motif sequence can bind
    # Current: Returns the probability of trans. fact. binding given sequence (using Bayes rule)
    def probabilitySequence(self, sequence):
        #sequence = list(sequence)
        i = 0
        prob = 1
        for s in sequence:
            prob *= self.probabilityAtPosition(i, s)
            i += 1

        a = BINDING_A_PRIORI_PROB # If we later are only interested in ratio of two such probabilities, this can be anything
        transFacBindingProb = a * prob / (a * prob + (1-a) * 0.25**len(sequence))

        return transFacBindingProb

def computeProbsForPWMLine(line, fastaFileContainsCnts = True):
    probs = np.array([float(p) for p in line.split()])
    #print probs

    pseudoWeight = 0.25 # Something that is added to avoid zero probs, see Matrix-based pattern matching by van Helden

    if fastaFileContainsCnts:
        totalCnts = sum(probs) + pseudoWeight
        probs = (probs + pseudoWeight) / totalCnts

    probDict = {"A": probs[0], "C": probs[1], "G": probs[2], "T": probs[3]}
    return probDict


def chrToNum(chromosome):
    c = chromosome.replace("chr", "")
    if c == "X" or c == "x":
        c = 23
    if c == "Y" or c == "y":
        c = 24

    return int(c)


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

    return False

# Returns a "probability" that the motif (needle) will bind/fit in every possible position in the haystack sequence
# (Should do, but doesn't now: Also returns an overall probability that every possible motif binds anywhere in the haystack)
def motifProbabilitySearch(haystack, needle):
    probs = []

    for i in range(0, len(haystack) - len(needle) + 1):
        probs.append(motif.probabilitySequence(list(haystack)[i:i + len(needle)]))

    return probs


# Represents a transcription factor (unique together with a motif that should be analysed together with this transcription factor
class TranscriptionFactor:
    def __init__(self, name, motifid):
        self.motifid = motifid
        self.name = str(name[4])
        self.motif = motifs[motifid] # motifs should already be a dict with motifs
        self.peaks = [] # Peaks in this transcription factor
        self.peakTrack = Track(name)
        self.trackName = name

        self._addPeaks()

    def __repr__(self):
        return "Transcription factor "  + self.name + " with motif " + self.motifid



    # Add all peaks this that this transcription factor has
    def _addPeaks(self):
        #trackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, self.trackName)
        track = PlainTrack(self.trackName)
        chromRegs = GlobalBinSource(genome)
        i = 0
        for region in chromRegs:
            if i > 2:
                break
            tv = track.getTrackView(region)
            starts = tv.startsAsNumpyArray()
            ends = tv.endsAsNumpyArray()

            for (start, end) in zip(starts, ends):
                self.peaks.append(Peak(self, region.chr, start, end))

            i += 1


class Peak:
    def __init__(self, transcriptionFactor, chr, start, end):
        self.chr = chr
        self.start = start
        self.end = end
        self.tf = transcriptionFactor
        self.bestBindingScoreBeforeMutation = -1
        self.bestBindingScoreAfterMutation = -1
        self.bestBindingPositionBeforeMutation = -1
        self.bestBindingPositionAfterMutation = -1
        self.worstBindingScoreAfterMutation = -1
        self.worstBindingPositionAfterMutation = -1
        self.mutation = 0 # Position of the mutation that caused
        self._getSequence()
        self.mutationPositions = [] # Position of all mutations in this peak

        self.hasSnps = False


    def hasSnpBetween(self, start, end):
        for m in self.mutationPositions:
            if m >= start and m < end:
                return True

        return False

    # Gets the sequence for this peak, stores it
    def _getSequence(self):
        seqTv = fastaTrack.getTrackView(GenomeRegion(genome, self.chr, self.start, self.end))
        self.sequence = np.array(seqTv.valsAsNumpyArray())

    # Returns the maximum matching score that this peak segment has with its motif
    def computeMaxScoreBeforeMutation(self):
        (score, pos) = self._computeMaxScoreWithSequence(self.sequence)
        self.bestBindingPositionBeforeMutation = pos
        self.bestBindingScoreBeforeMutation = score


    def _getMutatedSequences(self):
        relevantSnps = []
        for snp in snps[chrToNum(self.chr)]:
            if snp.position < self.end and snp.position >= self.start:
                relevantSnps.append(snp)
                self.mutationPositions.append(snp.position)


        if len(relevantSnps) > 0:
            self.hasSnps = True


        # Get combinations of SNPs
        # Not doing this anymore, because we are only interested in one SNP
        #from itertools import combinations
        #snpCombinations = sum([map(list, combinations(relevantSnps, i))
        #                       for i in range(len(relevantSnps) + 1)], []) # Lazy one liner that gets combinations from relevantSnps

        mutatedSequences = []

        #for snpCombination in snpCombinations:
        #    mutationsHere = []
        #    m = list(originalSequence)

        for snp in relevantSnps: # Old: for snp in snpsCombinations

            m = self.sequence.copy()
            #mutationsHere.append(snp.position)
            if m[snp.position - self.start].lower() != "n": # Do not change an n (not important)
                m[snp.position - self.start] = snp.mutationTo

                if ''.join(m) != ''.join(self.sequence):
                    mutatedSequences.append(m)
        #print "Number of mutated sequences: " + str(len(mutatedSequences))
        return mutatedSequences


    # Checks all mutated sequences, stores the maximum and minimum of the best scores
    def computeMinAndMaxOfMaxScoresAfterMutations(self):

        minScore = 10e10
        maxScore = -10e10

        minPos = -1
        maxPos = -1

        for seq in self._getMutatedSequences():
            (score, pos) = self._computeMaxScoreWithSequence(seq)
            if score > maxScore:
                maxScore = score
                maxPos = pos
                self.bindingSequenceAfterMutations = seq[pos - self.start : pos - self.start + len(self.tf.motif)]

            # This is probably irrelevant, because we are not interested in min of the all the max after mutation
            if score < minScore:
                minScore = score
                minPos = pos

        self.bestBindingPositionAfterMutation = maxPos
        self.bestBindingScoreAfterMutation = maxScore
        self.worstBindingScoreAfterMutation = minScore
        self.worstBindingPositionAfterMutation = minPos


    # Returns the maximum score that a motif (sequence) has with this peak
    def _computeMaxScoreWithSequence(self, sequence):

        max = -10
        maxPos = -1

        for i in range(0, self.end - self.start - len(self.tf.motif)):
            # Compute the score at this position
            score = self.tf.motif.probabilitySequence(sequence[i : i + len(self.tf.motif)])
            #print "Score at pos i: %f" % (score)
            if score > max:
                max = score
                maxPos = self.start + i


        return (max, maxPos)

# Returns a "pretty" html string showing where a sequence binds on the peak.sequence (with mutations)
# bindingPosition is the position on the genome (e.g. 23474885)
def prettySequence(peak, sequence, bindingPosition):

    prettySequence = ""


    sequenceList = sequence
    #print "Sequence list"
    #print sequenceList
    #print "Binding position"
    #print bindingPosition

    originalSequenceList = peak.sequence


    if len(sequenceList) > len(originalSequenceList):
        return ""

    rangeToShow = 10 # Number of bases outside the binding site we wish to include


    minBase = max(peak.start, bindingPosition - rangeToShow)
    maxBase = min(peak.end, bindingPosition + len(peak.tf.motif) + rangeToShow)

    #print minBase
    #print maxBase

    for i in range(minBase, maxBase):
        posRelToSeq = i - peak.start # The position in the peak sequence (where 0 is the first base in the seq)
        posRelToBindingSeq = i - bindingPosition
        #print "(" + str(posRelToSeq) + "<br>" + str(maxBase) + "<br>" + str(minBase) + "<br>" + self.sequence + "<br>" + self.peak.sequence + ")"
        base = originalSequenceList[posRelToSeq]
        baseHtml = base


        if i >= bindingPosition and i < bindingPosition + len(peak.tf.motif):

            if sequenceList[posRelToBindingSeq].upper() != originalSequenceList[posRelToSeq].upper() :
                baseHtml = "<a title='Mutated from " + originalSequenceList[posRelToSeq] + "'><b><u>" + base + "</u></b></a>"
            else:
                baseHtml = "<b>" + baseHtml + "</b>"

        prettySequence += baseHtml

    return prettySequence


class MutationAffectingGeneRegulation:


    def __init__(self, choices):
        global motifs, snps, peaks, transcription_factors, regions, genome, snpsTrack


        genome = choices.genome
        transcription_factors = []

        # Add all internal motifs to a dictionary
        self._addAllMotifsFromInternalPWMs()

        # Preprocess and store snp data file
        #trackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(choices.genome, choices.snp)
        #snpsTrack = PlainTrack(trackName)
        #print snpsTrack
        # Do it the "old" way since I do not know how to get the 4th column from trackview
        #print trackName
        self._getSnpData(choices.snp) #.split(":")[2])



        #tv = snpsTrack.getTrackView(GenomeRegion(genome, "chr1", 0, 10000))
        #print tv.allExtrasAsDictOfNumpyArrays()
        #print snps




        # Add some fake mutations
        #snps[1].append(SNP(1, 1708718, "C", "A"))
        #snps[1].append(SNP(1, 1708720, "G", "C"))

        # Add all transcription factor tracks from gsuite file
        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        for x in gsuite.allTracks():
            if not "pwm" in x.attributes:
                print "Error: pwm attribute is missing from track " + str(x.trackName) + ". The transcription factor was removed from analysis."
            #elif x.attributes["pwm"] not in motifs:
            #    print "Error: pwm "  + x.attributes["pwm"] + " was not found in the list of supported pwms. The transcription factor " + str(x.trackName) + " was removed from analysis."
            else:
                for pwm in x.attributes["pwm"].split(","):
                    if pwm not in motifs:
                        print "<p>Warning: pwm "  + pwm + " was not found in the list of supported pwms. The transcription factor " + str(x.trackName) + " will not be analysed with this pwm.</p>"
                    else:
                        transcription_factors.append(TranscriptionFactor(x.trackName, pwm))


        Track(x.trackName)


        self.runAnalysis()


        # For every transcription factor (that have an associated motif), do the following:
        # Go through every peak in that transcription factor, compute maximum binding on its exact sequence
        #   For every possible mutated sequences of that peak, compute the maximum binding score. Only consider mutated
        #   sequences where there is one single base pair that is mutated. Compute the minimum of the maximum scores from
        #   all these sequences. Store position of best before mutation and best after mutation in the peak object

    # Runs the analysis after init() has initialized all data
    def runAnalysis(self):

        for tf in transcription_factors:
            #print "Running analysis for tf " + str(tf.name)
            for peak in tf.peaks:
                # Find best binding score before any mutations with this peak
                peak.computeMaxScoreBeforeMutation()
                peak.computeMinAndMaxOfMaxScoresAfterMutations()

    def presentResults(self):
        """
        :return: Returns html core object
        """
        core = HtmlCore()
        core.begin()
        core.header("Results")
        core.divBegin(divClass='resultsExplanation')
        core.paragraph('''
            The table summarizes the results for each transcription factor and PWM that was analysed. Click on a row for details.
            ''')
        core.divEnd()

        core._str += """
         <script type="text/javascript" src="https://code.jquery.com/jquery-2.1.4.min.js"></script>
         <script>

        jQuery(document).ready(function() {
          jQuery(".content").hide();
          //toggle the componenet with class msg_body
          jQuery(".heading").click(function()
          {
            jQuery(this).next(".content").slideToggle(1);
          });
        });
        </script>
        """

        core._str +=  "<table class='colored bordered'>"
        #columns = ["Transcription factor", ""]
        #core.tableFromDictionary(rows, columns)
        core._str +=  """
            <tr>
                <th class='header'>Transcription factor</th>
                <!--<th>Peak data</th>-->
                <th class='header'>Mofif</th>
                <th class='header'>Number of peaks</th>
                <th class='header'>Number of peaks with SNP(s)</th>
                <th class='header'>Number of changed bindings</th>
                <!--<th class='header'>Binding after mutation</th>-->
            </tr>
        """

        for tf in transcription_factors:
            # First print some summary information for this TF
            name = tf.name
            core._str +=  "<tr class='heading' style='cursor: pointer;'>"
            core._str +=  "<td>" + name + "</td>"
            #core._str +=  "<td>" + ''.join(tf.name) + "</td>"
            core._str +=  "<td>" + tf.motif.name + "</td>"
            core._str +=  "<td>%d</td>" % (len(tf.peaks))
            core._str +=  "<td>%d</td>" % (len([p for p in tf.peaks if p.hasSnps]))

            subtable = ""
            subtable +=  "<tr class='content'><td colspan='7'>"
            subtable +=  "<br><h4 style='margin-left: 20px;'>Peaks that intersect with one or more SNPs</h4>"

            subtable +=  "<table border='1' cellpadding='5' style='margin-left: 20px;'>"
            subtable +=  """
                <tr>
                    <th>Position</th>
                    <th>Best binding before mutation</th>
                    <th>Best binding after mutation</th>
                </tr>
            """

            rows_important = []
            rows = []

            n_gain_loss = 0
            for peak in tf.peaks:

                important = False

                if len(peak.tf.motif) > len(peak.sequence):
                    continue # Ignore motifs longer than peak sequence (will only occur on test sets
                row = ""
                row +=  "<tr>"
                row +=  "<td>%s %d:%d</td>" % (peak.chr, peak.start, peak.end)
                #print "<td>%s</td>" % (''.join(peak.sequence))
                p = peak.bestBindingPositionBeforeMutation
                #print "Sequence: " + str(peak.sequence[p - peak.start : p - peak.start + len(peak.tf.motif)])
                row +=  "<td>On pos %d with score %.10f<br>%s</td>" % (p, peak.bestBindingScoreBeforeMutation, prettySequence(peak, peak.sequence[p - peak.start : p - peak.start + len(peak.tf.motif)], p))

                # Only present binding after if there was a mutation either within the old binding or within a new binding
                """
                if peak.hasSnpBetween(peak.bestBindingPositionAfterMutation, peak.bestBindingPositionAfterMutation + len(peak.tf.motif))  or \
                   peak.hasSnpBetween(peak.bestBindingPositionAfterMutation, peak.bestBindingPositionAfterMutation + len(peak.tf.motif)):
                    subtable +=  "<td>On pos %d with score %.10f<br>%s<br>Binding sequence: %s</td>" % (peak.bestBindingPositionAfterMutation, peak.bestBindingScoreAfterMutation, \
                                                                               prettySequence(peak, peak.bindingSequenceAfterMutations, peak.bestBindingPositionAfterMutation),\
                                                                                ''.join(peak.bindingSequenceAfterMutations))
                """



                if peak.hasSnpBetween(peak.start, peak.end):
                    if peak.bestBindingScoreAfterMutation != peak.bestBindingScoreBeforeMutation:
                        n_gain_loss += 1
                        row += "<td><font color='darkgreen'>"
                    else:
                        row += "<td><font>"
                        
                    row +=  "On position %d with score %.10f<br>%s<br>Binding sequence: %s</font></td>" % (peak.bestBindingPositionAfterMutation, peak.bestBindingScoreAfterMutation, \
                                                                               prettySequence(peak, peak.bindingSequenceAfterMutations, peak.bestBindingPositionAfterMutation),\
                                                                                    ''.join(peak.bindingSequenceAfterMutations))
                    important = True
                else:
                    row +=  "<td><font color='#666666'>No change (no point mutations)</font></td>"

                row +=  "</tr>"

                if important:
                    rows_important.append(row)
                else:
                    rows.append(row)



            subtable += ''.join(rows_important)


            #subtable += ''.join(rows)

            subtable +=  "</table><br><br>";
            subtable += "</td></tr>"

            if n_gain_loss > 0:
                core._str += "<td><b>%d</b></td>" % n_gain_loss
            else:
                core._str +=  "<td>%d</td>" % n_gain_loss
            core._str +=  "</tr>"
            core._str += subtable

        core._str +=  "</table>"

        return core


    def _getSnpData(self, fileName):
        global snps

        """
        f = open(fileName)
        for line in f.readlines():
            data = line.split()
            if "#" not in data[0]:
                chromosome = chrToNum(data[0])
                position = int(data[1])
                mutation = data[3].split(">")

                snps[chromosome].append(SNP(chromosome, position, mutation[0], mutation[1]))
        """

        fName = ExternalTrackManager.extractFnFromGalaxyTN(fileName)
        suffix = ExternalTrackManager.extractFileSuffixFromGalaxyTN(fileName)
        from gold.origdata.GenomeElementSource import GenomeElementSource
        geSource = GenomeElementSource(fName, suffix=suffix)

        for ge in geSource:
            chromosome = chrToNum(ge.chr)
            snps[chromosome].append(SNP(chromosome, int(ge.start), ge.mutated_from_allele, ge.mutated_to_allele))
            #print ge.chr, ge.start, ge.end, ge.mutated_from_allele


    def _addAllMotifsFromInternalPWMs(self):
        currentMotif = None
        pwmLine = 0
        f = open(HB_SOURCE_CODE_BASE_DIR + "/data/all_PWMs.txt")
        for line in f.readlines():

            if list(line)[0] == ">":
                currentMotif = Motif()
                motifName = line.replace(">", "").strip()
                currentMotif.name = motifName
                motifs[motifName] = currentMotif
                pwmLine = 0
            else:
                # We are at some line in the pwm. Get the probabilities/frequencies from that line
                probs = computeProbsForPWMLine(line, True)
                currentMotif.sequenceProbs.append(probs)







        """
        fastaTrack = PlainTrack( ['Sequence', 'DNA'] )

        chromRegs = GlobalBinSource(choices.genome)
        for region in chromRegs:
            tv = snpsTrack.getTrackView(region)
            #print tv.getBinaryBpLevelArray()

            #Numpy array access
            starts = tv.startsAsNumpyArray()
            ends = tv.endsAsNumpyArray()

            for i in range(0, len(starts)):
                print "Region: "
                print region
                seqTv = fastaTrack.getTrackView(GenomeRegion(genome, region.chr, starts[i], ends[i]))
                valList = list(seqTv.valsAsNumpyArray())
                print valList

        return
        """
        """
        trackName = choices.snp
        print "TrackName"
        print trackName
        snpsTrack = PlainTrack(choices.snp.split(":"))
        print snpsTrack.trackName
        view = snpsTrack.getTrackView(GenomeRegion(genome, "chr1", 1, 1000))
        return
        """

        """
        f = open(fileName)
        for line in f.readlines():
            data = line.split()
            chromosome = chrToNum(data[0])
            position = int(data[1])
            mutation = data[3].split(">")

            snps[chromosome].append(SNP(chromosome, position, mutation[0], mutation[1]))
        """



"""
# Represents a peak for a transcription factor
class TranscriptionFactorPeak:

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
"""

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

