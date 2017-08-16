#!/usr/bin/env python
import ast
import copy
import math
import os.path
import re
import shutil

import numpy

import gold.util.CommonFunctions as gcf
import quick.util.CommonFunctions as qcf
import third_party.safeshelve as safeshelve
from config.Config import HB_SOURCE_CODE_BASE_DIR, NONSTANDARD_DATA_PATH, STATIC_PATH
from gold.description.AnalysisManager import AnalysisManager
from gold.description.TrackInfo import TrackInfo
from gold.track.GenomeRegion import GenomeRegion
from gold.track.Track import PlainTrack
from quick.application.AutoBinner import AutoBinner
from quick.origdata.OrigTrackFnSource import OrigTrackNameSource
from quick.util.GenomeInfo import GenomeInfo


# Note: do not import functions here, as they will become callable from the command line

def getCategorySetForSubTracks(genome, baseTrackName, shelveFn):
    """genome baseTrackName shelveFn"""
    baseTrackName = re.split('/|:',baseTrackName)
    mapping = {}
    for trackName in OrigTrackNameSource(genome, baseTrackName):
        if trackName == baseTrackName:
            continue
        
        subTrackName = trackName[len(baseTrackName):]
        
        basePath = gcf.createOrigPath(genome, trackName)
        relFns = [x for x in os.listdir( basePath) if x[0] not in [',']]
        assert len(relFns) == 1, 'only tracks with single file is supported, thus not: ' + str(relFns)
        fn = basePath + os.sep + relFns[0]
        try:
            categories = list(set([line.split()[3] for line in open(fn) if line.strip()!='']))
        except:
            print 'Error, at filename %s and current line: %s' %(fn,line)
            raise
        
        mapping[':'.join(subTrackName)] = categories
    shelf = safeshelve.open(shelveFn)
    shelf.update(mapping)
    shelf.close()

def _createPos2NameShelf(pos2NameShelfFn, nameList):
    if pos2NameShelfFn is not None:
        pos2NameShelf = safeshelve.open(pos2NameShelfFn)
        
        for i,name in enumerate(nameList):
            assert name.startswith(str(i+1))
            name = ' '.join(name.split(' ')[1:])
            if name.find(' (') != -1 and name.endswith(')'):
                name = ' ('.join(name.split(' (')[:-1])
            pos2NameShelf[repr(i+1)] = name.lower()
        
        pos2NameShelf.close()

def _createPos2ElCountShelf(pos2ElCountShelfFn, nameList):
    if pos2ElCountShelfFn is not None:
        if len(nameList)>0 and not (nameList[0].find(' (') != -1 and nameList[0].endswith(')')):
            return
        
        pos2ElCountShelf = safeshelve.open(pos2ElCountShelfFn)
        
        for i,name in enumerate(nameList):
            assert name.startswith(str(i+1))
            elCount = name.split(' (')[-1][:-1]
            pos2ElCountShelf[repr(i+1)] = elCount
        
        pos2ElCountShelf.close()
    
def parseMatrixTextFileToShelf(txtFn, outShelfFn, rowPos2NameShelfFn=None, colPos2NameShelfFn=None, \
                               rowPos2ElCountShelfFn=None, colPos2ElCountShelfFn=None, keyType='names', countType='count'):
    "txtFn outShelfFn rowPos2NameShelfFn=None colPos2NameShelfFn=None rowPos2ElCountShelfFn=None colPos2ElCountShelfFn=None, keyType=names countType=count"
    assert keyType in ['names', 'pos']
    assert countType in ['count','log','binary']

    map = {}
    firstRealLine = True
    
    rowNames = []
    for line in open(txtFn):
        print '.',
        line = line.strip()
        if len(line)==0 or line[0] == '#':
            continue
        
        if firstRealLine:
            colNames = line.split('\t')
            firstRealLine = False
            continue
        
        cols = line.split('\t')
        rowName = cols[0]
        rowNames.append(rowName)
        tableVals = cols[1:]
        assert len(tableVals) == len(colNames), \
            'len(tableVals) != len(colNames) (%i != %i)' % (len(tableVals), len(colNames))
        for i in range(len(tableVals)):
            try:
                curVal = tableVals[i].replace(' ','')
                val = int(curVal)
            except:
                try:
                    val = float(curVal)
                except:
                    val = ast.literal_eval(curVal)
            if countType=='binary':
                val = 1 if val>0 else 0
            elif countType=='log':
                val = int( math.ceil( math.log(val+1,2) ) )
            if keyType == 'names':
                map[repr((rowName.lower(), colNames[i].lower()))] = val
            elif keyType == 'pos':
                map[repr((len(rowNames), i+1))] = val
    
    shelf = safeshelve.open(outShelfFn)
    shelf.update(map)
    shelf.close()
    
    _createPos2NameShelf(rowPos2NameShelfFn, rowNames)
    _createPos2NameShelf(colPos2NameShelfFn, colNames)
    
    _createPos2ElCountShelf(rowPos2ElCountShelfFn, rowNames)
    _createPos2ElCountShelf(colPos2ElCountShelfFn, colNames)
        
def parseMatrixTextFileTo1dShelf(txtFn, outShelfFn, rowOrCol='row', ignoreFirstColName='False'):
    "txtFn outShelfFn rowOrCol='row' ignoreFirstColName='False'"

    assert rowOrCol in ['row','col']
    assert ignoreFirstColName in ['False', 'True']

    ignoreFirstColName = ast.literal_eval(ignoreFirstColName)
    map = {}
    firstRealLine = True
    
    rowNames = []
    for line in open(txtFn):
        print '.',
        line = line.strip()
        if len(line)==0 or line[0] == '#':
            continue
        
        if firstRealLine:
            colNames = line.split('\t')
            if ignoreFirstColName:
                colNames = colNames[1:]
            firstRealLine = False
            continue
        
        cols = line.split('\t')
        rowName = cols[0]
        rowNames.append(rowName)
        tableVals = cols[1:]
        assert len(tableVals) == len(colNames), \
            'len(tableVals) != len(colNames) (%i != %i)' % (len(tableVals), len(colNames))
        for i in range(len(tableVals)):
            if tableVals[i] == 'None':
                continue
            try:
                val = int(tableVals[i])
            except:
                val = float(tableVals[i])
            key = rowName if rowOrCol == 'row' else colNames[i]
            if key not in map:
                map[key] = [val]
            else:
                map[key].append(val)
            
    shelf = safeshelve.open(outShelfFn)
    shelf.update(map)
    shelf.close()
            
def makeLowercaseName2NameShelfFromTnSubTypes(genome, trackName, shelfFn):
    'genome trackName shelfFn'
    trackName = re.split('/|:',trackName)
    
    from gold.application.GalaxyInterface import GalaxyInterface
    analysisDef = "-> ListOfPresentCategoriesStat"
    results = GalaxyInterface.runManual([trackName, None], analysisDef, '*', '*', genome, 
                                        printResults=False, printHtmlWarningMsgs=False)
    categories = results.getGlobalResult()['Result']
    
    shelf = safeshelve.open(shelfFn)
    for cat in categories:
        shelf[cat.lower()] = cat
    
    ##basePath = createDirPath(trackName, genome)
    #basePath = gcf.createOrigPath(genome, trackName)
    #shelf = safeshelve.open(shelfFn)
    #
    #for fn in os.listdir(basePath):
    #    if os.path.isdir(os.sep.join([basePath, fn])) and not any([fn.startswith(x) for x in ['_','.'] + GenomeInfo.getExtendedChrList(genome)]):
    #        shelf[fn.lower()] = fn
    shelf.close()
        
def makeShelfKeysLowercase(shelfFn, newShelfFn):
    'shelfFn newShelfFn'
    origShelf = safeshelve.open(shelfFn, 'r')
    newShelf = safeshelve.open(newShelfFn, 'c')
    
    for key in origShelf.keys():
#        print key
        if key.lower() in newShelf:
            print '%s: Duplicate: %s and %s. Using the longest.' % (key.lower(), origShelf[key], newShelf[key.lower()])
            newShelf[key.lower()] = (origShelf[key] if len(origShelf[key]) > len(newShelf[key.lower()]) else newShelf[key.lower()])
        else:
            newShelf[key.lower()] = origShelf[key]
    newShelf.close()
    origShelf.close()

def _createTfAndDisease2RankedGeneListMapping(disease2geneShelfFn, geneAndTf2TfbsCountShelfFn, rankedGeneListShelfFn):
    'disease2geneShelfFn geneAndTf2TfbsCountShelfFn geneListShelfFn'
    disease2geneShelf = safeshelve.open(disease2geneShelfFn,'r')
    geneAndTf2TfbsCountShelf = safeshelve.open(geneAndTf2TfbsCountShelfFn,'r')
    rankedGeneListShelf = safeshelve.open(rankedGeneListShelfFn, 'c')
    
    allDiseases = disease2geneShelf.keys()
    
    allTfs = set([])
    for key in geneAndTf2TfbsCountShelf:
        allTfs.add(ast.literal_eval(key)[0])

    for tf in allTfs:
        for disease in allDiseases:
            geneList = disease2geneShelf[disease]
            countList = [geneAndTf2TfbsCountShelf.get(repr((tf, x.lower()))) for x in geneList]
            countList = [(x if x is not None else 0) for x in countList]
            sumCounts = sum(countList)
            propList = [1.0*x/sumCounts if sumCounts != 0 else 0 for x in countList]
            rankedGeneListShelf[repr((tf, disease))] = zip(geneList, countList, propList)
    
    disease2geneShelf.close()
    geneAndTf2TfbsCountShelf.close()
    rankedGeneListShelf.close()

def createShelvesBehindRankedGeneLists(galaxyId, mapId, countType):
    'galaxyId mapId countType'
    batchid='0'
    
    resultsBaseDirStatic = '/work/hyperbrowser/results/developer/static'
    homeDirOnInsilico = '/xanadu/home/sveinugu'
    colldir = ('%.3f' % (int(galaxyId)/1000 *1.0 / 1000))[2:]
    #hent txt
    
    from quick.util.CommonFunctions import getGalaxyFnFromDatasetId
    from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
    galaxyFn = getGalaxyFnFromDatasetId(id)
    resultsStaticDir = GalaxyRunSpecificFile([batchid], galaxyFn).getDiskPath()
    #legg shelf
    googleMapsCommonDir = '/'.join([STATIC_PATH, 'maps', 'common',str(mapId)])
    
    disease2geneShelfFn = googleMapsCommonDir+os.sep + 'col2GeneList.shelf'
    geneAndTf2TfbsCountShelfFn = googleMapsCommonDir+os.sep + 'rowAndGene2count.shelf'
    rankedGeneListShelfFn = googleMapsCommonDir+os.sep + 'rowAndCol2rankedGeneList.shelf'
    resultTableTxtFn = resultsStaticDir+'/Result_table.txt'
    
    assert os.path.exists(resultTableTxtFn), 'Did not find Galaxy results file: ' + resultTableTxtFn    
    assert os.path.exists(disease2geneShelfFn), 'Did not find col2GeneList shelf: ' + disease2geneShelfFn
    
    parseMatrixTextFileToShelf(resultTableTxtFn, geneAndTf2TfbsCountShelfFn, countType=countType)
    #geneAndTf2tfbsCount = safeshelve.open(geneAndTf2TfbsCountShelfFn,'r')
    _createTfAndDisease2RankedGeneListMapping(disease2geneShelfFn, geneAndTf2TfbsCountShelfFn, rankedGeneListShelfFn) 
    
def printHistOfIntegerShelfValues(shelfFn):
    'shelfFn'
    shelf = safeshelve.open(shelfFn,'r')
    hist = {}
    for val in shelf.values():
        assert type(val)==int
        if not val in hist:
            hist[val] = 0
        hist[val]+=1
    assert len(hist)<1000, 'Hist considered too large to simply print to screen..'
    print 'Hist line-based:'
    for key in hist:
        print key,': ',hist[key]
    print 'Comma-separated keys and values:'
    print ','.join([str(x) for x in hist.keys()])
    print ','.join([str(x) for x in hist.values()])
    
def mergeShelvesTransitively(inShelf1Fn, inShelf2Fn, outShelfFn, includeSecondShelf='True'):
    """inShelf1Fn inShelf2Fn outShelfFn
    The values of the first shelf can be a list.
    """

    if isinstance(includeSecondShelf, basestring):
        includeSecondShelf = ast.literal_eval(includeSecondShelf)
    assert includeSecondShelf in [True, False]

    inShelf1 = safeshelve.open(inShelf1Fn,'r')
    inShelf2 = safeshelve.open(inShelf2Fn,'r')
    outShelf = safeshelve.open(outShelfFn,'c')

    if includeSecondShelf:
        for key,val in inShelf2.items():
            outShelf[key] = val
    
    for key,vals in inShelf1.items():
        if type(vals) != list:
            vals = [vals]

        transVals = []
        for val in vals:
            try:
                if val not in inShelf2:
                    val = val.replace('_', ' ')
                    if val not in inShelf2:
                        raise
                transVals += (inShelf2[val])
            except:
                print 'Unmatched value in %s: %s' % (inShelf2Fn, val)
        
        if len(transVals) > 0:
            outShelf[key] = transVals

    inShelf1.close()
    inShelf2.close()
    outShelf.close()
    
def reverseMappingHavingListValues(inShelfFn, outShelfFn):
    """inShelfFn, outShelfFn
    reverse a mapping that (in input) goes from a key to a list of values, that is key->val1,val2...valN
    end up with a reversed mapping from key (valK from any value list) to list of values (keys having this in its value list)
    """
    inShelf = safeshelve.open(inShelfFn,'r')
    revMap = {}
    for key in inShelf:
        el = inShelf[key]
        if type(el) != list:
            el = [el]
            
        for val in el:
            if not val in revMap:
                revMap[val] = []
            revMap[val].append(key)
    #print revMap.items()[0:3]
    shelf = safeshelve.open(outShelfFn)
    shelf.update(revMap)
    shelf.close()
    inShelf.close()
    
def getLengthOfValueListDistribution(shelfFn):
    shelf = safeshelve.open(shelfFn,'r')
    distribution = [len(valList) for valList in shelf.values()]
    print ','.join([str(x) for x in distribution])

def createSubtypeDirsFromFileList(inDir, outBaseDir, suffix='.bed'):
    """inDir outBaseDir suffix='.bed'"""
    files = [x for x in os.listdir(inDir) if x.endswith(suffix)]
    for f in files:
        outDir = os.path.sep.join([outBaseDir, f[0:-len(suffix)]]) 
        print 'Creating directory :' + outDir
        outFn = os.path.sep.join([outDir, f])
        qcf.ensurePathExists(outFn)
        shutil.copy(os.path.sep.join([inDir, f]), outFn)

#def subtypesAsCategories(genome, trackName, keepVal=False):
#    """genome trackName keepVal=False"""
#    trackName = re.split('/|:',trackName)
#    basePath = gcf.createOrigPath(genome, trackName)
#    outF = open(basePath+os.sep+'combined.category.bed','w')
#    for subType in os.listdir(basePath):
#        subPath = basePath + os.sep + subType
#        if not os.path.isdir(subPath):
#            continue
#        
#        fnPaths = [subPath+os.sep+x for x in os.listdir(subPath)]
#        onlyFiles = [x for x in fnPaths if os.path.isfile(x) and x.endswith('.bed')]
#        assert len(onlyFiles)==1, str(onlyFiles)
#        fn = onlyFiles[0]
#        
#        for line in open(fn):
#            cols = line.split()
#            if len(cols)==3:
#                outF.write(line.replace(os.linesep,'') + '\t' + subType + os.linesep )
#            elif len(cols)>3:
#                cols[3] = subType.replace(' ','_')
#                outF.write('\t'.join(cols) + os.linesep)
#            else:
#                raise InvalidFormatError('Line does not have enough columns: %s' %line)
#    outF.close()

def mergeSubtypeTracksToNewCategoryTrack(genome, trackName, newTrackName=None):
    """genome trackName newTrackName"""
    'Used to create a union of the subtype tracks, with the category column (4) used as key. If the same key has different'
    'locations, the first location is used, and the others are printed to standard out. Has been used to create a merged'
    'gene track with all genes from a set of subtypes.'
    'To create a standard categorical track based on subtypes, see instead SubtypesAsCategories in StandardizeTrackFiles'

    trackName = re.split('/|:',trackName)
    newTrackName = re.split('/|:',newTrackName)
    
    basePath = gcf.createOrigPath(genome, trackName)
    newFn = gcf.createOrigPath(genome, newTrackName) + os.sep + 'merged.category.bed'

    categoryDict = {}
    qcf.ensurePathExists(newFn)
    outF = open(newFn,'w')
    for subType in os.listdir(basePath):
        subPath = basePath + os.sep + subType
        if not os.path.isdir(subPath):
            continue
        
        fnPaths = [subPath+os.sep+x for x in os.listdir(subPath)]
        onlyFiles = [x for x in fnPaths if os.path.isfile(x) and x.endswith('.bed')]
#        assert len(onlyFiles)==1, str(onlyFiles)
        for fn in onlyFiles:
            for line in open(fn):
                cols = line.strip().split()
                assert len(cols) > 3
                
                cat = cols[3]
                if cat in categoryDict:
                
                    if categoryDict[cat] != [cols[x] for x in [0,1,2,5]]:
                        print cat + ': ' + str(categoryDict[cat]) + ' != ' + str([cols[x] for x in [0,1,2,5]])
                else:
                    categoryDict[cat] = [cols[x] for x in [0,1,2,5]]
                    outF.write('\t'.join([cols[x] for x in [0,1,2,3]] + ['0'] + [cols[5]]) + os.linesep)
    outF.close()

def showCodeSize():
    fileCount = 0
    lineCount = 0
    codeLineCount = 0
    
    for root, dirs, files in os.walk('.'):
        print root
        for fn in files:
            if fn.endswith('.py'):
                fileCount += 1
                lineCount += len( open(root+os.sep+fn).readlines() )
                codeLineCount  += len([line for line in open(root+os.sep+fn) if line.strip()!='' and line.strip()[0]!='#'] )
    
    print '#files: ',fileCount
    print '#lines: ',lineCount
    print '#code lines: ',codeLineCount
    
def _countAnalyses(analyses, includeExperimental):
    analyses = [a for a in analyses if len(a._analysisParts) > 0]
    if not includeExperimental:
        analyses = [a for a in analyses if not \
                    ('isExperimental' in a.getAllOptionsAsKeys() and 'True' in a.getAllOptionsAsKeys()['isExperimental'])]
    print 'Number of analyses ignoring assumptions' + \
          (' (including experimental analyses)' if includeExperimental else '') + \
          ': ', len(analyses)
    print 'Number of analyses distinguishing assumptions' + \
          (' (including experimental analyses)' if includeExperimental else '') + \
          ': ', sum( (len(a.getOptionsAsKeys()[a.ASSUMP_LABEL_KEY]) if a.ASSUMP_LABEL_KEY in a.getOptionsAsKeys() else 1) for a in analyses)

def countAnalyses():
    "Counts analyses"
    analyses = AnalysisManager.getAllAnalyses()
    print 'Total counts: '
    _countAnalyses(analyses, True)
    _countAnalyses(analyses, False)
    
    allAnalyses = AnalysisManager.getAnalysisDict()
    mainCats = ['Hypothesis testing','Descriptive statistics']
    for mainCat in mainCats:
        analyses = reduce( lambda x,y:x+y, [allAnalyses[cat].values() for cat in allAnalyses.keys() if cat.startswith(mainCat)] )
        print 'Considering the main-category: ', mainCat
        _countAnalyses(analyses, True)
        _countAnalyses(analyses, False)
            
    for cat in allAnalyses.keys():
        analyses = allAnalyses[cat].values() 
        print 'Considering the category: ', cat
        _countAnalyses(analyses, True)
        _countAnalyses(analyses, False)

def allBatchTrackNames(genome='hg18'):
    """[genome]"""
#instead use OrigTrackFnSource
    for tn in OrigTrackNameSource(genome,[]):
        print ':'.join(tn).replace(' ','_')
        
def createMappingFromColsOfTabSpacedFile(inFn, outShelfFn, fromCol, toCol):
    'inFn outShelfFn fromCol toCol'
    map = {}
    for line in open(inFn):
        if len(line.strip()) == 0:
            continue
        cols = line.strip().split()
        key = cols[int(fromCol)]
        if not key in map:
            map[key] = set([])
        map[key].add(cols[int(toCol)])
    for key in map:
        map[key] = list(map[key])
    shelf = safeshelve.open(outShelfFn)
    shelf.update(map)
    shelf.close()
        
        
def fixTrackInfo(trackName, genome='hg18'):
    """trackName [genome]"""
    "fix timeOfPreProcessing of TrackInfo for a given trackName, in order for it to become a valid selection.."
    trackName = trackName.split(':')
    ti = TrackInfo(genome, trackName)
    ti.timeOfPreProcessing = 'manualOverride'
    ti.store()

def makeInitFromParamList(paramStr):
    """paramStr"""
    paramList = paramStr.replace(' ','').split(',')
    print '    def __init__(self, ' + ', '.join(paramList) + '):'
    for param in paramList:
        param = param.replace('*','')
        print '        self._' + param + ' = ' + param

def createChromosomeFile(genome, chromNames, referToCollected=False):
    """genome chromNames"""
    # python quick/extra/CustomFuncCatalog.py CreateChromosomeFile mm9 'chr1, chr2, ...'"
    
    chrList = chromNames.replace(' ','').split(',')
    if referToCollected:
        from gold.util.CommonFunctions import createCollectedPath
        basePath = createCollectedPath(genome, GenomeInfo.getPropertyTrackName(genome, 'chrs'))
    else:
        basePath = gcf.createOrigPath(genome, GenomeInfo.getPropertyTrackName(genome, 'chrs'))

    outFn = basePath + os.sep + 'chromosomes.category.bed'
    qcf.ensurePathExists(outFn)
    print 'Creating: ' + outFn

    outFile = open(outFn, 'w')
    for chr in chrList:
        outFile.write('\t'.join([chr, '0', str(GenomeInfo.getChrLen(genome,chr)), chr]) + os.linesep)
    outFile.close()

def createSplittedChrArms(genome, binSize, outFn):
    """genome binsize outFn.bed"""
    outFile = open(outFn, 'w')
    
    from quick.application.GalaxyInterface import GalaxyInterface
    chrArms = GalaxyInterface._getUserBinSource('__chrArms__', '*', genome)
    chrArmBins = AutoBinner(chrArms, int(binSize))
    for bin in chrArmBins:
        outFile.write('\t'.join([bin.chr, str(bin.start), str(bin.end)]) + os.linesep)
    outFile.close()
    
def createAssemblyGapsFile(genome, assemblyChars='ACGTacgt'):
    """genome assemblyChars='ACGTacgt'"""
    basePath = gcf.createOrigPath(genome, GenomeInfo.getPropertyTrackName(genome, 'gaps'),'')
    outFn = basePath + 'assemblyGaps.bed'
    qcf.ensurePathExists(outFn)
    outFile = open(outFn,'w')
    
    seqTrack = PlainTrack( GenomeInfo.getSequenceTrackName(genome) )

    anyGaps = False
    for chr in GenomeInfo.getExtendedChrList(genome):
        chrRegion = GenomeRegion(genome, chr, 0, GenomeInfo.getChrLen(genome, chr))
        seqTV = seqTrack.getTrackView(chrRegion)
        seq = seqTV.valsAsNumpyArray()
        
        #gapIndexes = numpy.arange(len(seq))[(seq == 'n') | (seq == 'N')]
        gapIndexes = numpy.arange(len(seq))[numpy.logical_not( numpy.logical_or.reduce([seq == x for x in assemblyChars]) )]
        gapIndexDiff = gapIndexes[1:] - gapIndexes[:-1]
        gapBeginIndexes = numpy.delete(gapIndexes, (numpy.arange(len(gapIndexDiff)) + 1)[gapIndexDiff==1])
        gapEndIndexes = numpy.delete(gapIndexes + 1, numpy.arange(len(gapIndexDiff))[gapIndexDiff==1])
        
        assert len(gapBeginIndexes) == len(gapEndIndexes)
        
        for i in xrange(len(gapBeginIndexes)):
            anyGaps = True
            outFile.write('\t'.join([chr, str(gapBeginIndexes[i]), str(gapEndIndexes[i])]) + os.linesep)
        
    if not anyGaps:
        outFile.write('\t'.join([GenomeInfo.getExtendedChrList(genome)[0], '1', '1']))
        
    outFile.close()


def CreateChromosomeArmsFiles(genome):
    pass
    #chromArmsFn = gcf.createOrigPath(genome, GenomeInfo.getPropertyTrackName(genome, 'chrarms'),'chromosomeArms.category.bed')
    #
    #qcf.ensurePathExists(gapsFn)
    #qcf.ensurePathExists(chromArmsFn)
    #
    #inFile = open(inFn)
    #inFile.readline()
    #
    #outFileGaps = open(gapsFn, 'w')
    #outFileArms = open(chromArmsFn, 'w')
    #
    #centromere_starts = {}
    #centromere_ends = {}
    #
    #for line in inFile:
    #    cols = line.strip().split()
    #    outFileGaps.write('\t'.join(cols[i] for i in [1,2,3,7]) + os.linesep)
    #    
    #    chr = cols[1]
    #    if not chr in centromere_starts:
    #        centromere_starts[chr] = []
    #        centromere_ends[chr] = []
    #        
    #    if any(x in cols[7].lower() for x in ['centromere', 'heterochromatin', 'arms']):
    #        centromere_starts[chr].append(int(cols[2]))
    #        centromere_ends[chr].append(int(cols[3]))
    #
    #for chr in GenomeInfo.getChrList(genome):
    #    chrLen = GenomeInfo.getChrLen(genome, chr)
    #    if len(centromere_starts[chr]) == 0:
    #        outFileArms.write('\t'.join([chr, str(0), str(chrLen), chr]) + os.linesep)
    #    else:
    #        centromerStart = sorted(centromere_starts[chr])[0]
    #        centromerEnd = list(reversed(sorted(centromere_ends[chr])))[0]
    #        
    #        if 0 < centromerStart:
    #            outFileArms.write('\t'.join([chr, str(0), str(centromerStart), chr + 'p']) + os.linesep)
    #        if centromerEnd < chrLen:
    #            outFileArms.write('\t'.join([chr, str(centromerEnd), str(chrLen), chr + 'q']) + os.linesep)
    #
    #outFileGaps.close()
    #outFileArms.close()
    #inFile.close()

def gwPlotting(inFn, outFn):
    """inFn.bed outFn.pdf"""
    outDir = os.path.split(outFn)[0]
    
    PLOT_BED_FN = os.sep.join([HB_SOURCE_CODE_BASE_DIR, 'rCode', 'plotBed.r'])
    PLOT_CHR_FN = os.sep.join([HB_SOURCE_CODE_BASE_DIR, 'rCode', 'ChromosomePlot.r'])
    PLOT_GW_FN = os.sep.join([HB_SOURCE_CODE_BASE_DIR, 'rCode', 'GenomePlot.r'])
    CYTOBANDS_FN = os.sep.join([HB_SOURCE_CODE_BASE_DIR, 'data', 'cytoband_mm8.txt'])
    from proto.RSetup import r
    r('source("%s")' % PLOT_BED_FN)
    #r('source("%s")' % PLOT_CHR_FN)
    r('source("%s")' % PLOT_GW_FN)
    r('cytoband = read.table("%s", header=TRUE)' % CYTOBANDS_FN)
    r('loadedBedData <- plot.bed("%s")' % inFn)
    #r('plot.chrom(segments=loadedBedData, unit="bp", dir.print="%s", plot.ideo=TRUE,cytoband=cytoband)' % outDir)
    r('plot.genome(segments=loadedBedData, unit="bp", dir.print="%s")' % outDir)
    shutil.move(outDir+ os.sep + '.pdf', outFn)

def copyAndFilterSubtypes(genome, trackName, newTrackName, filterFn):
    """genome trackName newTrackName filterFn"""
    trackName, newTrackName  = [re.split('/|:',tn) for tn in [trackName, newTrackName]]
    origPath, newPath = [gcf.createOrigPath(genome, tn,'') for tn in [trackName, newTrackName]]

    filterFile = open(filterFn, 'r')
    filterList = []
    for line in filterFile:
        filterList.append(line.strip().replace('_',' '))
    filterSet = set(filterList)
    filterFile.close()
    
    for subType in os.listdir(origPath):
        if subType.replace('_',' ') in filterSet:
            print 'copying %s' % subType
            shutil.copytree(origPath + subType, newPath + subType, symlinks=True)

def createMappingsFromMeshAsciiFile(asciiFn, mapHeadingToIdFn, mapIdToHeadingFn):
    """asciiFn mapHeadingToIdFn mapIdToHeadingFn"""
    mapHeadingToIdFile = safeshelve.open(mapHeadingToIdFn)
    mapIdToHeadingFile = safeshelve.open(mapIdToHeadingFn)

    curHeading = ''
    curId = None

    for line in open(asciiFn, 'r'):
        line = line.strip()
        if line=='*NEWRECORD':
            if curHeading != '' and curId != '':
                mapHeadingToIdFile[curHeading] = curId
                mapIdToHeadingFile[curId] = curHeading
            curHeading = ''
            curId = None
        if line.startswith('MH = '):
            curHeading = line[5:]
        if line.startswith('UI = '):
            curId = line[5:]

    mapHeadingToIdFile.close()
    mapIdToHeadingFile.close()

def createMeshHierarchyMappings(hierarchyIdFile, mapIdToHeadingFn, mapParentToChildrenFn, mapChildToParentsFn):
    """hierarchyIdFile mapIdToHeadingFn mapParentToChildrenFn mapChildToParentsFn"""
    mapParentToChildrenFile = safeshelve.open(mapParentToChildrenFn)
    mapChildToParentsFile = safeshelve.open(mapChildToParentsFn)
    mapIdToHeadingFile = safeshelve.open(mapIdToHeadingFn, 'r')

    for line in open(hierarchyIdFile, 'r'):
        cols = line.strip().split()
        try:
            parent, child = [mapIdToHeadingFile[cols[x]] for x in [0,2]]
        except KeyError, e:
            print e
            continue

        if parent == child:
            continue

        if not parent in mapParentToChildrenFile:
            mapParentToChildrenFile[parent] = [child]
        else:
            temp = mapParentToChildrenFile[parent]
            temp.append(child)
            mapParentToChildrenFile[parent] = [x for x in sorted(set(temp))]

        if not child in mapChildToParentsFile:
            mapChildToParentsFile[child] = [parent]
        else:
            temp = mapChildToParentsFile[child]
            temp.append(parent)
            mapChildToParentsFile[child] = [x for x in sorted(set(temp))]

    mapParentToChildrenFile.close()
    mapChildToParentsFile.close()

def createAllNodesAndLeaves(mapFn, fullMapFn):
    """mapFn fullMapFn"""
    mapFile = safeshelve.open(mapFn, 'r')
    fullMapFile = safeshelve.open(fullMapFn)

    def _getAllChildren(mapFile, curChild, parents):
        if curChild not in mapFile:
            return []
        
        allChildren = [x for x in mapFile[curChild] if x not in parents]
        for child in copy.copy(allChildren):
            allChildren += _getAllChildren(mapFile, child, parents + [curChild])

        return allChildren

    for entry in mapFile:
        fullMapFile[entry] = [x for x in sorted(set(_getAllChildren(mapFile, entry, [])))]

    mapFile.close()
    fullMapFile.close()

def copyStandardTrack(genome, oldTn, newTn):
    """genome oldTn newTn"""
    oldTn = re.split('/|:', oldTn)
    newTn = re.split('/|:', newTn)
    oldPath = gcf.createOrigPath(genome, oldTn)
    assert os.path.exists(oldPath), 'ERROR: TN did not exist in stdTracks: ' + oldPath
    
    print '(copying track in stdTracks..)'
    newPath = gcf.createOrigPath(genome, newTn)
    assert not os.path.exists(newPath), 'ERROR: Target path already exists: ' + newPath
    qcf.ensurePathExists(newPath)
    shutil.copytree(oldPath, newPath)
    
def findArticleCountOfAllSubtypes(genome, trackName, outFn):
    'genome trackName outFn'
    trackName = trackName.split(':')
    basePath = os.sep.join([NONSTANDARD_DATA_PATH, genome] + trackName)
    subnames = []
    articleCounts = []
    i = 0
    for sub in os.listdir(basePath):
        fullPath = basePath + os.sep + sub
        if os.path.isdir(fullPath):
            contents = os.listdir(fullPath)
            if len(contents) == 1:
                inFn = fullPath + os.sep + contents[0]
                inFile = open(inFn, 'r')
                firstLineCols = inFile.readline().strip().split()
                if len(firstLineCols) > 0:
                    assert len(firstLineCols) == 9, firstLineCols
                    subnames.append(sub.replace(' ','_'))
                    articleCounts.append(firstLineCols[8])
                inFile.close()
                i += 1
                if i == 100:
                    print '.'
                    i = 0
                
    outFile = open(outFn, 'w')
    outFile.write('\t'.join(subnames) + os.linesep)
    outFile.write('\t'.join(articleCounts) + os.linesep)
    outFile.close()

def compareRegulomeWithDirectPubmedTfData(pValThresholdReg, pValThresholdTf, useRowCount):
    "pValThresholdReg pValThresholdTf useRowCount"
    pValThresholdReg = float(pValThresholdReg)
    pValThresholdTf = float(pValThresholdTf)
    assert useRowCount in ['True', 'False']
    
    rowCountRegFn = STATIC_PATH + "/maps/final_tfbs_diseases_binary_average_euc_0.01_rowcount/data/Result_pval_table.txt"
    rowSumRegFn = STATIC_PATH + "/maps/final_tfbs_diseases_binary_average_euc_0.01_rowsum/data/Result_pval_table.txt"

    regFn = rowCountRegFn if ast.literal_eval(useRowCount) else rowSumRegFn

    tfDir = gcf.createOrigPath('hg18', ['Private', 'disease' 'all diseases, hyperg., only TFs'])
    v2tfFn = '/projects/rrresearch/eivindto/v2tf-sort-ok.txt'

    regFile = open(regFn)

    for i in xrange(4):
        regFile.readline()

    tfDiseases = dict([(x.lower(), x) for x in os.listdir(tfDir)])
    regDiseases = [' '.join(x.split()[1:-1]).lower() for x in regFile.readline().strip().split('\t')]

    combDiseases = [tfDiseases[x] for x in regDiseases if x in tfDiseases]
    disease2index = dict([(x,i) for i,x in enumerate(combDiseases)])
    index2disease = dict([(i,x) for i,x in enumerate(combDiseases)])

    v2tf = dict([line.strip().split() for line in open(v2tfFn)])
    tf2v = dict([reversed(line.strip().split()) for line in open(v2tfFn)])
    tf2index = dict([(x,i) for i,x in enumerate(sorted(v2tf.values()))])
    index2tf = dict([(i,x) for i,x in enumerate(sorted(v2tf.values()))])
    
    regTable = numpy.zeros(shape=[len(v2tf), len(combDiseases)], dtype='bool')
    tfTable = numpy.zeros(shape=[len(v2tf), len(combDiseases)], dtype='bool')

    for line in regFile:
        line = line.strip()
        if line == '' or line[0] == '#':
            continue

        cols = line.split('\t')
        pwm = ' '.join(cols[0].split()[1:-1]).lower()
        if pwm not in v2tf:
            continue

        tfIndex = tf2index[v2tf[pwm]]
        for disIndex,x in enumerate(cols[1:]):
            if float(x) < pValThresholdReg:
                regTable[tfIndex][disIndex] = True

    for dis in combDiseases:
        tfFile = open(os.sep.join([tfDir, dis, dis + '.category.bed']))
        for line in tfFile:
            cols = line.strip().split()
            if math.exp(float(cols[4])) < pValThresholdTf:
                if cols[3] in tf2index:
                    tfTable[ tf2index[cols[3]] ][ disease2index[dis] ] = True

    tfIndexes, disIndexes = numpy.where(regTable&tfTable)

    print 'All hits in both:'
    for i in xrange(len(tfIndexes)):
        print index2disease[disIndexes[i]] + '\t' + tf2v[index2tf[tfIndexes[i]]] + '\t' + index2tf[tfIndexes[i]]

    print '#Diseases: %d' % len(combDiseases)
    print '#TFs: %d' % len(v2tf)
    print '#Hits in both: %d' % (regTable&tfTable).sum()
    print '#Hits in both (expected): %f' % ((regTable&~tfTable).sum()*1.0*(~regTable&tfTable).sum()/(~regTable&~tfTable).sum())
    print '#Hits in regulome only: %d' % (regTable&~tfTable).sum()
    print '#Hits in TF & Pubgene only: %d' % (~regTable&tfTable).sum()
    print '#Hits in none: %d' % (~regTable&~tfTable).sum()

def RemoveDirectoriesWithOneEmptyFileRecursively(baseDir):
    'baseDir'
    for path, dirs, files in os.walk(baseDir):
#        print path, dirs, files
        if len(dirs) == 0 and len(files) == 1:
            if os.path.getsize(os.sep.join([path, files[0]])) == 0:
                print 'Removing directory %s' % path
                shutil.rmtree(path)

def mergeTrackInfoShelves(otherTrackInfoShelveFn):
    mainShelve = safeshelve.open(TrackInfo.SHELVE_FN, 'r')
    otherShelve = safeshelve.open(otherTrackInfoShelveFn, 'r')
    
    mergeKeys = [key for key in otherShelve if key not in mainShelve]
    
    for key in mergeKeys:
        ti = otherShelve[key]
        ti.store()
                
def _usage():
    print 'syntax: '
    print 'to use: [name] [args]'
    print 'available commands: '
    print ', '.join(funcList.keys())
    sys.exit(0)                

if __name__ == "__main__":
    from gold.application.HyperBrowserCLI import *

    from collections import OrderedDict
    import types
    import sys
    thisModule = sys.modules[__name__]
    print 'STARTING'
    funcList = OrderedDict((a, thisModule.__dict__.get(a)) for a in sorted(dir(thisModule))
                    if isinstance(thisModule.__dict__.get(a), types.FunctionType) and a[0] != '_')


    #'subtypesAsCategories'
    #funcList = ['allBatchTrackNames','preDiseaseStepwise','fixTrackInfo','showCodeSize','countAnalyses',\
    #            'makeInitFromParamList','createCategoryBedFileFromUCSCRepeats','createChromosomeFile','createSplittedChrArms', \
    #            'createAssemblyGapsFile', 'gwPlotting', 'copyAndFilterSubtypes', \
    #            'createSubtypeDirsFromFileList', 'createMappingsFromMeshAsciiFile', 'createMeshHierarchyMappings', \
    #            'createAllNodesAndLeaves','getCategorySetForSubTracks','parseMatrixTextFileToShelf', 'parseMatrixTextFileTo1dShelf', \
    #            'makeLowercaseName2NameShelfFromTnSubTypes', 'mergeShelvesTransitively', 'reverseMappingHavingListValues', \
    #            'getLengthOfValueListDistribution', 'mergeSubtypeTracksToNewCategoryTrack', \
    #            'makeShelfKeysLowercase', '_createTfAndDisease2RankedGeneListMapping', \
    #            'createMappingFromColsOfTabSpacedFile','printHistOfIntegerShelfValues', 'copyStandardTrack','createShelvesBehindRankedGeneLists', \
    #            'findArticleCountOfAllSubtypes', 'compareRegulomeWithDirectPubmedTfData', 'RemoveDirectoriesWithOneEmptyFileRecursively', \
    #            'mergeTrackInfoShelves']

    if len(sys.argv) == 1:
        _usage()
    else:
        assert( len(sys.argv) >= 2)
        if not sys.argv[1] in funcList:
            _usage()
        else:
            try:
                func = funcList[sys.argv[1]]
                func(*sys.argv[2:])
            except:
                print
                print 'usage: python CustomFuncCatalog.py ' + str(func.__name__) + ' ' + str(func.__doc__)
                print
                raise

