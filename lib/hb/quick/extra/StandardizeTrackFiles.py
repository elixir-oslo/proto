#!/usr/bin/env python
import ast
import bz2
import os
import sys
import shutil
import re
#from proto.RSetup import r
import inspect
from glob import glob
from collections import OrderedDict

from gold.util.CustomExceptions import InvalidFormatError, AbstractClassError
from quick.util.CommonFunctions import ensurePathExists
from quick.util.GenomeInfo import GenomeInfo
from config.Config import DEFAULT_GENOME
from quick.extra.OrigFormatConverter import OrigFormatConverter
from third_party.roman import fromRoman
import third_party.safeshelve as safeshelve
from gold.util.CommonFunctions import createOrigPath, reverseDict, getOrigFn, getOrigFns
from config.Config import PARSING_ERROR_DATA_PATH, NONSTANDARD_DATA_PATH, ORIG_DATA_PATH, DATA_FILES_PATH
from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
from config.Config import DATA_FILES_PATH
from _collections import defaultdict
from third_party.asteval_raise_errors import Interpreter

SHELVE_FN = DATA_FILES_PATH + os.sep + 'StandardizerTool.shelve'

class GeneralTrackDataModifier(object):
    _DIR_DICT = OrderedDict([ \
                 ('coll_to_std', (NONSTANDARD_DATA_PATH, ORIG_DATA_PATH)),\
                 ('coll_to_coll', (NONSTANDARD_DATA_PATH, NONSTANDARD_DATA_PATH)),\
                 ('std_to_coll', (ORIG_DATA_PATH, NONSTANDARD_DATA_PATH)),\
                 ('std_to_std', (ORIG_DATA_PATH, ORIG_DATA_PATH)),\
                 ('std_to_error', (ORIG_DATA_PATH, PARSING_ERROR_DATA_PATH)),\
                 ('error_to_std', (PARSING_ERROR_DATA_PATH, ORIG_DATA_PATH))])

    EXCLUDE_PARAMS = ['cls', 'baseOutFn', 'direction', 'fromFn', 'toFn', 'stdFn', 'collFn', 'inFn', 'outFn', 'trackName', 'genome', 'firstFile', 'firstSubType', 'origSubTypeDepth', '**kwArgs']

    @classmethod
    def _findRevisionInputDir(cls, collPath, next=True):
        index = 0
        dirExists = True
        nextDir = None
        while dirExists:
            curDir = nextDir
            nextDir = collPath + os.sep + '__%d__' % index
            dirExists = os.path.exists(nextDir) and os.path.isdir(nextDir)
            index += 1
        return nextDir if next else curDir

    @classmethod
    def _getInputOutputPaths(cls, genome, trackName, direction, differentOutputTrackName=None):
        assert direction in cls._DIR_DICT, "Error: direction '%s' is not defined. Allowed directions: %s" % (direction, ', '.join(cls._DIR_DICT.keys()))
        inBasePath, outBasePath = cls._DIR_DICT[direction]

        inPath = os.sep.join([inBasePath, genome] + trackName)
        assert os.path.exists(inPath), 'Path does not exist: ' + inPath
        assert len(os.listdir(inPath)) != 0, 'Empty dir: ' + inPath

        outPath = os.sep.join([outBasePath, genome] + (differentOutputTrackName if differentOutputTrackName else trackName))

        return inPath, outPath

    @classmethod
    def _prepareInputOutputPaths(cls, genome, trackName, direction, differentOutputTrackName=None):
        inPath, outPath = cls._getInputOutputPaths(genome, trackName, direction, differentOutputTrackName)

        if direction == 'std_to_coll':
            pass
            #cls._resetCollected(genome, trackName, clearHistory=False)
        elif direction == 'coll_to_coll':
            nextRevisionInputDir = cls._findRevisionInputDir(inPath, next=True)
            ensurePathExists(nextRevisionInputDir + os.sep)
            for fn in [fn for fn in os.listdir(inPath) if os.path.isfile(inPath + os.sep + fn)]:
                shutil.move(inPath + os.sep + fn, nextRevisionInputDir + os.sep + fn)
            inPath = nextRevisionInputDir
        elif direction in ['coll_to_std', 'error_to_std', 'std_to_std', 'std_to_error'] \
                and not issubclass(cls, GeneralTrackDataAdder) and os.path.exists(outPath):
            for fn in [fn for fn in os.listdir(outPath) if os.path.isfile(outPath + os.sep + fn)]:
                os.remove(outPath + os.sep + fn)

        return inPath, outPath

    @classmethod
    def cleanUp(cls, genome, trackName, direction='coll_to_std', **kwArgs):
        inPath, outPath = cls._getInputOutputPaths(genome, trackName, direction)

        if direction == 'coll_to_coll':
            curRevisionInputDir = cls._findRevisionInputDir(inPath, next=False)
            if curRevisionInputDir is not None:
                for fn in [fn for fn in os.listdir(curRevisionInputDir) if os.path.isfile(curRevisionInputDir + os.sep + fn)]:
                    shutil.move(curRevisionInputDir + os.sep + fn, inPath + os.sep + fn)
                shutil.rmtree(curRevisionInputDir)

    @classmethod
    def _parseFilesInDir(cls, inPath, outPath, genome, trackName, direction, **kwArgs):
        fileWasHandled = False
        firstFile = True
        for baseFn in os.listdir(inPath):
            outFn = os.sep.join([outPath, baseFn])
            inFn = inPath + os.sep + baseFn
            if os.path.isfile(inFn) and not baseFn.startswith('.'):
                ensurePathExists(outFn)
                assert issubclass(cls, GeneralTrackDataAdder) or inFn != outFn, 'Error: input and ouput is the same file: ' + inFn
                cls.parseFile(inFn, outFn, trackName, genome=genome, firstFile=firstFile, direction=direction, **kwArgs)
                fileWasHandled = True
                print '.',
                firstFile = False
        if not fileWasHandled:
            print 'No action taken on path: ', inPath
            print 'Having contents: ', os.listdir(inPath)

    @classmethod
    def parseFiles(cls, genome, trackName, direction='coll_to_std', **kwArgs):
        inPath, outPath = cls._prepareInputOutputPaths(genome, trackName, direction)
        cls._parseFilesInDir(inPath, outPath, genome, trackName, direction, **kwArgs)

    @classmethod
    def parseAllSubTypes(cls, genome, mainTrackName, direction='coll_to_std', subTypeDepth=1, origSubTypeDepth=None, **kwArgs):
        inPath, outPath = cls._getInputOutputPaths(genome, mainTrackName, direction)
        subTypeDepth = int(subTypeDepth)
        assert subTypeDepth >= 1
        if origSubTypeDepth is None:
            origSubTypeDepth = subTypeDepth
        #inPath = os.sep.join([inPath]+mainTrackName)
        firstSubType = True
        #print '**', inPath, [x for x in os.listdir(inPath)]

        for subType in os.listdir(inPath):
            fullPath = inPath + os.sep + subType
            if not os.path.isdir(fullPath) or subType[0]=='_':
                continue

            print
            print '-' * subTypeDepth,
            print 'standardizing subFolder: ', subType

            if subTypeDepth == 1:
                try:
                    cls.parseFiles(genome, mainTrackName+[subType], direction=direction, \
                                   firstSubType=firstSubType, origSubTypeDepth=origSubTypeDepth, **kwArgs)
                except:
                    cls.cleanUp(genome, mainTrackName+[subType], direction)
                    raise
            else:
                cls.parseAllSubTypes(genome, mainTrackName+[subType], direction=direction, subTypeDepth=subTypeDepth-1, origSubTypeDepth=origSubTypeDepth, **kwArgs)

            firstSubType = False

class GeneralTrackDataAdder(GeneralTrackDataModifier):
    pass

class RemoveFirstLine(GeneralTrackDataModifier):
    "E.g. SNP-files from Sigve.."
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, **kwArgs):
#        print inFn
        inFile = open(inFn)

        if not outFn.endswith('.bed'):
            outFn += '.bed'

        ensurePathExists(outFn)
        outFile = open(outFn,'w')

        #ignore first line..
        first = True

        for line in inFile:
            if first:
                first = False
                continue
            outFile.write( line )

class ImplicitChrSegments(GeneralTrackDataModifier):
    "E.g. methylation"
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, **kwArgs):
#        print inFn
        assert(inFn.count('chr')==1)
        assert(inFn.endswith('.txt'))

        chrIndex = inFn.find('chr')
        chr = inFn[ chrIndex : inFn.find('_',chrIndex)]

        inFile = open(inFn)

        outFn += '.bed'
        ensurePathExists(outFn)
        outFile = open(outFn,'w')

        for line in inFile:
            outFile.write( chr + '\t' + line )

class OneBasedInclusive(GeneralTrackDataModifier):
    @classmethod
    def subtactOneFromStart(cls, cols):
        cols[1] = str( int(cols[1]) - 1 )
        return cols

    @classmethod
    def parseFile(cls, inFn, outFn, trackName, **kwArgs):
#        print inFn, outFn
        assert(inFn.endswith('.txt') or inFn.endswith('.point'))

        inFile = open(inFn)

        if not outFn.endswith('.bed'):
            outFn += '.bed'

        ensurePathExists(outFn)
        outFile = open(outFn,'w')

        for line in inFile:
            cols = line.strip().split('\t')
            outFile.write( '\t'.join(cls._processCols(cols)) + os.linesep )

    @classmethod
    def _processCols(cls, cols):
        return cls.subtactOneFromStart(cols)

class OneBasedInclusiveCutExtraCols(OneBasedInclusive):
    "E.g DNaseHS clusters"
    @classmethod
    def _processCols(cls, cols):
        return cls.cutExtraCols( cls.subtactOneFromStart(cols) )

    @classmethod
    def cutExtraCols(cls, cols):
        return cols[0:6]

class OneBasedInclusivePointAddNameAndScoreCutExtraCols(OneBasedInclusiveCutExtraCols):
    "E.g DNaseHS individuals"
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, **kwArgs):
        outFn += '.point'
        super(OneBasedInclusivePointAddNameAndScoreCutExtraCols, cls).parseFile(inFn, outFn, trackName)

    @classmethod
    def _processCols(cls, cols):
        return cls.cutExtraCols( cls.addNameAndScore( cls.subtactOneFromStart(cols) ) )

    @classmethod
    def addNameAndScore(cls, cols):
        return cols[0:3] + ['N/A'] + ['0'] + cols[3:]

class CreateCategoryBedFileFromUCSCRepeats(GeneralTrackDataModifier):
    """Converts a tabular repeats file downloaded from UCSC Genome Browser to categorical BED file"""
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, **kwArgs):
        inFile = open(inFn, 'r')
        outFile = open(os.path.splitext(outFn)[0] + '.category.bed', 'w')

        for line in inFile:
            if line.startswith('#'):
                continue
            cols = line.split()
    #        outFile.write('\t'.join( [cols[5], str(int(cols[6])-1), cols[7]] +\ # Caused a lot of tests to fail after segsMany (and catSegs?) was preprocessed from bed versions..
            outFile.write('\t'.join( [cols[5], str(int(cols[6])), cols[7]] +\
                                     [os.sep.join([ cols[i].replace(os.sep, '_') for i in [11,12,10] ])] +\
                                     ['0', cols[9]] ) +\
                          os.linesep)
        inFile.close()
        outFile.close()


class ConvertToGtrack(GeneralTrackDataModifier):
    """Converts tabular format to gtrack format"""
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, **kwArgs):
        inFile = open(inFn, 'r')
        outFile = open(outFn+'.gtrack','w')


        fileFormatDict = dict([('.broadPeak', 'seqid\tstart\tend\tname\tscore\tstrand\tvalue\tpValue\tqValue'),\
        ('.narrowPeak', 'seqid\tstart\tend\tname\tscore\tstrand\tvalue\tpValue\tqValue\tpeaks'),\
        ('.peaks', 'seqid\tstart\tend\tname\tstrand\tvalue'),\
        ('.bed', 'seqid\tstart\tend\tname\tvalue') ])

        fileFormat = os.path.splitext(inFn)[1]
        if fileFormat == 'bed':
            assert len(open(inFn,'r').readline().strip().split()) == len(fileFormatDict[fileFormat].split())
        print>>outFile, '##track type: valued segments'
        print>>outFile, '###' + fileFormatDict[fileFormat]
        print>>outFile, inFile.read()
        outFile.close()
        inFile.close()

class ConvertMy5cToGtrack(GeneralTrackDataModifier):

    @classmethod
    def parseFile(cls, inFn, outFn, trackName, **kwArgs):
        outFile = open(outFn+'.gtrack','w')
        colToIdDict = dict()
        resDict = defaultdict(list)
        headers = '##Track type: linked segments\n##1-indexed: true\n##Edge weights: true\n##Edge weight type: number\n###seqid\tstart\tend\tid\tedges'
        headerflag = True

        for line in open(inFn, 'r'):
            if not headerflag:
                lineTab = line.strip().split('\t')
                id, weights  = lineTab[0], lineTab[1:]
                for index, val in enumerate(weights):
                    if val !='0':
                        resDict[colToIdDict[index]].append(id+'='+val)
                    resDict[id] =['.']

            elif headerflag and line.startswith('#'):
                continue
            else:
                lineTab = line.strip().split('\t')
                colToIdDict = dict(zip(range(len(lineTab)), lineTab))
                headerflag = False


        print>>outFile, headers
        for id in sorted(resDict.keys()):
            chr, start, end = re.split('[:-]+', id.split('|')[-1])
            print>>outFile, '\t'.join([chr, start, end, id, ';'.join(resDict[id])])

        outFile.close()



#class TrivialParser(GeneralTrackDataModifier):
#    @classmethod
#    def parseFile(cls, inFn, outFn, trackName, **kwArgs):
#        print inFn
#        assert(inFn.endswith('.wig') or inFn.endswith('.bed'))
#
#        inFile = open(inFn)
#        ensurePathExists(outFn)
#        outFile = open(outFn,'w')
#
#        for line in inFile:
#            outFile.write( line )
#

class ParseSacSerSNP(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, **kwArgs):#(self, filename):

        fileObj = open(inFn, 'r')
        outFile = open(os.path.dirname(outFn) + "/track.gtrack",'w')

        outFile.write('##track type: valued points\n')
        outFile.write('##value type: category\n')
        outFile.write('##1-indexed: True\n')
        outFile.write('###'+'\t'.join(['seqid','start','value','allele','quality'])+'\n')
        for row in fileObj.read().split('\n\n'):
            tempRow = [v.strip().split(' ') for v in row.split('\n')[:2]]
            ## issues with uppercase and lowercase for snp values
            outFile.write('\t'.join(tempRow[0][1:]) + '\t' + '\t'.join([v[2] if v.find('>')>=0 else v for v in tempRow[1][3:]])+'\n')
        outFile.close()

#class ParseTrackNameFromFnHCNE(GeneralTrackDataModifier):
#    @classmethod
#    def parseFiles(cls, genome, trackName, **kwArgs):
#        inPath = os.sep.join([NONSTANDARD_DATA_PATH, genome] + trackName)
#
#        for baseFn in os.listdir(inPath):
#            subType = [baseFn.replace('HCNE_','').replace('hg18_','').replace('.wig','').replace('.bed','')]
#
#            outFn = os.sep.join([ORIG_DATA_PATH, genome] + trackName + subType + [baseFn])
#            inFn = inPath + os.sep + baseFn
#            if os.path.isfile(inFn) and not baseFn.startswith('.'):
#                if baseFn.endswith('.wig'):
#                    TrivialParser.parseFile(inFn, outFn, trackName)
#                elif baseFn.endswith('.bed'):
#                    RemoveFirstLine.parseFile(inFn, outFn, trackName)
#                print '.',



class AddGtrackHeaderLine(GeneralTrackDataModifier):

    @classmethod
    def parseFile(cls, inFn, outFn, trackName, headerLine='', **kwArgs):
#        print inFn, outFn
        if not outFn.endswith('.gtrack'):
            outFn += '.gtrack'
        ensurePathExists(outFn)

        inFile = open(inFn)
        outFile = open(outFn,'w')

        headerKwrd = headerLine.split(':')[0]
        headerLines = [inFile.readline().strip() for v in range(10)]
        headerKwrds = [v.split(':')[0] for v in headerLines]

        if not headerKwrd in headerKwrds:
            print>>outFile, headerLine
        else:
            headerLines[headerKwrds.index(headerKwrd)] = headerLine

        print>>outFile, '\n'.join(headerLines)
        outFile.write(inFile.read())

        inFile.close()
        outFile.close()




class MergeFastaFilesToSingleFastaFile(GeneralTrackDataModifier):
    '''Requires collected '''
    @classmethod
    def parseFile(cls, inFn=None, outFn=None, trackName=None, genome=None, fastaFolder='Sequence:DNA', **kwArgs):
        trackName = GenomeInfo.getChrTrackName(genome)
        outFileName = createOrigPath(genome, cls.getSequenceTrackName(genome), 'MergedChrs.fa')
        outfileIndexAccName = createOrigPath(genome,trackName, 'MergedChrs.bed', 'collected')

        ensurePathExists(outfileIndexAccName)
        ensurePathExists(outFileName)
        outIndexAccFile = open(outfileIndexAccName, 'w')
        outFile = open(outFileName, 'w')
        print>>outFile, '>MergedChrs'
        start, end = 0, 0
        chrName = 'MergedChrs'
        count = 0
        fileNames = getOrigFns( genome, fastaFolder.split(':'), '','collected')
        for fileName in fileNames:
            seqId = ''
            fastaLines=''
            for line in open(fileName,'r'):
                if line.strip()[0]=='>':
                    seqId = line.strip()[1:]
                else:
                    fastaLines+= line.strip()
            print seqId
            end += len(fastaLines)
            print>>outIndexAccFile, '\t'.join([chrName, str(start), str(end), seqId])
            outFile.write(fastaLines)
            start=end
            count+=1
            if count%100 ==0:
                print count, seqId

        outFile.write('\n')
        outFile.close()
        outIndexAccFile.close()


class MergeAllSeqIdsToSingleSeqId(GeneralTrackDataModifier):
    '''Requires '''
    @classmethod
    def parseFile(cls, inFn=None, outFn=None, trackName=None, genome=None, **kwArgs):
        trackName = GenomeInfo(genome).getPropertyTrackName(genome, 'chrs')
        print 'trackName', trackName, genome
        outFileName = createOrigPath(genome, trackName, 'MergedChrs.bed', 'collected')
        fileName = getOrigFn( genome, trackName, '')

        outFile = open(outFileName, 'w')
        start, end = 0, 0
        chrName = 'MergedChrs'


        print 'fileName', fileName
        for line in open(fileName, 'r'):
            val, startStr, endStr = line.split('\t')
            start, end = start+int(startStr), end+int(endStr)
            outFile.write('\t'.join([chrName, str(start), str(end), val])+os.linesep)
        outFile.close()


class ConvertToMergedSeqIdCoordinates(GeneralTrackDataModifier):
    #def parseFile(cls, genome, trackName, **kwArgs):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName,  genome=None, **kwArgs):
        assistingFileName = createOrigPath(genome, GenomeInfo(genome).getPropertyTrackName(genome, 'chrs'), 'MergedChrs.bed', 'collected')
        assistDict = dict()
        for line in open(assistingFileName,'r'):
            tuple= line.strip().split('\t')
            assistDict[tuple[-1]] =[int(tuple[-3]), int(tuple[-2])]
        generalChr =  tuple[0].strip()

        #outFile = open(getOrigFn(genome, trackName, ''), 'w')
        outFile = open(outFn, 'w')
        #outFile.write('##track type: segments\n###seqid\tstart\tend\toriginalsqeid\n')
        for line in open(inFn,'r'):
            lineList = line.split('\t')
            if lineList[0] in assistDict:
                start = int(lineList[1])+assistDict[lineList[0]][0]
                end = int(lineList[2])+assistDict[lineList[0]][1]
                print>>outFile, '\t'.join([generalChr, str(start), str(end), lineList[0]] +(lineList[3:] if len(lineList)>3 else []) )

            elif len(lineList)<1:
                pass
            else:
                raise InvalidFormatError('File has datalines that are incomplete..  '+ line)
        outFile.close()

class ConvertToMergedSeqIdCoordinatesFasta(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn=None, outFn=None, trackName=None, genome=None,  **kwArgs):
        assistingFileName = createOrigPath(genome, GenomeInfo(genome).getPropertyTrackName(genome, 'chrs'), 'MergedChrs.fa')
        assistList = [ x.split('\t')[-1] for x in open(assistingFileName,'r')]

        outFile = open(getOrigFn(genome, ''), 'w')
        outFile.write('>MergedChrs'+os.linesep)

        for line in open(getOrigFn( genome, '', '', 'collected'),'r'):
            if line.strip()[0]=='>':
                assert line.strip()[1:] == assistList[0], 'order of chrs must be identical for sequence and tracks: (%s :: %s)' % (line.strip()[1:], assistList[0])
                assistList.pop(0)
            elif len(line>0):
                outFile.write(line.strip()+os.linesep)
            else:
                pass
        outFile.close()

class PlainNumbers(GeneralTrackDataModifier):
    "E.g. melting"

    @classmethod
    def parseFile(cls, inFn, outFn, trackName, **kwArgs):
#        print inFn
        assert(inFn.count('chr')==1)
        chrIndex = inFn.find('chr')
        chr = inFn[ chrIndex : inFn.find('.',chrIndex)]

        if inFn.endswith('.bz2'):
            inFile = bz2.BZ2File(inFn)
            outFn = outFn.replace('.bz2','')
        else:
            inFile = open(inFn)

        outFn += '.wig'
        ensurePathExists(outFn)
        outFile = open(outFn,'w')

        outFile.write( os.linesep.join(['track type=wiggle_0 name=' + ':'.join(trackName),
                '\t'.join(['fixedStep','chrom=' + chr, 'start=1', 'step=1'])]) + os.linesep)

        for pos in xrange(GenomeInfo.getChrLen(DEFAULT_GENOME, chr)):
            #for line in inFile:
            line = inFile.readline()
            if line=='':
                print 'Warning: File to short: ',inFn
                outFile.write('0.0 nan')
            else:
                outFile.write(line)

        while inFile.readline() != '':
            print 'Warning: Extra bps in file: ' ,inFn

class WigVariableStepWithSpanAsBedGraphImporter(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, **kwArgs):
        OrigFormatConverter.wigVariableStepWithSpanToBedGraph(inFn, outFn)

#
#class SplitEachFileToSubdirImporter(GeneralTrackDataModifier):
#    @classmethod
#    def parseFiles(cls, genome, mainTrackName, **kwArgs): #directly overwrites parseFiles in plural..
#        inPath = os.sep.join([NONSTANDARD_DATA_PATH, genome] + mainTrackName)
#        for relFn in os.listdir(inPath):
#            subType = ''.join( relFn.split('.')[:-1])
#            print 'moving subtype: ', subType
#            fullPath = inPath + os.sep + relFn
#            outPath = os.sep.join([ORIG_DATA_PATH, genome] + mainTrackName + [subType,relFn])
#            ensurePathExists(outPath)
#            print outPath
#            if os.path.isfile(fullPath) and not relFn[0]=='_':
#                shutil.copy(fullPath, outPath)#+os.sep+relFn)

class FixChromOfFastaFiles(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, **kwArgs):
        assert inFn.endswith('.fa')

        inFile = open(inFn, 'r')
        header = inFile.readline()
        assert header.startswith('>')
        chr = GenomeInfo.fixChr( header.split()[0][1:] )

        outFn = os.path.dirname(outFn) + os.sep + chr + '.fa'
        outFile = open(outFn, 'w')
        outFile.write('>' + chr + ' ' + ' '.join(header.split()[1:]) + os.linesep)
        for line in inFile:
            outFile.write(line)


class MakeNewTrackStructure(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, newStructure, **kwArgs):

        #
        for root, folder, files in os.walk(os.path.dirname(inFn)):
            if folder == [] and files !=[]:
                inFn = root + os.sep + files[0]
                outFolder = os.path.dirname(outFn)
                outLen = len(outFolder.split('/'))
                outFn = outFolder + os.sep + '/'.join(inFn.split('/')[outLen:])

                break


        print 'inFn', inFn
        print 'outFn', outFn
        structList, compressList  = [], []

        lenNewStruct = 0
        for value in newStructure.split(','):

            if value.find('_'):
                tempList = []
                for val in value.split('_'):
                    lenNewStruct+=1
                    tempList.append(int(val))
                structList.append(tempList)
            else:
                lenNewStruct+=1
                structList.append(int(value))



        #structList = [int(v) for v in newStructure.split(',')]
        #print 'structList', structList, lenNewStruct

        inFnRoot = '/'.join(inFn.split('/')[:-(lenNewStruct+1)])
        outFnRoot = '/'.join(outFn.split('/')[:-(lenNewStruct+1)])
        print 'inFnRoot', inFnRoot
        print 'outFnRoot', outFnRoot
        lenRoot = len(inFnRoot.split('/'))
        for root, folders, files in os.walk(inFnRoot):
            if folders == [] and files != []:
                rootList = root.split('/')

                print 'RootList', rootList, len(rootList)
                print structList
                #assert len(rootList) == lenNewStruct, 'Error the inpath is deeper than specified'
                #newRoot = os.sep + '/'.join([rootList[lenRoot+v-1] for v in structList])
                outNewTab = []
                for val in structList:
                    if type(val) == list:
                        outNewTab.append('_'.join([rootList[lenRoot+v-1] for v in val]))
                    else:
                        outNewTab.append(rootList[lenRoot+val-1])

                newRoot = os.sep + '/'.join(outNewTab)
                shutil.copytree(root, outFnRoot + newRoot)




class SplitFasta(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, chromNamesDict, **kwArgs):
        assert any(inFn.lower().endswith(x) for x in [".fa", ".fas", ".fasta", ".fna", ".fsa", ".mpfa", ".seq"]), \
            "Error: Not a FASTA file"
        fastaFile=open(inFn, "r")
        chromFile=None
        includechromosome=False

        if isinstance(chromNamesDict, basestring):
            chromNamesDict = ast.literal_eval(chromNamesDict)

        for l in fastaFile:
            if l[0]==">":
                if chromFile is not None:
                    chromFile.close()
                ensurePathExists(outFn)
                chrDesc = l[1:].strip().split()[0]
                if chrDesc in chromNamesDict.keys():
                    newchromname=chromNamesDict[chrDesc]
                    chromFile=open(os.path.dirname(outFn) + os.sep + newchromname+".fa", "w")
                    chromFile.write(">"+newchromname+os.linesep)
                    includechromosome=True
                else:
                    includechromosome=False

            else:
                if includechromosome:
                    chromFile.write(l)
        if chromFile is not None:
            chromFile.close()
        fastaFile.close()

class FilterByRegExp(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, regExp='', numHeaderLines='0', **kwArgs):
        inFile = open(inFn)
        ensurePathExists(outFn)
        outFile = open(outFn, 'w')

        for i in range(int(numHeaderLines)):
            outFile.write(inFile.readline())

        for line in inFile:
            if len(re.findall(regExp, line)) > 0:
                outFile.write(line)

class CutColumns(GeneralTrackDataModifier):
    '''
    Selects a set of column in a particular order and outputs a new text file
    with only the selected columns. Writes the selected number of header lines
    directly to the output file without editing.

    colListStr: a comma-separated list of 0-indexed column numbers
    numHeaderLines: the number of header lines (at the top of the file)
    '''
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, colListStr='0,1,2', numHeaderLines='0', **kwArgs):
        inFile = open(inFn)
        ensurePathExists(outFn)
        outFile = open(outFn, 'w')

        colList = [int(x.strip()) for x in colListStr.split(',')]

        for i in range(int(numHeaderLines)):
            outFile.write(inFile.readline())

        for line in inFile:
            cols = line.strip().split('\t')
            outFile.write('\t'.join(cols[x] for x in colList) + os.linesep)

class SubsampleTracks(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls,inFn, outFn, numElements=None, **kwargs):
        assert numElements != None
        numElements = int(numElements)
        lines = open(inFn).readlines()
        outF = open(outFn, 'w')

        if lines[0].startswith('track'):
            outF.write( lines[0])
            lines = lines[1:]

        import numpy.random as nr
        lineNumbers = range(len(lines))
        nr.shuffle(lineNumbers)
        lineNumbers = lineNumbers[0:numElements]

        for lineNum in lineNumbers:
            outF.write( lines[lineNum] )

class ConvertVcfTo3ColBed(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls,inFn, outFn, **kwargs):
        outF = open(outFn, 'w')

        for line in open(inFn):
            if line.startswith('#'):
                continue
            chrPart, pos = line.split('\t')[0:2]
            outF.write('\t'.join(['chr'+chrPart, str(int(pos)-1), pos ]) + '\n')

class ConvertMafTo3ColBed(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls,inFn, outFn, **kwargs):
        outF = open(outFn, 'w')

        for line in open(inFn):
            if line.startswith('#'):
                continue
            if line.startswith('Hugo_Symbol'): #header..
                continue
            chrPart, start, end = line.split('\t')[4:7]
            outF.write('\t'.join(['chr'+chrPart, str(int(start)-1), end ]) + '\n')

class ICGCToGTrack(GeneralTrackDataModifier):
    '''
    Converts an ICGC tsv file into GTrack format.
    '''
    @classmethod
    def convertLine(cls, line, chrIndex, chrStartIndex, chrEndIndex, strandIndex):
        data = line.split('\t')
        chrName = data[chrIndex] if data[chrIndex].startswith('chr') else 'chr' + data[chrIndex]
        chrStart = data[chrStartIndex]
        chrEnd = data[chrEndIndex]
        strand = '+' #by definition always positive for ICGC format
        converted = [chrName, chrStart, chrEnd, strand]
        converted += [data[i] for i in range(len(data))
                      if i not in (chrIndex, chrStartIndex, chrEndIndex, strandIndex)]
        #replace empty with '.'
        converted = [x if x else '.'  for x in converted]
        return '\t'.join(converted)

    @classmethod
    def parseFile(cls, inFn, outFn, trackName, genome='hg19', trackType='segments',
                  oneIndexed='True', endInclusive='True',
                  chrLabel = 'chromosome', chrStartLbl='chromosome_start',
                  chrEndLabel = 'chromosome_end', strandLabel = 'chromosome_strand',
                  **kwArgs):
        with open(inFn) as inFile:
            inFileLines = [x.strip(' \n\r') for x in inFile.readlines()] #dont strip tabs

        inAttributeNames = [x.strip() for x in inFileLines[0].split('\t')]
        chrIndex = inAttributeNames.index(chrLabel.strip())
        chrStartIndex = inAttributeNames.index(chrStartLbl.strip())
        chrEndIndex = inAttributeNames.index(chrEndLabel.strip())
        strandIndex = inAttributeNames.index(strandLabel.strip())

        headerLines = []
        if oneIndexed and oneIndexed.lower().strip() == 'true':
            headerLines.append('##1-indexed: True')
        if trackType:
            headerLines.append('##track type: ' + trackType.strip())
        if endInclusive and endInclusive.lower().strip() == 'true':
            headerLines.append('##end inclusive:True')

        outAttributeNames = ['seqid', 'start', 'end', 'strand'] +\
         [inAttributeNames[i] for i in range(len(inAttributeNames))
          if i not in (chrIndex, chrStartIndex, chrEndIndex, strandIndex)]

        headerLines.append('###' + '\t'.join(outAttributeNames))

        if genome:
            headerLines.append('####genome=' + genome)

        outFileLines = headerLines

        for line in inFileLines[1:]:
            if line and line.strip():
                outFileLines.append(cls.convertLine(line, chrIndex, chrStartIndex,
                                                    chrEndIndex, strandIndex))

        ensurePathExists(outFn)
        with open(outFn,'w') as outFile:
            for line in outFileLines:
                print>>outFile, line


class CommonToGTrack(GeneralTrackDataModifier):

    @classmethod
    def _getAttributeNames(cls):
        raise AbstractClassError

    @classmethod
    def _convertLine(cls, line):
        splitted = line.split('\t')
        for i in cls._getColsToConvertToDot():
            if splitted[i] == '-1':
                splitted[i] = '.'
        return '\t'.join(splitted)

    @classmethod
    def _getColsToConvertToDot(cls):
        raise AbstractClassError

    @classmethod
    def parseFile(cls, inFn, outFn, trackName, **kwArgs):
        with open(inFn) as inFile:
            inFileLines = [x.strip() for x in inFile.readlines() if not
                           (x.startswith('browser') or x.startswith('track') )] #skip lines that start with 'track' or 'browser' (bed format)
        ensurePathExists(outFn)
        broadpeakAttributeNames = cls._getAttributeNames()
        with open(outFn, 'w') as outFile:
            print>>outFile, '##track type: valued segments'
            print>>outFile, '###' + '\t'.join(broadpeakAttributeNames)
            for line in inFileLines:
                print>>outFile, cls._convertLine(line)

class BroadpeakToGTrack(CommonToGTrack):

    @classmethod
    def _getAttributeNames(self):
        return ['seqid', 'start', 'end', 'name', 'score', 'strand', 'value', 'pValue', 'qValue']

    @classmethod
    def _getColsToConvertToDot(cls):
        return [-1,-2]

class NarrowpeakToGTrack(CommonToGTrack):

    @classmethod
    def _getAttributeNames(self):
        return ['seqid', 'start', 'end', 'name', 'score', 'strand', 'value', 'pValue', 'qValue', 'peak']

    @classmethod
    def _getColsToConvertToDot(cls):
        return [-1,-2,-3]


from gold.origdata.GESourceWrapper import ElementModifierGESourceWrapper
class MyElementModifier(ElementModifierGESourceWrapper):
    def __init__(self, geSource, genome=None, segmentLength='1', **kwArgs):
        super(MyElementModifier, self).__init__(geSource, genome=genome)
        self._segmentLength = int(segmentLength)
        # init of extra class members, as needed

    def _next(self, brt, ge, i): #ignore brt. ge is the GenomeElement object. i is a counter starting on 0 for the first ge
        if self.checkLength(ge):
            return ge
    def checkLength(self, ge):
        if ge.end is not None and ge.start is not None:
            return ge.end - ge.start == self._segmentLength
        else:
            return False

class FilterGTrackByGELength(GeneralTrackDataModifier):

    @classmethod
    def parseFile(cls, inFn, outFn, trackName, segmentLength='1', **kwArgs):
        try:
            int(segmentLength)
        except:
            raise InvalidFormatError('Genome element lenght must be a valid integer')

        from gold.origdata.GtrackComposer  import StdGtrackComposer

        geSource = GtrackGenomeElementSource(inFn) # reads the query track as genome elements
        modGeSource = MyElementModifier(geSource, segmentLength=segmentLength)
        composer = StdGtrackComposer(modGeSource)
        composer.composeToFile(outFn)


class SplitToSeparatChrFiles(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, baseOutFn, trackName, numHeaderLines='0', **kwArgs):
        #assert int(numHeaderLines)==0, 'not supported yet (should be easy..)'
        inFile = open(inFn)
        headerLines = ''.join([inFile.readline() for x in xrange(int(numHeaderLines))])

        ensurePathExists(baseOutFn)
        #outFile = open(outFn, 'w')
        outFiles = {}

        for line in inFile:
            if line.strip()=='':
                continue
            cols = line.strip().split()
            assert len(cols) >= 3
            chr = cols[0]
            if not chr in outFiles:
                outFn = os.path.split(baseOutFn)[0] + os.sep + chr + '_' + os.path.split(baseOutFn)[1]
                print 'creating fn: ', outFn
                outFiles[chr] = open(outFn,'w')
                outFiles[chr].write(headerLines)
            outFiles[chr].write(line)



class FilterOutNonStandardChrLines(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, genome, numHeaderLines='0', **kwArgs):
#        assert genome=='hg18' #only supported yet..
        inFile = open(inFn)
        ensurePathExists(outFn)
        outFile = open(outFn, 'w')

        for i in range(int(numHeaderLines)):
            outFile.write(inFile.readline())

        removedChrs = set([])
        removedLines = 0
#        standardChrs = ['chr'+str(x) for x in range(1,23)+list('XYM')]
        standardChrs = GenomeInfo.getExtendedChrList(genome)
        for line in inFile:
            if line.split()[0] in standardChrs:
                outFile.write(line)
            else:
                removedChrs.add(line.split()[0])
                removedLines+=1
        print 'Removed ',removedLines, ' lines, having chromosomes: ',removedChrs

class ReplaceByRegExp(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, regExp='', replaceWith='', selectedCol='', **kwArgs):
        inFile = open(inFn)
        ensurePathExists(outFn)
        outFile = open(outFn, 'w')

        for line in inFile:
            if selectedCol == '':
                outFile.write(re.sub(regExp, replaceWith, line))
            else:
                cols = line.strip().split()
                cols[int(selectedCol)] = re.sub(regExp, replaceWith, cols[int(selectedCol)])
                outFile.write('\t'.join(cols) +os.linesep)

class ShiftLines(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, linesToShiftDownwards='0', numHeaderLines='0', **kwArgs):
        inFile = open(inFn)
        ensurePathExists(outFn)
        outFile = open(outFn, 'w')

        for i in range(int(numHeaderLines)):
            outFile.write(inFile.readline())

        lines = [line for line in inFile]

        for line in lines[-int(linesToShiftDownwards):] + lines[:-int(linesToShiftDownwards)]:
            outFile.write(line)

class RemoveBeyondChrRange(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, genome, **kwArgs):
        inFile = open(inFn)
        ensurePathExists(outFn)
        outFile = open(outFn, 'w')

        for line in inFile:
            cols = line.split()
            if not 'chr' in line or len(cols) < 3:
                print 'Skipping assumed header: ', line
                continue

            start,end = [int(x) for x in cols[1:3]]
            if 0 <= start < end < GenomeInfo.getChrLen(genome, cols[0]):
                outFile.write(line)
            else:
                print 'Skipping line: ', line

class SplitFileToSubDirs(GeneralTrackDataModifier):
    """Splits each category to a seperate unique sub-track"""
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, genome, suffix='.bed', catSuffix='.category.bed', subTypeCol='3', depth='1', numHeaderLines='0', **kwArgs):
        depth = int(depth)
        subTypeCol = int(subTypeCol)
        inFile = open(inFn)
        numHeaderLines = int(numHeaderLines)
        #ensurePathExists(outFn)
        baseOutFolder, baseFn = os.path.split(outFn)

        header = ''
        for i in range(int(numHeaderLines)):
            header += inFile.readline()

        catFns = {}
        i = 0
        data = []
        for line in inFile:
            try:
                if line.strip() == '' or line.startswith('#'):
                    continue

                cols = line.strip().split('\t')
                splittedCat = cols[subTypeCol].split(os.sep)
                cat = os.sep.join( splittedCat[0:depth] )
                ending = catSuffix if len(splittedCat) > depth else suffix
                if not cat in catFns:
                    fn = os.sep.join([baseOutFolder,cat,baseFn.split('.')[0] + ending])
                    print 'creating path: ', fn
                    ensurePathExists(fn)
                    catFns[cat] = fn
                data.append([cat, '\t'.join(cols[:subTypeCol] + ([os.sep.join(splittedCat[depth:depth+1])] if len(splittedCat)>depth else [cat]) + \
                                              (cols[subTypeCol+1:] if len(cols)>4 else [])) + os.linesep])
            except:
                print line
                raise
        inFile.close()
        print 'Finished reading'
        data = sorted(data)
        print 'Finished sorting'

        prevCat = None
        outFile = None
        allOpenFiles = set([])
        for el in data:
            if el[0] != prevCat:
                if outFile is not None:
                    outFile.close()

                fn = catFns[el[0]]
                outFile = open(fn, 'w+')
                if fn not in allOpenFiles:
                    allOpenFiles.add(fn)
                    outFile.write(header)

                prevCat = el[0]
            outFile.write(el[1])
        outFile.close()

            #outFiles[cat].write(line)
            #files[cats[cat][1]] += '\t'.join(cols[:3] + ([os.sep.join(splittedCat[depth:depth+1])] if len(splittedCat)>depth else ['-']) + \
             #                             (cols[4:] if len(cols)>4 else [])) + os.linesep

class RemoveCombinedCategoryBeds(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, allSubTypes=False, **kwArgs):
        baseDir = os.sep.join(outFn.split(os.sep)[: (-2 if allSubTypes else -1) ])
        combinedFn = os.sep.join([baseDir, 'combined.category.bed'])
        print 'Removing %s' %combinedFn
        if os.path.exists(combinedFn):
            os.remove(combinedFn)

class SubtypesAsCategories(GeneralTrackDataAdder):
    'Makes a categorical file from all subtypes of a given track name, which will make is possible to select '
    '"all subTypes" for this track name. Must be run recursively, e.g. allSubTypes=True.'

    @classmethod
    def parseFile(cls, inFn, outFn, trackName, keepCategories='False', numHeaderLines='0', firstSubType=False, firstFile=False, numCols='12', **kwArgs):
        print inFn, outFn
        if isinstance(keepCategories, basestring):
            keepCategories = {'True':True, 'False':False}[keepCategories]

        if isinstance(numHeaderLines, basestring):
            numHeaderLines = int(numHeaderLines)

        if isinstance(numCols, basestring):
            numCols = int(numCols)

        if not any([inFn.endswith(x) for x in ['.bed', '.bedgraph']]):
            print "Warning: filename '%s' does not end with '.bed' or '.bedgraph'." % inFn
            return

        subDir = os.path.dirname(outFn).split(os.sep)
        #subType = subDir[-1].replace(' ', '_')
        subType = subDir[-1]
        baseDir = os.sep.join(subDir[:-1])

        combinedFn = os.sep.join([baseDir, 'combined.category.bed'])
        if firstSubType and firstFile and os.path.exists(combinedFn):
            print 'Removing %s' %combinedFn
            os.remove(combinedFn)

        print combinedFn
        outF = open(combinedFn,'a')

        for i,line in enumerate(open(inFn)):
            if i < numHeaderLines:
                continue

            cols = line.strip().split()

            if len(cols) > numCols:
                cols = cols[:numCols]

            if len(cols) < 3:
                raise InvalidFormatError('Line does not have enough columns: %s' %line)

            if len(cols) == 3:
                cols.append(subType)
            elif len(cols) > 3:
                if not keepCategories:
                    cols[3] = subType

            outF.write('\t'.join(cols) + os.linesep)

        outF.close()

class FilterOnCategoryDepth(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, genome, depth='1', **kwArgs):
        depth = int(depth)
        inFile = open(inFn)
        ensurePathExists(outFn)
        outFile = open(outFn, 'w')
        for line in inFile:
            cols = line.split()
            splittedCat = cols[3].split(os.sep)
            outFile.write( '\t'.join(cols[:3] + [os.sep.join(splittedCat[:depth])] + \
                                          (cols[4:] if len(cols)>4 else [])) + os.linesep)
        outFile.close()
        inFile.close()

class CopyAndSplitTcBedGraphToSubDirs(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, genome, **kwArgs):
        #copy:
        assert inFn.endswith('targetcontrol.bedgraph')
        ensurePathExists(outFn)
        shutil.copy(inFn, outFn)

        #split:
        inFile = open(inFn)
        #ensurePathExists(outFn)
        baseOutFolder, baseFn = os.path.split(outFn)

        outFiles = {}
        header = None
        for line in inFile:
            if header is None:
                header = line
                continue

            cols = line.split()
            cat = cols[3]
            ending = '.wig'
            if not cat in outFiles:
                fn = os.sep.join([baseOutFolder,cat,baseFn.split('.')[0] + ending])
                print 'creating path: ', fn
                ensurePathExists(fn)
                outFiles[cat] = open(fn, 'w')
                outFiles[cat].write(header)
            outFiles[cat].write(line)

        for cat in outFiles:
            outFiles[cat].close()

class PlainTransfer(GeneralTrackDataModifier):
    FILE_OPERATION = ''

    @classmethod
    def parseFile(cls, fromFn, toFn, trackName, genome, direction, **kwArgs):
        if not os.path.exists(toFn):
            print cls.FILE_OPERATION + ' from %s to %s' % (fromFn, toFn)
            ensurePathExists(toFn)
            if cls.FILE_OPERATION == 'copy':
                shutil.copy(fromFn, toFn)
            elif cls.FILE_OPERATION == 'move':
                assert direction != 'coll_to_coll', 'Error: moving file from %s to %s in collectedTracks is not supported.' % (fromFn, toFn)
                shutil.move(fromFn, toFn)
            else:
                raise
        else:
            print 'File already exists in target folder: ', toFn

class HiCParserTanay(GeneralTrackDataModifier):
    FILE_OPERATION = ''

    @classmethod
    def parseFile(cls, fromFn, toFn, trackName, genome, direction, **kwArgs):

        fromFnTab = re.split('[/.]',fromFn)
        toFnTab = re.split('[/.]',toFn)

        if fromFnTab[-1] in ['n_contact','n_smooth']:
            from collections import defaultdict

            idOverview = dict()
            idVal = dict()
            chrSizes = dict()
            resultDicts = [defaultdict(list), defaultdict(list), defaultdict(list)]

            with open('/'.join(fromFnTab[:-1])+'.cbins','r') as fileObj:
                fileObj.readline()
                for line in fileObj:
                    if line.strip() !='':
                        lineTab = line.split('\t')
                        if not chrSizes.has_key('chr'+lineTab[1]):
                            chrSizes['chr'+lineTab[1]] = GenomeInfo.getChrLen(genome, 'chr'+lineTab[1])

                        if int(lineTab[3])> chrSizes['chr'+lineTab[1]]:
                            lineTab[3] = str(chrSizes['chr'+lineTab[1]])
                        idOverview[lineTab[0]] = 'chr' + '\t'.join(lineTab[1:4])
                        idVal[lineTab[0]] = 'chr'+lineTab[1]+':'+lineTab[2]+'-'+lineTab[3]

            with open(fromFn,'r') as fileObj:
                fileObj.readline()
                for line in fileObj:
                    lineTab = line.strip().split('\t')
                    if len(lineTab)>3:
                        if fromFnTab[-1]=='n_contact':
                            resultDicts[0][lineTab[1]].append(idVal[lineTab[0]]+'='+lineTab[-1])
                            resultDicts[1][lineTab[1]].append(idVal[lineTab[0]]+'='+lineTab[-2])
                            if float(lineTab[-2]) != 0:
                                resultDicts[2][lineTab[1]].append(idVal[lineTab[0]]+'='+str(float(lineTab[-1])/float(lineTab[-2])))
                        else:
                            resultDicts[0][lineTab[0]].append(idVal[lineTab[4]]+'='+lineTab[-1])
                            resultDicts[1][lineTab[0]].append(idVal[lineTab[4]]+'='+lineTab[-2])
                            if float(lineTab[-2]) != 0:
                                resultDicts[2][lineTab[0]].append(idVal[lineTab[4]]+'='+str(float(lineTab[-1])/float(lineTab[-2])))

            mal = "##Track type: linked segments\n##1-indexed: false\n##End inclusive: false\n##Edge weights: true\n##Edge weight type: number\n###seqid\tstart\tend\tid\tedges"

            path = '/'.join(toFnTab[:-1]+[toFnTab[-2]+'_%s',toFnTab[-2]+'_%s.gtrack'])
            print path
            for index, trackType in  enumerate(['obs', 'exp', 'ratio']):
                ensurePathExists(path % (trackType, trackType))
                with open(path % (trackType, trackType),'w') as utfil:
                    print>>utfil, mal
                    for key in resultDicts[index].keys():
                        print>>utfil, idOverview[key]+'\t'.join(['',idVal[key],''])+';'.join(resultDicts[index][key])


class RenameTrackBasedOnCellType(GeneralTrackDataModifier):

    @classmethod
    def parseFile(cls, fromFn, toFn, trackName, genome, **kwArgs):
        from quick.extra.RenameTrack import renameTrack
        from gold.description.TrackInfo import TrackInfo
        ti = TrackInfo(genome, trackName)
        if ti.cellType != '' and not ti.cellType in trackName:
            renameTrack(genome, trackName, trackName[:-1]+[ti.cellType]+[trackName[-1]])




class RenameTrackBasedOnRegExp(GeneralTrackDataModifier):

    @classmethod
    def parseFile(cls, fromFn, toFn, trackName, genome, replaceStr='/', newTrackNameDir=None, **kwArgs):
        from quick.extra.RenameTrack import renameTrack
        tnStr = trackName[-1]
        newTrackNameDir = [v for v in trackName[:-1]] if newTrackNameDir in [None,''] else newTrackNameDir.split(':')
        for repl in replaceStr.split(','):
            replTab = repl.strip().split('/')
            tnStr = tnStr.replace(replTab[0], replTab[1])
        print trackName
        newTrackNameDir.append(tnStr)
        isEqualTn = True
        if len(newTrackNameDir) != len(trackName):
            isEqualTn = False
        else:
            for i in range(len(trackName)):
                if newTrackNameDir[i] != trackName[i]:
                    isEqualTn = False
                    break
        if not isEqualTn:
            try:
                renameTrack(genome, trackName,newTrackNameDir)
                print 'Moved:', trackName
            except:
                print 'Not moved:', trackName, newTrackNameDir[-1]




class CropSegmentsCrossingBorders(GeneralTrackDataModifier):

    @classmethod
    def parseFile(cls, fromFn, toFn, trackName, genome, direction, numHeaderLines=1, seqIdCol=0, endPosCol=2, **kwArgs):
        print fromFn

        numHeaderLines, seqIdCol, endPosCol = int(numHeaderLines), int(seqIdCol), int(endPosCol)
        ensurePathExists(toFn)
        with open(toFn,'w') as outFile:
            with open(fromFn) as inFile:
                for index in range(numHeaderLines):
                    outFile.write(inFile.readline())

                chrSizeDict={}
                for line in inFile:
                    lineTab = line.split('\t',endPosCol+1)
                    seqId = lineTab[seqIdCol]
                    if seqId not in chrSizeDict:
                        if seqId not in GenomeInfo.getExtendedChrList(genome):
                            continue
                        chrSizeDict[seqId] = GenomeInfo.getChrLen(genome, seqId)

                    if len(lineTab) > endPosCol:
                        if int(lineTab[endPosCol]) > chrSizeDict[seqId]:
                            print '\t'.join(lineTab)
                            lineTab[endPosCol] = str(chrSizeDict[seqId])
                        outFile.write('\t'.join(lineTab))


class HiCParserSdsc(GeneralTrackDataModifier):
    FILE_OPERATION = ''

    @classmethod
    def parseFile(cls, fromFn, toFn, trackName, genome, direction, **kwArgs):
        from quick.util.CommonFunctions import changedWorkingDir

        fromFnTab = re.split('[/]',fromFn)
        toFnTab = re.split('[/]',toFn)
        toRootFolder = '/'.join(toFnTab[:-1])
        rootFolder = '/'.join(fromFnTab[:-1])
        idFolders = [v for v in os.listdir(rootFolder) if not v in ['20kb','40kb', 'README.txt']]
        if len(idFolders)>0:
            from collections import defaultdict
            idOverviews = dict([(v, defaultdict(list)) for v in idFolders])
            idVal = dict()
            chrSizes = dict()
            resultDicts = [defaultdict(list), defaultdict(list), defaultdict(list)]
            for idFolder in  idFolders:
                with changedWorkingDir(os.path.join(rootFolder,  idFolder)):
                    with open(glob('*.*')[0],'r') as fileObj:
                        fileObj.readline()
                        prevChr = prevEnd = None
                        for index, line in enumerate(fileObj):
                            if line.strip() !='':

                                lineTab = line.split('\t')
                                extraVal = False
                                if not lineTab[0] in [None,prevChr] and lineTab[1]!='0' :
                                    extraVal = '0'
                                elif int(lineTab[1])>int(prevEnd):
                                    extraVal = prevEnd
                                if extraVal:
                                    keyTuple, id = [lineTab[0],extraVal,lineTab[1]], lineTab[0]+':'+extraVal+'-'+lineTab[1]
                                    key = '\t'.join(keyTuple)
                                    columns = key+'\t'+id
                                    idOverviews[idFolder][lineTab[0]].append(id)
                                    idVal[idFolder+key] = columns
                                    print idFolder+key
                                prevEnd, prevChr = lineTab[2], lineTab[0]


                                key = '\t'.join(lineTab[:3])
                                if not chrSizes.has_key('chr'+lineTab[1]):
                                    chrSizes[lineTab[0]] = GenomeInfo.getChrLen(genome, lineTab[0])

                                lineTab[2] = str(chrSizes[lineTab[0]]) if int(lineTab[2])> chrSizes[lineTab[0]] else lineTab[2]
                                id = lineTab[0]+':'+'-'.join(lineTab[1:3])
                                columns = '\t'.join(lineTab[:3]+[id])
                                idOverviews[idFolder][index].append(id)
                                idVal[idFolder+key] = columns

            mal = "##No overlapping elements: true\n##Track type: linked segments\n##1-indexed: false\n##End inclusive: false\n##Edge weights: true\n##Edge weight type: number\n###seqid\tstart\tend\tid\tedges"
            for subfolder in ['20kb','40kb']:
                for idFolder in os.listdir(rootFolder+'/'+subfolder+'/'):
                    with changedWorkingDir(rootFolder+'/'+os.path.join(subfolder, idFolder)):
                        for pattern in ['*kb.matrix', '*00.matrix']:
                            patternToOutFileFolder = {'*kb.matrix':'Observed', '*00.matrix':'Normalised'}
                            utfilPath = os.path.join(toRootFolder, '/'.join([patternToOutFileFolder[pattern]+'/'+subfolder, idFolder+'/'+idFolder+'.gtrack']))
                            ensurePathExists(utfilPath)
                            print utfilPath
                            with open(utfilPath, 'w') as utfil:
                                print>>utfil, mal
                                for hiCfile in glob(pattern):
                                    chrSize= GenomeInfo.getChrLen(genome, hiCfile.split('.')[0])
                                    idList = []
                                    idVal = dict()
                                    with open(hiCfile,'r') as fileObj:
                                        for line in fileObj:
                                            lineTab = line.split('\t' ,3)
                                            columns = '\t'.join(lineTab[:2]+[str(chrSize)]) if int(lineTab[2])>chrSize else '\t'.join(lineTab[:3])
                                            startPoint = lineTab[1][:-3] +'k' if len(lineTab[1])>3 and lineTab[1][-3:] == '000' else lineTab[1]
                                            id = lineTab[0]+':'+startPoint+'+'+subfolder[:-1]
                                            idList.append(id)
                                            idVal[idFolder+'\t'.join(lineTab[:3])] = columns+'\t'+id+'\t'

                                    with open(hiCfile,'r') as fileObj:
                                        for line in fileObj:
                                            lineTab = line.split('\t')
                                            columns = idVal[idFolder+'\t'.join(lineTab[:3])]

                                            columns+=';'.join([idList[index]+'='+val for index, val in enumerate(lineTab[3:])])
                                            print>>utfil, columns


class PlainMover(PlainTransfer):
    FILE_OPERATION = 'move'

class PlainCopier(PlainTransfer):
    FILE_OPERATION = 'copy'

class AddFileExtension(PlainCopier):
    @classmethod
    def parseFile(cls, fromFn, toFn, trackName, genome, direction, extension='', **kwArgs):
        assert extension != '' and extension[0] != '.'
        return PlainCopier.parseFile(fromFn, toFn + '.' + extension, trackName, genome, direction, **kwArgs)

class CreateTrackDirectoriesFromFileName(PlainCopier):
    'Creates track directories from the name of the files with the appropriate suffix (comma-separated), '
    'moving each file into the appropriate directory.'

    @classmethod
    def parseFile(cls, inFn, outFn, trackName, suffixList='bed', **kwArgs):
        print inFn, outFn
        suffixList = [x.strip() for x in suffixList.split(',')]

        fileSuffix = None
        for suffix in suffixList:
            if inFn.endswith('.' + suffix):
                fileSuffix = '.' + suffix

        print fileSuffix
        if fileSuffix:
            baseOutDir = os.path.dirname(outFn)
            baseInFn = os.path.basename(inFn)
            newOutFn = os.path.sep.join([baseOutDir, baseInFn[:-len(fileSuffix)], baseInFn])
            print inFn, newOutFn

            PlainCopier.parseFile(inFn, newOutFn, trackName, **kwArgs)

class FlattenDirectoryStructure(PlainCopier):
    'Flattens a directory structure into one level. Must be run recursively, e.g. allSubTypes=True.'

    @classmethod
    def parseFile(cls, inFn, outFn, trackName, genome, direction, origSubTypeDepth=0, **kwArgs):
        assert origSubTypeDepth > 0

        flattenedTrackName = trackName[:-origSubTypeDepth] + [' - '.join(trackName[-origSubTypeDepth:])]
        inPath, flattenedOutPath = cls._getInputOutputPaths(genome, trackName, direction, differentOutputTrackName=flattenedTrackName)
        flattenedOutFn = flattenedOutPath + os.sep + os.path.basename(outFn)

        print inFn, flattenedOutFn

        PlainCopier.parseFile(inFn, flattenedOutFn, trackName, genome, direction, **kwArgs)

class ChangeToValuedBedIfFloatVal(PlainCopier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, **kwArgs):
        if inFn.endswith('.bed') and \
            not any(inFn.endswith(suffix) for suffix in ['valued.bed','marked.bed']):
            for line in open(inFn):
                cols = [x.strip() for x in line.split('\t')]
                if len(cols) == 1:
                    continue
                if len(cols) >= 5:
                    try:
                        val = int(cols[4])
                        if val < 0 or val > 1000:
                            raise Exception()
                    except:
                        try:
                            float(cols[4])
                            outFn = outFn.replace('.bed','.valued.bed')
                            break
                        except:
                            raise InvalidFormatError('Fifth column of BED file is not a number: ' + cols[4])

        PlainCopier.parseFile(inFn, outFn, trackName, **kwArgs)

class TrackFileCopier(GeneralTrackDataAdder, PlainTransfer):
    FILE_OPERATION = 'copy'
    @classmethod
    def parseFiles(cls, genome, trackName, newTrackName, direction='std_to_std', parentsAsPrefix='False', **kwArgs):
        assert newTrackName is not None, 'You must provide a new track name'
        newTrackName = newTrackName.replace('/',':').split(':')

        parentsAsPrefix = ast.literal_eval(parentsAsPrefix)
        assert parentsAsPrefix in [False, True]

        inPath, outPath = cls._prepareInputOutputPaths(genome, trackName, direction, differentOutputTrackName=\
                                                       (newTrackName[:-1] + [trackName[-2] + ' - ' + newTrackName[-1]] if parentsAsPrefix else newTrackName))

        cls._parseFilesInDir(inPath, outPath, genome, trackName, direction=direction, **kwArgs)


class TrackFullTreeCopier(GeneralTrackDataAdder):
    @classmethod
    def parseAllSubTypes(cls, genome, mainTrackName, **kwArgs):
        print "Argument 'subTypeDepth' ignored..."
        cls.parseFiles(genome, mainTrackName, **kwArgs)

    @classmethod
    def parseFiles(cls, genome, trackName, newTrackName, direction='std_to_std', **kwArgs):
        assert newTrackName is not None, 'You must provide a new track name'
        newTrackName = newTrackName.replace('/',':').split(':')

        inPath, outPath = cls._prepareInputOutputPaths(genome, trackName, direction, differentOutputTrackName=newTrackName)

        print 'Copy from %s to %s' % (inPath, outPath)
        shutil.copytree(inPath, outPath)

class RemoveEmptyFiles(GeneralTrackDataModifier):
    @classmethod
    def parseFiles(cls, genome, trackName, direction='std_to_std', **kwArgs):
        inPath, outPath = cls._prepareInputOutputPaths(genome, trackName, direction)

        if all([os.path.getsize(os.sep.join([outPath, baseFn])) == 0 \
                for baseFn in os.listdir(inPath)]):
            print 'Removing directory %s' %inPath
            shutil.rmtree(inPath)

class RemoveSmallFiles(GeneralTrackDataModifier):
    @classmethod
    def parseFiles(cls, genome, trackName, minNumLines=0, direction='std_to_std', **kwArgs):
        inPath, outPath = cls._prepareInputOutputPaths(genome, trackName, direction)

        if all([len(open(os.sep.join([outPath, baseFn]), 'r').readlines()) < int(minNumLines) \
                for baseFn in os.listdir(inPath)]):
#            print inPath, len(open(os.sep.join([ORIG_DATA_PATH, genome] + trackName + [baseFn]), 'r').readlines())
            print 'Removing directory %s' %inPath
            shutil.rmtree(inPath)

class FilterOnColumnVal(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, genome, valCol='3', valType='float', valKeepFunc='lambda x:True', append='False', **kwArgs):
        inFile = open(inFn)
        ensurePathExists(outFn)
        if isinstance(append, basestring):
            append = ast.literal_eval(append)
        outFile = open(outFn, 'a' if append else 'w')
        for line in inFile:
#            if line.startswith('track'):
#                continue
            cols = line.split()
            valCol = int(valCol)
            if not valCol < len(cols):
                continue
            if isinstance(valKeepFunc, basestring):
                valKeepFunc = ast.literal_eval(valKeepFunc)
            if isinstance(valType, basestring):
                valType = ast.literal_eval(valType)
            if not valKeepFunc(valType(cols[valCol])):
                continue
            outFile.write( '\t'.join(cols) + os.linesep)
        outFile.close()
        inFile.close()

class ShuffleAndAddColumns(GeneralTrackDataModifier):
    '''
    Shuffle columns and add new columns with expression. the param colOrder is the specification for changing /ordering data lines
    colOrder = c0 c2 c2+1 c1 c3 puts column 0 and 2 then adds new column with expression(c2+1), this expr will do addition if c2 is int else string concat
    after exp follow column 1 and 3
    '''
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, genome, numHeaderLines='0', colOrder=None, **kwArgs):
        if colOrder:
            aeval = Interpreter()

            inFile = open(inFn)
            ensurePathExists(outFn)
            outFile = open(outFn, 'w')
            for line in range(int(numHeaderLines)):
                outFile.write(inFile.readline())

            colOrderTab = colOrder.strip().split()
            colOrderTypeTab = [int]
            for line in inFile:
                lineTab = line.strip().split('\t')
                for i in range(len(lineTab)):
                    val = int(lineTab[i]) if lineTab[i].isdigit() else lineTab[i]
                    aeval.symtable['c'+str(i)] = val
                outStr = ''
                for v in colOrderTab:
                    try:
                        outStr += str(aeval(v)) +'\t'
                    except:
                        for i in range(len(lineTab)):
                            if v.find('c'+str(i)):
                                aeval.symtable['c'+str(i)] = str(aeval.symtable['c'+str(i)])

                        outStr += str(aeval(v)) +'\t'
                print>>outFile, outStr.strip()

            outFile.close()
            inFile.close()

    @classmethod
    def _getHandleOperatorExpr(cls, lineTab, item, operator, colReferenceSet):
        itemTab = item.split('+')
        tempval = cls._getcorrectValue(lineTab, itemTab[0], colReferenceSet) + cls._getcorrectValue(lineTab, itemTab[1], colReferenceSet) if operator == '+' else cls._getcorrectValue(lineTab, itemTab[0], colReferenceSet) + cls._getcorrectValue(lineTab, itemTab[1], colReferenceSet)
        if len(itemTab)>2:
            for subItem in itemTab[2:]:
                if operator == '+':
                    tempval+=cls._getcorrectValue(lineTab, subItem, colReferenceSet)
                else:
                    tempval-=cls._getcorrectValue(lineTab, subItem, colReferenceSet)

        return str(tempval)

    @classmethod
    def _getcorrectValue(cls, lineTab, item, colReferenceSet):
        if item.find('"')>=0:
            return item.replace('"','')
        elif item.isdigit():
            return int(item)
        elif item in colReferenceSet:
            value = lineTab[int(item[1:])]
            return value.replace('"','') if not value.isdigit() else int(value)
        else:
            return item

class ImportTabularToGtrack(GeneralTrackDataModifier):
    '''Imports a tabular file strips the headerlines and makes a gtrack format of the file'''
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, genome, columnsSpec='seqid start end', numHeaderLines='0', endInclusive='False', oneIndexed='False',  **kwArgs):
        inFile = open(inFn)
        ensurePathExists(outFn)
        outFile = open(outFn+('.gtrack' if not outFn.endswith('.gtrack') else ''), 'w')

        if isinstance(oneIndexed, basestring):
            oneIndexed = ast.literal_eval(oneIndexed)
        if isinstance(endInclusive, basestring):
            endInclusive = ast.literal_eval(endInclusive)

        if oneIndexed:
            outFile.write('##1-indexed: True\n')
        if endInclusive:
            outFile.write('##end inclusive: True\n')

        columnsList = columnsSpec.split()
        inverseColumnSpec = dict([(tuple(x[1]),x[0]) for x in GtrackGenomeElementSource.DEFAULT_COLUMN_SPEC.items()])
        result = []
        for i in inverseColumnSpec.keys():
            if len(set(list(i))-set(columnsList))==0:
                result.append(i)
        trackType = ''
        tempLen = 0
        if len(result)>0:
            for i in result:
                if len(i)>tempLen:
                    tempLen = len(i)
                    trackType = inverseColumnSpec[i]

        outFile.write('##track type: '+trackType+'\n')
        outFile.write('###'+'\t'.join(columnsList)+'\n')

        for line in range(int(numHeaderLines)):
            inFile.readline()

        for line in inFile:
            outFile.write(line.replace(' ', '\t'))

        outFile.close()
        inFile.close()

class FixNonUnixLineShifts(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, genome, **kwArgs):
        inFileStr = open(inFn,'r').read().replace('\r\n','\n').replace('\r', '\n')
        ensurePathExists(outFn)
        open(outFn, 'w').write(inFileStr)

class ImportMitfExcel(GeneralTrackDataModifier):#
    '''Imports a csv file strips the headerlines and makes a bed/gtrack format(segments) of the file'''
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, genome, numHeaderLines='1', **kwArgs):

        inFile = open(inFn,'r')
        ensurePathExists(outFn)
        outFile = open(outFn, 'w')

        for line in range(int(numHeaderLines)):
            inFile.readline()

        for line in inFile:
            lineRow = [v.split('/')[0].replace(':','-').split('-') for index,v in enumerate(line.strip().split('\t')) if not index in [0,2]]
            start = int(lineRow[0][1])
            for tf in lineRow[1:]:
                outFile.write('\t'.join([lineRow[0][0], str(start+int(tf[0])), str(start+int(tf[1]))]) +'\n')

        outFile.close()
        inFile.close()

#class LambdaOnSelectedColumn(GeneralTrackDataModifier):
#    '''Evaluates a custom lambda function on a selected column, replacing the column value with what the lambda evaluates to
#    Example: 'lambda x:str(int(x)*2) would replace the values at the selected column with that of its double..
#    '''
#    @classmethod
#    def parseFile(cls, inFn, outFn, trackName, genome, col='3', customLambda='lambda x:x', **kwArgs):
#        pass
#        inFile = open(inFn)
#        ensurePathExists(outFn)
#        outFile = open(outFn, 'w')
#        for line in inFile:
##            if line.startswith('track'):
##                continue
#            cols = line.split()
#            valCol = int(valCol)
#            if not valCol < len(cols):
#                continue
#            if not Interpreter()(valKeepFunc)(float(cols[valCol])):
#                continue
#            outFile.write( '\t'.join(cols) + os.linesep)
#        outFile.close()
#        inFile.close()

class CalculateHypergeometricPVal(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, genome, n='1', minQ='2', excludeCats='[]', onlyIncludeCatsFn='', minArticles='0', \
                  maxPval='1.0', numTests='1', useLog='True', increaseEnds='False', makeCategoryBed='False', **kwArgs):
        from proto.RSetup import r

        minArticles = int(minArticles)

        inFile = open(inFn)
        ensurePathExists(outFn)

        assert outFn.endswith('.bed')
        if ast.literal_eval(makeCategoryBed) and not outFn.endswith('.category.bed'):
            outFn = outFn.replace('.bed', '.category.bed')
        outFile = open(outFn, 'w')

        if onlyIncludeCatsFn != '':
            onlyIncludeCats = [line.strip() for line in open(onlyIncludeCatsFn, 'r')]
        else:
            onlyIncludeCats = None

        hasWritten = False

        for line in inFile:
            cols = line.strip().split()
            if onlyIncludeCats is not None:
                if cols[3] not in onlyIncludeCats:
                    continue
            else:
                if cols[3] in ast.literal_eval(excludeCats):
                    continue

            q, m, n, k = int(cols[6]), int(cols[7]), int(n) - int(cols[7]), int(cols[8])
            if k < minArticles:
                outFile.close()
                inFile.close()
                return

            if q < int(minQ):
                continue

            pval = r('function(q, m, n, k, log) { phyper'
                     '(q, m, n, k, lower.tail=FALSE, log.p=log) }')\
                     (q, m, n, k, ast.literal_eval(useLog))
            maxPvalBonfCorr = float(maxPval)/int(numTests)

            if useLog:
                from math import log
                maxPvalBonfCorr = log(maxPvalBonfCorr)
            if pval > maxPvalBonfCorr:
                continue
            if ast.literal_eval(increaseEnds):
                cols[2] = str(int(cols[2]) + 1)

            outFile.write('\t'.join(cols[0:4] + [str(pval), cols[5]]) + os.linesep)
            hasWritten = True

        outFile.close()
        inFile.close()

        if not hasWritten:
            outDir = os.path.dirname(outFn)
            print 'Nothing written. Removing directory %s' %outDir
            shutil.rmtree(outDir)

class RemapCategoryColumn(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, genome, insuffix='bed', outsuffix='category.bed', catCol='3', shelveMapFile='', **kwArgs):
        inFile = open(inFn)
        outFn = outFn.replace(insuffix, outsuffix)
        ensurePathExists(outFn)
        outFile = open(outFn, 'w')
        if not os.path.exists(shelveMapFile):
            print 'Map file \'%s\' does not exist.' % shelveMapFile
            sys.exit(0)
        mapFile = safeshelve.open(shelveMapFile, 'r')

        for line in inFile:
            if line.startswith('track'):
                continue
            cols = line.strip().split()
            catCol = int(catCol)
            if not catCol < len(cols):
                continue
            if cols[catCol] in mapFile:
                for cat in mapFile[cols[catCol]]:
                    outFile.write( '\t'.join([cols[x] for x in [0,1,2]] + [cat] + [cols[x] for x in range(4, len(cols))]) + os.linesep)

        mapFile.close()
        outFile.close()
        inFile.close()

class ExpandBedSegments(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, genome, upFlank='0', downFlank='0',
                  treatTrackAs='segments', removeChrBorderCrossing='False', suffix='bed', **kwArgs):
        assert removeChrBorderCrossing in [False, True, 'False', 'True']
        removeChrBorderCrossing = ast.literal_eval(removeChrBorderCrossing)

        from gold.util.CommonFunctions import parseShortenedSizeSpec, getFileSuffix
        upFlank = parseShortenedSizeSpec(upFlank)
        downFlank = parseShortenedSizeSpec(downFlank)

        from quick.application.GalaxyInterface import GalaxyInterfaceTools
        GalaxyInterfaceTools.expandBedSegments(inFn, outFn, genome, upFlank, downFlank,
                                               treatTrackAs=treatTrackAs,
                                               removeChrBorderCrossing=removeChrBorderCrossing,
                                               suffix=suffix)

class ImportBarJoseph(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, genome, **kwArgs):
        id2Name = reverseDict( safeshelve.open(DATA_FILES_PATH + '/pwmName2id.shelf') )

        outF = open(outFn+'.category.bed', 'w')
        header=True
        for line in open(inFn):
            cols = line.split()
            if header:
                assert cols[0:3] == ['chr','position','gene']
                pwmIds = cols[3:]
                ignoredIds = [id for id in pwmIds if not id.lower() in id2Name]
                print 'Warning! Ignoring %i out of %i pwm IDs: '%(len(ignoredIds),len(pwmIds)), ignoredIds
                header = False
            else:
                positionData = cols[0:2] + [str(int(cols[1])+1)]
                pwmIndicators = cols[3:]
                assert len(pwmIndicators) == len(pwmIds)
                for pwmIndex in range(len(pwmIndicators)):
                    if pwmIds[pwmIndex] in ignoredIds:
                        continue
                    if pwmIndicators[pwmIndex] == '1':
                        outF.write('\t'.join(positionData+[id2Name[pwmIds[pwmIndex]]]) + os.linesep)

class RemoveDuplicateLines(GeneralTrackDataModifier):
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, **kwArgs):
        ensurePathExists(outFn)
        outFile = open(outFn, 'w')
        lineSet = set()
        with open(inFn) as f:
            fileLines = f.readlines()
        for line in fileLines:
            if not line in lineSet:
                lineSet.add(line)
                outFile.write(line)
        outFile.close()


def getStandTrackFileToolCache(genome, trackName):
    StandInfoShelve = safeshelve.open(SHELVE_FN, 'r')
    stored = StandInfoShelve.get(genome+':'+':'.join(trackName))
    StandInfoShelve.close()
    return stored

def setStandTrackFileToolCache(genome, trackName, args):
    StandInfoShelve = safeshelve.open(SHELVE_FN)
    StandInfoShelve[':'.join([genome, ':'.join(trackName)])] = str(args)
    StandInfoShelve.close()

def getFormattedParamList(parserClass, argStr='%s', kwArgStr='%s=%s'):
    paramList = []
    cls = globals()[parserClass]
    for methodName in ['parseFiles', 'parseFile']:
        if not hasattr(cls, methodName):
            continue

        methodObj = getattr(cls, methodName)
        argspec = inspect.getargspec(methodObj)
        methodParams = argspec.args
        defaultVals = [] if not argspec.defaults else list(argspec.defaults)

        numMandatoryParams = len(methodParams) - len(defaultVals)
        for i in range(len(methodParams)):
            if not methodParams[i] in GeneralTrackDataModifier.EXCLUDE_PARAMS:
                if i < numMandatoryParams:
                    paramList.append(argStr % methodParams[i])
                else:
                    defaultVal = defaultVals[i-numMandatoryParams]
                    if isinstance(defaultVal, basestring):
                        defaultVal = '"%s"' % defaultVal
                    else:
                        defaultVal = str(defaultVal)
                    paramList.append(kwArgStr % (methodParams[i], defaultVal))
    return paramList

def getParserClassList():
    return sorted([x.__name__ for x in globals().values() if type(x)==type(GeneralTrackDataModifier) \
        and issubclass(x,GeneralTrackDataModifier) \
        and x.__name__ not in ['GeneralTrackDataModifier', 'GeneralTrackDataAdder', 'PlainTransfer']])

def formatParserClassWithParams(parserClass):
    paramList = getFormattedParamList(parserClass)
    return '%s(%s)' % (parserClass, ', '.join(paramList))

def getParserClassDocString(parserClass):
    return inspect.getdoc(globals()[parserClass])

def printUsage():
    parserClassList = getParserClassList()
    for i,parserClass in enumerate(parserClassList):
        parserClassList[i] = formatParserClassWithParams(parserClass)

    print ''
    print "Usage: python StandardizeTrackFiles.py genome trackName:subtype parserClassName [direction=coll_to_std] [allSubTypes=False] [subTypeDepth=1] [other keyword arguments..]"
    print 'Direction is one of: ' + ', '.join(['"%s"' % x for x in GeneralTrackDataAdder._DIR_DICT.keys()])
    print "NB: Adding the term 'allSubtypes=True' will assume subtypes are located in subdirectories.."
    print ''
    print 'Available parser classes'
    print '------------------------'
    print os.linesep.join(parserClassList)
    print ''
    print "For documentation on a parser class, try: 'python StandardizeTrackFiles.py -h parserClassName'"
    print ''

def runParserClassDirectly(parserClassName, inFn, outFn, **kwArgs):
    globals()[parserClassName].parseFile(inFn, outFn, trackName=None, genome=None, **kwArgs)

def runParserClass(args, printUsageWhenError=True):
    genome = args[0]
    trackName = args[1].replace('/',':').split(':')
    parserClass = args[2]
    kwArgs = dict((kwArg[0:kwArg.find('=')], kwArg[kwArg.find('=')+1:]) for kwArg in args[3:])
    setStandTrackFileToolCache(genome, trackName, args)

    if 'allSubTypes' in kwArgs and kwArgs['allSubTypes'] in [True,'True']:
        globals()[parserClass].parseAllSubTypes(genome, trackName, **kwArgs)
    else:
        try:
            globals()[parserClass].parseFiles(genome, trackName, **kwArgs)
        except:
            globals()[parserClass].cleanUp(genome, trackName, **kwArgs)
            raise

class AddChrExplicitlyInBedFile(GeneralTrackDataModifier):
    "Take a file in ENSEMBL chromosome naming and change to UCSC chr naming (e.g. from 1 to chr1)"
    @classmethod
    def parseFile(cls, inFn, outFn, trackName, **kwArgs):
        inFile = open(inFn)

        outFn += '.bed'
        ensurePathExists(outFn)
        outFile = open(outFn,'w')

        for line in inFile:
            cols = line.strip().split()
            cols[0] = 'chr' + cols[0]
            outFile.write( '\t'.join(cols) +'\n')


if __name__ == "__main__":
    if len(sys.argv)==3 and sys.argv[1] == '-h':
        parserClass = sys.argv[2]

        if parserClass in getParserClassList():
            print ''
            print 'Documentation for parser class: ' + parserClass
            print '--------------------------------' + '-'*len(parserClass)
            print 'Usage: ' + formatParserClassWithParams(parserClass)
            print ''
            docStr = getParserClassDocString(parserClass)
            if docStr is None:
                print '(no documentation)'
            else:
                print docStr
            print ''
        else:
            print ''
            print "Error: parser class '%s' does not exist." % parserClass
            print ''
        sys.exit(0)

    if not (len(sys.argv) == 4 or ( len(sys.argv) > 4 and \
                                    all(sys.argv[i].find('=') != -1 for i in range(4,len(sys.argv))) )):
        printUsage()
        sys.exit(0)

    runParserClass(sys.argv[1:])

