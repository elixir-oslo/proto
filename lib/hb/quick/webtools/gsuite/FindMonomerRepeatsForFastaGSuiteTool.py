import subprocess
from collections import OrderedDict

from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util.CommonFunctions import ensurePathExists
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.util.debug import DebugUtil
from quick.webtools.GeneralGuiTool import GeneralGuiTool, HistElement
from gold.gsuite import GSuiteConstants
import re
from Bio import pairwise2

# This is a template prototyping GUI that comes together with a corresponding
# web page.


class FindMonomerRepeatsForFastaGSuiteTool(GeneralGuiTool):

    TRF_PATH = "/software/VERSIONS/trf-4.0.4/bin/trf404.linux64"
    TRF_VERSION = '4.0.4'

    FULL_REPEAT_REGION = 'Use full repeat region recognized by TRF tool'
    CUTOFF_REPEAT_REGION = 'Use only full length repeats to form regions'

    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PRIMARY]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]

    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    @staticmethod
    def getToolName():
        return 'Find repeat regions for each FASTA track in a GSuite with the Tandem Repeat Finder tool'

    @classmethod
    def getInputBoxNames(cls):
        return [
            ('Select gsuite', 'gsuite'),
            ('Match', 'match'),
            ('Mismatch', 'mismatch'),
            ('Delta', 'delta'),
            ('Matching probability (Pm)', 'pm'),
            ('Indel probability (Pi)', 'pi'),
            ('Min score', 'minscore'),
            ('Max period', 'maxperiod'),
            ('Min consensus length', 'minconsensus'),
            ('Max consensus length', 'maxconsensus'),
            ('Min copy number', 'mincopynumber'),
            ('Generate GSuite of repeat regions (bed)', 'regionsGSuite'),
            ('Generate GSuite of repeat monomers (bed)', 'monomersGSuite'),
            ('Repeat region cutoff', 'rrCutoff')]

    @staticmethod
    def getOptionsBoxGsuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxMatch(prevChoices):
        return '2'

    @staticmethod
    def getOptionsBoxMismatch(prevChoices):
        return '5'

    @staticmethod
    def getOptionsBoxDelta(prevChoices):
        return '7'

    @staticmethod
    def getOptionsBoxPm(prevChoices):
        return '80'

    @staticmethod
    def getOptionsBoxPi(prevChoices):
        return '10'

    @staticmethod
    def getOptionsBoxMinscore(prevChoices):
        return '50'

    @staticmethod
    def getOptionsBoxMaxperiod(prevChoices):
        return '300'

    @staticmethod
    def getOptionsBoxMinconsensus(prevChoices):
        return '190'

    @staticmethod
    def getOptionsBoxMaxconsensus(prevChoices):
        return '240'    \

    @staticmethod
    def getOptionsBoxMincopynumber(prevChoices):
        return '2'

    @staticmethod
    def getOptionsBoxRegionsGSuite(prevChoices):
        return True

    @staticmethod
    def getOptionsBoxMonomersGSuite(prevChoices):
        return True

    @classmethod
    def getOptionsBoxRrCutoff(cls, prevChoices):
        if prevChoices.regionsGSuite:
            return [cls.CUTOFF_REPEAT_REGION, cls.FULL_REPEAT_REGION]


    @classmethod
    def getExtraHistElements(cls, choices):
        hEList = []
        if choices.regionsGSuite:
            hEList.append(HistElement('Repeat regions (bed) GSuite', 'gsuite'))
        if choices.monomersGSuite:
            hEList.append(HistElement('Repeat monomers (bed) GSuite', 'gsuite'))
        return hEList

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        import os
        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        # match = int(choices.match)
        # mismatch = int(choices.mismatch)
        # delta = int(choices.delta)
        # pm = int(choices.pm)
        # pi = int(choices.pi)
        # minscore = int(choices.minscore)
        # maxperiod = int(choices.maxperiod)
        minConsensusLength = int(choices.minconsensus) if choices.minconsensus.isdigit() else None
        maxConsensusLength = int(choices.maxconsensus) if choices.maxconsensus.isdigit() else None
        minCopyNumber = int(choices.mincopynumber) if choices.mincopynumber.isdigit() else None
        parameters = [choices.match, choices.mismatch, choices.delta, choices.pm,
                      choices.pi, choices.minscore, choices.maxperiod]
        resultsDict = OrderedDict()
        for gsTrack in gsuite.allTracks():
            resFile = GalaxyRunSpecificFile(['trf', gsTrack.title, gsTrack.title + '.tmp'], galaxyFn)
            ensurePathExists(resFile.getDiskPath())
            trackDirName = os.path.dirname(os.path.realpath(resFile.getDiskPath()))
            # parameters = ["2", "5", "7", "80", "10", "50", "300"] #Madeleine suggestion
            instruction = [cls.TRF_PATH, gsTrack.path] + parameters + ["-d", "-h"]
            pipe = subprocess.Popen(instruction, cwd=trackDirName, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            results, errors = pipe.communicate()

            outFileName = ".".join([os.path.basename(gsTrack.path)] + parameters + ["dat"])
            outFilePath = os.path.join(trackDirName, outFileName)

            # print outFilePath

            resultList = cls.parseTRFResultFile(outFilePath, minConsensusLength, maxConsensusLength, minCopyNumber)
            if resultList:
                resultsDict[gsTrack.title] = resultList

        if choices.regionsGSuite:
            repeatRegionsBedTracksGSuite = GSuite()
            for trackName, trfResultList in resultsDict.iteritems():
                trackUri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                         extraFileName=("Repeat_regions_"+trackName),
                                                         suffix='bed')
                gsTrack = GSuiteTrack(trackUri, title=("Repeat regions " + trackName), genome=gsuite.genome)
                ensurePathExists(gsTrack.path)
                with open(gsTrack.path, 'w') as bedFile:
                    header = 'track name="' + trackName + '" description="' + trackName + '" priority=1'
                    bedFile.write(header + os.linesep)
                    for trfResult in trfResultList:
                        for repeatRegion in trfResult._repeatRegionList:
                            # if not repeatRegion.strand:
                            #     DebugUtil.insertBreakPoint()
                            endPosition = repeatRegion.endPositionFullCopies if choices.rrCutoff == cls.CUTOFF_REPEAT_REGION else repeatRegion.endPosition
                            bedFile.write('\t'.join([repeatRegion.chromosome,
                                                     str(repeatRegion.startPosition),
                                                     str(endPosition),
                                                     repeatRegion.bedName,
                                                     '0',
                                                     str(repeatRegion.strand)]) + os.linesep)
                repeatRegionsBedTracksGSuite.addTrack(gsTrack)

            GSuiteComposer.composeToFile(repeatRegionsBedTracksGSuite, cls.extraGalaxyFn['Repeat regions (bed) GSuite'])

        if choices.monomersGSuite:
            monomersBedTracksGSuite = GSuite()
            for trackName, trfResultList in resultsDict.iteritems():
                trackUri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                         extraFileName=("Repeat_monomers_"+trackName),
                                                         suffix='bed')
                gsTrack = GSuiteTrack(trackUri, title=("Repeat monomers " + trackName), genome=gsuite.genome)
                ensurePathExists(gsTrack.path)
                with open(gsTrack.path, 'w') as bedFile:
                    header = 'track name="' + trackName + '" description="' + trackName + '" priority=1'
                    bedFile.write(header + os.linesep)
                    for trfResult in trfResultList:
                        for repeatRegion in trfResult._repeatRegionList:
                            # if not repeatRegion.strand:
                            #     DebugUtil.insertBreakPoint()
                            for repeatMonomer in repeatRegion._monomers:
                            # endPosition = repeatRegion.endPositionFullCopies if choices.rrCutoff == cls.CUTOFF_REPEAT_REGION else repeatRegion.endPosition
                                bedFile.write('\t'.join([repeatRegion.chromosome,
                                                         str(repeatMonomer.startPosition),
                                                         str(repeatMonomer.endPosition),
                                                         repeatMonomer.bedName,
                                                         '0',
                                                         str(repeatRegion.strand)]) + os.linesep)

                monomersBedTracksGSuite.addTrack(gsTrack)

            GSuiteComposer.composeToFile(monomersBedTracksGSuite, cls.extraGalaxyFn['Repeat monomers (bed) GSuite'])


        ###################
        analysisParamsTableColumnTitles = ['Parameter', 'Selected value']
        analysisParamsDict = OrderedDict()
        analysisParamsDict['Tandem Repeat Finder tool version'] = cls.TRF_VERSION
        analysisParamsDict.update(
            OrderedDict([
            ('Match', choices.match),
            ('Mismatch', choices.mismatch),
            ('Delta', choices.delta),
            ('Matching probability (Pm)', choices.pm),
            ('Indel probability (Pi)', choices.pi),
            ('Min score', choices.minscore),
            ('Max period', choices.maxperiod),
            ('Min consensus length', choices.minconsensus),
            ('Max consensus length', choices.maxconsensus),
            ('Min copy number', choices.mincopynumber)]
            )
        )
        ###################

        ###################
        countTableColumnTitles = ['Name', 'Nr of repeat regions', 'Avg copy number', 'Min copy number',
                                  'Max copy number', 'Avg consensus length', 'Min consensus length',
                                  'Max consensus length']
        countTableDict = OrderedDict()
        from numpy import mean
        for trackName, trfResultList in resultsDict.iteritems():
            countTableDict[trackName] = []
            repeatRegionsNr = sum([x.repeatRegionsCount for x in trfResultList])
            countTableDict[trackName].append(repeatRegionsNr)
            copyNumberList =[]
            for trfRes in trfResultList:
                copyNumberList += trfRes.copyNumberList if \
                    choices.rrCutoff == cls.CUTOFF_REPEAT_REGION else trfRes.realCopyNumberList
            countTableDict[trackName].append(mean(copyNumberList))
            countTableDict[trackName].append(min(copyNumberList))
            countTableDict[trackName].append(max(copyNumberList))

            consensusLengthList = []
            for trfRes in trfResultList:
                consensusLengthList += trfRes.consensusLengths
            countTableDict[trackName].append(mean(consensusLengthList))
            countTableDict[trackName].append(min(consensusLengthList))
            countTableDict[trackName].append(max(consensusLengthList))

        ###################

        core = HtmlCore()
        core.begin()
        core.divBegin()
        # core.paragraph('''This tool reports repeat regions discovered by the TRF tool
        #                 ''')
        core.tableFromDictionary(analysisParamsDict, columnNames=analysisParamsTableColumnTitles, sortable=False)
        core.divEnd()
        core.divBegin()
        core.tableFromDictionary(countTableDict, columnNames=countTableColumnTitles,
                                 tableId='repeatCounts', sortable=True, presorted=0)
        core.divEnd()
        # core.divBegin()
        # for k, v in resultsDict.iteritems():
        #     core.line('track: ' + k)
        #
        #     for val in v:
        #         core.line(str(val))
        # core.divEnd()
        core.end()

        print core



            # print results

    @staticmethod
    def parseTRFResultFile(filepath, minConsensusLength=None, maxConsensusLength=None, minCopyNumber=0):
        resultObjectList = []
        with open(filepath, 'r') as f:
            currentResult = None
            for line in f:
                if line.startswith('Sequence:'):
                    if currentResult and currentResult._repeatRegionList:
                        resultObjectList.append(currentResult)
                    currentResult = None #for clarity
                    seqTitleLine = line.strip().split(":")[1]
                    seqTitleLineList = seqTitleLine.split()
                    #print seqTitleLineList
                    chromosome = seqTitleLineList[0].strip()
                    absoluteStart = 0
                    absoluteEnd = 0
                    regionStringList = None
                    if len(seqTitleLineList) > 2 and '-' in seqTitleLineList[1]:
                        regionStringList = seqTitleLineList[1].strip().split('-')
                        absoluteStart = int(regionStringList[0])
                        absoluteEnd = int(regionStringList[1])
                    strand = None
                    if len(seqTitleLineList) > 2:
                        strandStr = seqTitleLineList[2].strip()
                        if strandStr in ['(Pos)', '+']:
                            strand = '+'
                        elif strandStr in ['(Neg)', '-']:
                            strand = '-'
                        else:
                            # DebugUtil.insertBreakPoint()
                            strand = '.' #TODO boris: determine default value and set here
                    name = chromosome + ":" + seqTitleLineList[1].strip() if regionStringList else chromosome
                    currentResult = LineElementRepeatsModel(name, chromosome, absoluteStart, absoluteEnd, strand=strand)
                else:
                    splitLine = line.strip().split()
                    if len(splitLine) == 15 and splitLine[0].strip().isdigit():
                        start = int(splitLine[0].strip())
                        end = int(splitLine[1].strip())
                        period = int(splitLine[2].strip())
                        consensus = splitLine[13].strip()
                        consensusLength = len(consensus)
                        if minConsensusLength and consensusLength < minConsensusLength:
                            continue
                        if maxConsensusLength and consensusLength > maxConsensusLength:
                            continue
                        realCopyNumber = float(splitLine[3])
                        copyNumber = int(realCopyNumber)
                        if minCopyNumber and minCopyNumber > copyNumber:
                            continue
                        repeatRegionSeq = splitLine[14].strip()
                        currentRepeatRegion = RepeatRegionModel(currentResult, start, end, period, copyNumber, realCopyNumber,
                                                  consensus, sequence=repeatRegionSeq)
                        currentResult.addRepeatRegion(currentRepeatRegion)
                        # DebugUtil.insertBreakPoint()

                        # monomerAllignments = pairwise2.align.localms(repeatRegionSeq, consensus, 2, -1, -0.5, -0.1)
                        # print 'Consensus: ', consensus
                        # for a in monomerAllignments:
                        #     print(pairwise2.format_alignment(*a))

                        # print '<br>Full sequence: ', repeatRegionSeq
                        # print '<br>Copy number: ', str(copyNumber)
                        # print "<br><br>Local: ", monomerAllignments
                        repeatRegionSeqShortened = repeatRegionSeq
                        if realCopyNumber > copyNumber:
                            lenDiff = len(repeatRegionSeq) - consensusLength*copyNumber
                            if lenDiff > 10: #shorten the full repeats region to just the full copy number and add 10 characters
                                repeatRegionSeqShortened = repeatRegionSeq[:(consensusLength*copyNumber + 10)]
                        # DebugUtil.insertBreakPoint()
                        #10*X after each consensus slice to mark borders between monomers
                        # seq2 = ((consensus + 'XXXXXXXXXX') * (copyNumber - 1) + consensus) if copyNumber == realCopyNumber \
                        seq2 = (consensus + 'XXX') * copyNumber if copyNumber == realCopyNumber \
                            else ((consensus + 'XXX') * copyNumber + consensus[0:20])
                        # monomerAllignmentsGlobal = pairwise2.align.globalms(repeatRegionSeqShortened, seq2, 2, -1, -1, -0.5)
                        scoreMatrix = {('A', 'A'): 2, ('A', 'C'): -1, ('A', 'G'): -1, ('A', 'T'): -1,
                                       ('C', 'C'): 2, ('C', 'A'): -1, ('C', 'G'): -1, ('C', 'T'): -1,
                                       ('G', 'G'): 2, ('G', 'C'): -1, ('G', 'A'): -1, ('G', 'T'): -1,
                                       ('T', 'T'): 2, ('T', 'C'): -1, ('T', 'G'): -1, ('T', 'A'): -1,
                                       ('X', 'X'): 2,
                                       ('X', 'T'): -11,
                                       ('X', 'C'): -11,
                                       ('X', 'G'): -11,
                                       ('X', 'A'): -11,
                                       ('T', 'X'): -11,
                                       ('C', 'X'): -11,
                                       ('G', 'X'): -11,
                                       ('A', 'X'): -11
                                       }
                        monomerAlignmentsGlobal = pairwise2.align.globalds(repeatRegionSeqShortened, seq2, scoreMatrix, -1, -1)

                        # if copyNumber == realCopyNumber:
                        alignmentRes = monomerAlignmentsGlobal[0]
                        realSeqAligned = alignmentRes[0]
                        consensusSeqAligned = alignmentRes[1]
                        monomerStartPos = 0
                        monomerRelativeStart = 0
                        for k, i in enumerate((m.start() for m in re.finditer('XXX', consensusSeqAligned))):
                            monomerEndPos = i
                            monomerSeqAligned = realSeqAligned[monomerStartPos:monomerEndPos]
                            monomerSeq = ''.join([x for x in monomerSeqAligned if x != '-'])
                            monomerRelativeEnd = monomerRelativeStart + len(monomerSeq)
                            monomerConsensusAligned = consensusSeqAligned[monomerStartPos:monomerEndPos]
                            currentMonomer = RepeatMonomerModel(currentRepeatRegion,
                                                                monomerRelativeStart,
                                                                monomerRelativeEnd,
                                                                sequence=monomerSeq,
                                                                alignmentToConsensus=(monomerSeqAligned,
                                                                                      monomerConsensusAligned))
                            currentRepeatRegion.addMonomer(currentMonomer)
                            monomerRelativeStart = monomerRelativeEnd
                            monomerStartPos = i + 3


                        # print "Global: "
                        # for a in monomerAllignmentsGlobal:
                        #     s1 = a[0]
                        #     s2 = a[1]
                        #     import re
                        #     for i in (m.start() for m in re.finditer('XXX', s2)):
                        #         try:
                        #             if s1[i:i+3] == '---':
                        #                 print 'Success'
                        #             else:
                        #                 nonDashCharacters = ''.join([x for x in s1[i:i+3] if x != '-'])
                        #                 nonDashCharactersNr = len(nonDashCharacters)
                        #                 print 'Fail ', str(copyNumber), ' ', str(realCopyNumber)
                        #                 print 'Failed match: ', s1[i:i+3]
                        #                 print 'Nr of non-dashes: ', nonDashCharactersNr
                        #                 print nonDashCharacters
                        #                 print consensus[:nonDashCharactersNr]
                        #                 if nonDashCharacters == consensus[:nonDashCharactersNr]:
                        #                     print "Same as start of consensus"
                        #                 else:
                        #                     print "Different from start of consensus"
                        #
                        #                 if copyNumber == realCopyNumber:
                        #                     print 'EQUAL!!!'
                        #         except:
                        #             print 'Fail with exception', str(copyNumber), ' ', str(realCopyNumber)
                        #     print(pairwise2.format_alignment(*a))


        return resultObjectList

    @classmethod
    def validateAndReturnErrors(cls, choices):
        """
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        :param choices:  Dict holding all current selections
        """
        errorString = GeneralGuiTool._checkGSuiteFile(choices.gsuite)
        if errorString:
            return errorString

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
    #def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
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
    #    name. The base directory is STATIC_PATH as defined by AutoConfig.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    #@staticmethod
    #def getFullExampleURL():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether the debug mode is turned on.
    #    '''
    #    return False
    #
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


class LineElementRepeatsModel(object):
    def __init__(self, name, chromosome, startPos, endPos, strand=None):
        self._name = name
        self._chromosome = chromosome
        self._startPos = startPos
        self._endPos = endPos
        self._strand = strand
        self._repeatRegionList = []

    @property
    def chromosome(self):
        return self._chromosome

    def addRepeatRegion(self, repeatRegion):
        self._repeatRegionList.append(repeatRegion)

    @property
    def repeatRegionsCount(self):
        return len(self._repeatRegionList) if self._repeatRegionList else 0

    @property
    def copyNumberList(self):
        return [x.copyNumber for x in self._repeatRegionList]

    @property
    def realCopyNumberList(self):
        return [x.realCopyNumber for x in self._repeatRegionList]

    @property
    def consensusLengths(self):
        return [len(x.consensus) for x in self._repeatRegionList]

    def __str__(self):
        return ' '.join([self._name, self._chromosome, str(self._startPos), str(self._endPos), self._strand] + [str(x) for x in self._repeatRegionList])

    def __unicode__(self):
        return u''+' '.join([self._name, self._chromosome, str(self._startPos), str(self._endPos), self._strand] + [str(x) for x in self._repeatRegionList])

    def __repr__(self):
        return ' '.join([self._name, self._chromosome, str(self._startPos), str(self._endPos), self._strand] + [str(x) for x in self._repeatRegionList])


class RepeatRegionModel(object):

    def __init__(self, parent, relativeStart, relativeEnd, period, copyNumber, realCopyNumber, consensus, sequence=None):
        self._parent = parent
        self._relativeStart = relativeStart
        self._relativeEnd = relativeEnd
        self._period = period
        self._copyNumber = copyNumber
        self._realCopyNumber = realCopyNumber
        self._consensus = consensus
        self._sequence = sequence
        # self._regionStart = regionStart
        # self._regionEnd = regionEnd
        self._monomers = []

    @property
    def chromosome(self):
        return self._parent.chromosome

    @property
    def startPosition(self):
        return self._parent._startPos + self._relativeStart - 1

    @property
    def endPosition(self):
        return self._parent._startPos + self._relativeEnd - 1

    @property
    def endPositionFullCopies(self):
        return self.startPosition + self._copyNumber*self._period

    @property
    def bedName(self):
        return self._consensus + '-' + str(self._copyNumber) + "-" + self._parent._name

    @property
    def strand(self):
        return self._parent._strand

    @property
    def copyNumber(self):
        return self._copyNumber

    @property
    def realCopyNumber(self):
        return self._realCopyNumber

    @property
    def consensus(self):
        return self._consensus

    @property
    def sequence(self):
        return self._sequence


    def addMonomer(self, monomer):
        self._monomers.append(monomer)

    def __str__(self):
        return ' '.join([str(self._relativeStart), str(self._relativeEnd), str(self._copyNumber), self._consensus] + [str(x) for x in self._monomers])

    def __unicode__(self):
        return u'' + ' '.join([str(self._relativeStart), str(self._relativeEnd), str(self._copyNumber), self._consensus] + [str(x) for x in self._monomers])

    def __repr__(self):
        return ' '.join([str(self._relativeStart), str(self._relativeEnd), str(self._copyNumber), self._consensus] + [str(x) for x in self._monomers])


class RepeatMonomerModel(object):

    def __init__(self, parent, relativeStart, relativeEnd, sequence=None, alignmentToConsensus=None):
        self._parent = parent #repeat region
        self._relativeStart = relativeStart #start position inside the repeat region
        self._relativeEnd = relativeEnd #end position inside the repeat region
        self._sequence = sequence
        self._alignmentToConsensus = alignmentToConsensus #2-tuple monomer, consensus with indels

    @property
    def startPosition(self):
        return self._parent.startPosition + self._relativeStart

    @property
    def endPosition(self):
        return self._parent.startPosition + self._relativeEnd

    @property
    def sequence(self):
        return self._sequence

    @property
    def bedName(self):
        return self._sequence + "-" + self._parent.bedName

    def __str__(self):
        return ' '.join([str(self._relativeStart), str(self._relativeEnd)])

    def __unicode__(self):
        return u'' + ' '.join([str(self._relativeStart), str(self._relativeEnd)])

    def __repr__(self):
        return ' '.join([str(self._relativeStart), str(self._relativeEnd)])







