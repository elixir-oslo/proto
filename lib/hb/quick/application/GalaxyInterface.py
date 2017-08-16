import ast
import os
import os.path
import re
import shutil
import sys
import time
from copy import copy
from datetime import datetime
from urllib import unquote, quote

from config.Config import DebugConfig, DEFAULT_GENOME, STATIC_REL_PATH,\
    IS_EXPERIMENTAL_INSTALLATION, ORIG_DATA_PATH, HB_VERSION, DATA_FILES_PATH, USE_PARALLEL, \
    URL_PREFIX
from gold.util.CommonConstants import BATCH_COL_SEPARATOR
from gold.application.LogSetup import logging, HB_LOGGER, usageAndErrorLogging, \
    runtimeLogging, logException, detailedJobRunHandler, logMessage, logLackOfSupport
from gold.application.StatRunner import AnalysisDefJob, AssemblyGapJob #, CountBothTracksJob
from gold.description.AnalysisDefHandler import AnalysisDefHandler
from gold.description.TrackInfo import TrackInfo
from gold.extra.nmers.NmerManager import NmerManager
from gold.origdata.PreProcessTracksJob import PreProcessAllTracksJob
from gold.track.Track import PlainTrack
from gold.util.CommonFunctions import smartStrLower,\
    getClassName, prettyPrintTrackName, createOrigPath, \
    getOrigFn, strWithStdFormatting
from gold.util.CustomExceptions import NotSupportedError, \
    Warning, InvalidFormatError, InvalidRunSpecException, \
    ShouldNotOccurError  #, IncompatibleTracksError
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile, StaticFile
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.ProcTrackOptions import ProcTrackOptions
from quick.application.SignatureDevianceLogging import takes,returns
from quick.application.UserBinSource import GlobalBinSource
from quick.extra.CustomTrackCreator import TrackViewBasedCustomTrackCreator
from quick.extra.FunctionCategorizer import FunctionCategorizer
from quick.extra.OrigFormatConverter import OrigFormatConverter
from quick.extra.StandardizeTrackFiles import runParserClass
from quick.extra.TrackExtractor import TrackExtractor
from quick.util.CommonFunctions import extractIdFromGalaxyFn, ensurePathExists
from proto.ProtoToolRegister import getToolPrototype
from quick.util.GenomeInfo import GenomeInfo
from third_party.asteval_raise_errors import Interpreter


#from quick.batch.BatchRunner import BatchRunner,SuperBatchRunner
#from quick.webtools.GeneralGuiToolsFactory import GeneralGuiToolsFactory

class GalaxyInterfaceVis:
    @staticmethod
    def runVisualization(regSpec, galaxyFn):
        open(galaxyFn,'w').writelines(['chr1 10 100', 'chr1 200 1000'])
        return 'This should be track-data I think, but in what form? Return the path to a just created bed-file with the content?'

class GalaxyInterfaceAux:
    @staticmethod
    def standardizeTrackFiles(genome, trackName, parserClass, extraArgs=[]):
        runParserClass([genome, trackName, parserClass] + extraArgs)

    @classmethod
    def installNmerSupport(cls, genome, maxNmerLenForChains, maxNmerLenForTracks):
        #asserts to avoid unnecessarily large generation jobs (typically by mistake..)
        assert maxNmerLenForChains <= 20
        assert 4**maxNmerLenForTracks < 10000

        for i in range(1,maxNmerLenForChains+1):
            cls.createNmerChains(genome, i)
        for i in range(1,maxNmerLenForTracks+1):
            cls.createNmerTracks(genome, i)

    @staticmethod
    def createNmerChains(genome, n):
        NmerManager(genome).createNmerChains(n)

    @staticmethod
    def createNmerTracks(genome, n):
        NmerManager(genome).createNmerTracks(n)

    @staticmethod
    def createNmerTrack(genome, nmer):
        print '<pre>'
        nmerManager = NmerManager(genome)
        if nmerManager.nmerChainExists( len(nmer) ):
            print 'Creating k-mer track from index chain'
            nmerManager.createNmerTrack(nmer)
        else:
            chainOrder = nmerManager.getHighestExistingChainOrderLessThanN( len(nmer) )
            #chainOrder = 5#temp hack!!
            assert chainOrder is not None, 'no nmer data is available for this genome'
            print 'Creating k-mer track (order:%i) from index chain of lower order (%i)' % (len(nmer),chainOrder)

            nmerManager.createNmerTrackFromLowerOrderChain(nmer, chainOrder)
        print '</pre>'

    #@staticmethod
    #def createGenome(genome, fullName, fastaFn, allChromosomes, extendedChromosomes):
    #    from quick.extra.CustomFuncCatalog import createGenome as cg
    #    cg(genome, fullName, fastaFn, allChromosomes, extendedChromosomes)

    @staticmethod
    def clusterBySelfFeature(genome, tracksStr, track_namesStr, clusterMethod, extra_option, feature, distanceType, kmeans_alg, regSpec, binSpec, galaxyFn=''):
        #from galaxy_hb.lib.hyperbrowser.clusteringtool import executeSelfFeature
        assert galaxyFn != ''
        from quick.extra.clustering.ClusteringExecution import ClusteringExecution
        ClusteringExecution.executeSelfFeature(genome, [t.split(':') for t in tracksStr.split('$')], track_namesStr.split(':'), clusterMethod, extra_option, feature, distanceType, kmeans_alg, galaxyFn, regSpec, binSpec)

    @staticmethod
    def clusterByPairDistance(genome, tracksStr, track_namesStr, clusterMethod, extra_option, feature, extra_feature, regSpec, binSpec, galaxyFn=''):
        #from galaxy_hb.lib.hyperbrowser.clusteringtool import executeSelfFeature
        assert galaxyFn != ''
        from quick.extra.clustering.ClusteringExecution import ClusteringExecution
        ClusteringExecution.executePairDistance(genome, [t.split(':') for t in tracksStr.split('$')], track_namesStr.split(':'), clusterMethod, extra_option, feature, extra_feature, galaxyFn, regSpec, binSpec)

    @staticmethod
    def clusterByReference(genome, tracksStr, track_namesStr, clusterMethod, extra_option, distanceType, kmeans_alg, regSpec, binSpec, numreferencetracks=None, refTracks=None, refFeatures=None, yesNo=None, howMany=None, upFlank=None, downFlank=None, galaxyFn=''):
        #from galaxy_hb.lib.hyperbrowser.clusteringtool import executeSelfFeature
        assert galaxyFn != ''
        from quick.extra.clustering.ClusteringExecution import ClusteringExecution
        ClusteringExecution.executeReferenceTrack(genome, [t.split(':') for t in tracksStr.split('$')], track_namesStr.split(':'), clusterMethod, extra_option, distanceType, kmeans_alg, galaxyFn, regSpec, binSpec, numreferencetracks, refTracks, refFeatures, yesNo, howMany, upFlank, downFlank)

class GalaxyInterfaceTools:
    @staticmethod
    #@takes(str,list,list)
    def renameTrack(genome, oldTn, newTn):
        from quick.extra.RenameTrack import renameTrack
        renameTrack(genome, oldTn, newTn)

    @staticmethod
    def _writePrevReg(prevReg, outFile, numGenes):
        numSkipped = 0
        if prevReg is not None:
            if numGenes <= 2:
                outFile.write('\t'.join(str(prevReg[x]) for x in xrange(3)) + os.linesep)
            else:
                numSkipped = 1
        return numSkipped

    @staticmethod
    def getEnsemblGenes(genome, geneList, fn):
        GalaxyInterface.getGeneTrackFromGeneList(genome, GenomeInfo.getStdGeneRegsTn(genome), geneList, fn)
        #print open(fn).readlines()

    @staticmethod
    def getGeneTrackFromGeneList(genome, geneRegsTrackName, geneList, outFn):
        from gold.origdata.BedComposer import CategoryBedComposer

        if isinstance(geneList, basestring):
            geneList = ast.literal_eval(geneList)
            assert type(geneList) in [tuple, list]

        geneRegsFn = getOrigFn(genome, geneRegsTrackName, '.category.bed')
        assert geneRegsFn != None

        ubSource = GenomeInfo.getGeneRegs(genome, geneRegsFn, categoryFilterList=geneList, cluster=False)
        CategoryBedComposer(ubSource).composeToFile(outFn)
        #ensurePathExists(outFn)
        #outFile = open(outFn, 'w')
        #for region in ubSource:
        #    outFile.write(region.source + os.linesep)
        #outFile.close()
        #'\t'.join(str(x) for x in [region.chr, region.start, region.end, region.val, '0', region.strand]) + os.linesep)
        #ensemblTN = GenomeInfo.getPropertyTrackName(genome, 'ensembl')
        #TrackExtractor.extractOneTrackManyRegsToOneFile(ensemblTN, ubSource, fn, globalCoords=True, asOriginal=True, allowOverlaps=True)
    #
    #@staticmethod
    #def getGeneListOfRegulomeCluster(diseases, tfs):
    #    shelfFn = '/work/hyperbrowser/results/developer/static/maps/common/tfAndDisease2rankedGeneLists.shelf'
    #    assert all([x.split('(')[0].count('.') in [0,1] and x.count('(') in [0,1] for x in diseases.split(',')]), 'Multiple . or ( in: '+str(x)
    #    assert all([x.split('(')[0].count('.') in [0,1] and x.count('(') in [0,1] for x in tfs.split(',')]), 'Multiple . or ( in: '+str(x)
    #
    #    diseaseList = [d.split('(')[0].split('.')[-1].strip() for d in diseases.split('|')]
    #    tfList = [t.split('(')[0].split('.')[-1].strip() for t in tfs.split('|')]
    #    return GalaxyInterface._getGeneListOfRegulomeCluster(diseaseList, tfList, shelfFn)
    #
    #@staticmethod
    #def _getGeneListOfRegulomeCluster(diseases, tfs, geneListShelfFn, colTitle, rowTitle, hitText):
    #    print '<pre>'
    #    print 'Getting gene lists with diseases ',diseases, ' and tfs ',tfs
    #    print '#diseases: ',len(diseases), ' and #tfs: ',len(tfs)
    #    geneCounts = {}
    #    gene2diseaseSet = {}
    #    gene2tfSet = {}
    #    import third_party.safeshelve as safeshelve
    #
    #    geneListShelf = safeshelve.open(geneListShelfFn,'r')
    #    for disease in diseases:
    #        for tf in tfs:
    #            geneList = geneListShelf[repr((tf.replace(' ','_').lower(), disease.lower()))]
    #            for geneTriplet in geneList:
    #                gene = geneTriplet[0]
    #                count = geneTriplet[1]
    #                if count==0:
    #                    continue
    #
    #                if not gene in geneCounts:
    #                    geneCounts[gene] = 0
    #                    gene2diseaseSet[gene] = set([])
    #                    gene2tfSet[gene] = set([])
    #
    #                geneCounts[gene] += count
    #                gene2diseaseSet[gene].add(disease)
    #                gene2tfSet[gene].add(tf)
    #
    #    geneCountItems = geneCounts.items()
    #    sortedItems = list(reversed(sorted(geneCountItems, key=lambda t:(t[1],t[0]) )))
    #    rankedGenes = [x[0] for x in sortedItems]
    #
    #    genesOut = ', '.join(rankedGenes)
    #    countsOut = ', '.join([str(x[1]) for x in sortedItems])
    #    diseaseAssocOut = ', '.join([str(len(gene2diseaseSet[g])) for g in rankedGenes])
    #    tfAssocOut = ', '.join([str(len(gene2tfSet[g])) for g in rankedGenes])
    #
    #    headerLines = ['Ranked gene list:', \
    #                   'Corresponding total ' + hitText + ' counts:', \
    #                   'Corresponding number of ' + colTitle + ' each gene is involved with:', \
    #                   'Corresponding number of ' + rowTitle + ' each gene is involved with:']
    #    contentLines = [genesOut, countsOut, diseaseAssocOut, tfAssocOut]
    #    print '/n'.join(['%s\n%s\n' % (headerLines[i], contentLines[i]) for i in range(len(headerLines))])
    #    print '</pre>'
    #    return '<br>'.join(['<b>%s</b><br>%s<br>' % (headerLines[i], contentLines[i]) for i in range(len(headerLines))])
    #
    @staticmethod
    def getCombinedGeneList(genome, geneType1, geneType2, outFn):
        from gold.origdata.GenomeElementSource import GenomeElementSource
        from gold.util.CommonFunctions import getOrigFn
        from gold.origdata.GenomeElementSorter import GenomeElementSorter
        from gold.origdata.GEOverlapClusterer import GEOverlapClusterer
        from quick.origdata.GERegionBoundaryFilter import GERegionBoundaryFilter
        from quick.application.UserBinSource import GlobalBinSource

        superTN = ['Genes and Gene Prediction Tracks', 'Genes']
        fn1, fn2 = [getOrigFn(genome, superTN + [type.replace('_', ' ')], '.bed') for type in [geneType1, geneType2]]
        for fn,genetype in [(fn1,geneType1), (fn2,geneType2)]:
            if fn is None:
                raise Exception("Path does not exist for gene name: " + genetype)

        genes1, genes2 = [GenomeElementSource(fn, genome) for fn in [fn1, fn2]]
        genes1, genes2 = [GERegionBoundaryFilter(GEOverlapClusterer(GenomeElementSorter(geSource)), GlobalBinSource(genome))\
                          for geSource in [genes1, genes2]]

        allRegs = []
        for genes in [genes1, genes2]:
            allRegs += [[g.chr, g.start, g.end] for g in genes]

        outFile = open(DATA_FILES_PATH + os.sep + outFn, 'w')

        numGenes = 1
        countSkipped = 0
        prevReg = None
        for reg in sorted(allRegs):
            if prevReg is not None and int(reg[1]) - int(prevReg[2]) <= 0 and prevReg[0] == reg[0]:
                if int(reg[2]) > int(prevReg[2]):
                    prevReg[2] = reg[2]
                numGenes += 1
            else:
                countSkipped += GalaxyInterface._writePrevReg(prevReg, outFile, numGenes)
                prevReg = reg
                numGenes = 1
        countSkipped += GalaxyInterface._writePrevReg(prevReg, outFile, numGenes)
        print 'Number of genes skipped: ' + str(countSkipped)

    @staticmethod
    def convertBedGraphToWigVStepFillingGaps(inFn, outFn, gapValue):
        OrigFormatConverter.convertBedGraphToWigVStepFillingGaps(inFn, outFn, gapValue)

    @staticmethod
    def convertSegmentsToPoints(inFn, outFn, pointToUse):
        OrigFormatConverter.segments2points(inFn, outFn, pointToUse)

    @staticmethod
    def filterMarkedSegments(inFn, outFn, criteria, genome):
        if isinstance(criteria, basestring):
            criteriaFunc = Interpreter()(criteria)
        elif type(criteria) in [list,tuple]:
            criteriaFunc = lambda x: (criteria[0] is None or x>=criteria[0]) and (criteria[1] is None or x<=criteria[1])
        else:
            criteriaFunc = criteria
        OrigFormatConverter.filterMarkedSegments(inFn, outFn, criteriaFunc, genome)

    # TODO: should be refactored to instead use a geSource, which would accept both vStep
    # and bedGraph-formats etc..
    @staticmethod
    def filterSegmentsByLength(inFn, outFn, criteria):
        if type(criteria) in [list,tuple]:
            assert len(criteria) == 2
            criteriaFunc = lambda x: (criteria[0] is None or x>=criteria[0]) and (criteria[1] is None or x<=criteria[1])
        else:
            assert isinstance(criteria, basestring)
            criteriaFunc = Interpreter()(criteria)
        OrigFormatConverter.filterSegmentsByLength(inFn, outFn, criteriaFunc)

    @staticmethod
    def joinTracksToCategoryTrack(catNameToTrackNameDict):
        print 'This will be joined file contents..'
        return

    @classmethod
    def _getDnaBasedExpressionInterpreter(cls, locals):
        aeval = Interpreter()
        localObjectNames = ['s', 'a', 'c', 'g', 't', 'n', 'winSize', 'winIndexes']
        aeval.symtable.update(dict([(name, locals.get(name)) for name in localObjectNames]))
        return aeval

    @classmethod
    def wrappedDnaFunc(cls, tv, expression, midPointIsZero):
        s = tv.valsAsNumpyArray()

        winSize = len(s)
        winIndexes = range(winSize)
        import numpy

        if midPointIsZero:
            s = numpy.append(s[winSize/2:], s[:winSize/2])
            #s[0]='c'
        a = numpy.zeros(winSize)
        c = numpy.zeros(winSize)
        g = numpy.zeros(winSize)
        t = numpy.zeros(winSize)
        n = numpy.zeros(winSize)

        a[s=='a'] = 1
        c[s=='c'] = 1
        g[s=='g'] = 1
        t[s=='t'] = 1
        n[s=='n'] = 1

        a[s=='A'] = 1
        c[s=='C'] = 1
        g[s=='G'] = 1
        t[s=='T'] = 1
        n[s=='N'] = 1

        cls.validateDnaBasedExpressionAndReturnError(winSize, expression, \
                                                     raiseExceptions=True, logUnsupported=True)
        aeval = cls._getDnaBasedExpressionInterpreter(locals())
        return aeval(expression)

    #$createDnaBasedCustomTrack('testMit','Private:GK:test3011','21','g[0]+c[0]')
    #$createDnaBasedCustomTrack('testMit','Private:GK:test2','5','sum([g[i]+c[i] for i in winIndexes])')
    @classmethod
    def createDnaBasedCustomTrack(cls, genome, outTrackName, windowSize, expression, midPointIsZero=False, username=''):
        inTrackName = GenomeInfo.getSequenceTrackName(genome)
        #funcStr = 'lambda s:'+expression
        #GalaxyInterface.createCustomTrack(genome, inTrackName, outTrackName, windowSize, funcStr)

        import quick.application.parallel.PickleTools
        import pickle
        func = quick.application.parallel.PickleTools.FunctionPickleWrapper(expression, midPointIsZero)
        pickle.dumps(func)

        cls.createCustomTrack(genome, inTrackName, outTrackName, windowSize, func, username)

    @classmethod
    def validateDnaBasedExpressionAndReturnError(cls, windowSize, expression,
                                                 raiseExceptions=False, logUnsupported=False):
        try:
            winSize = int(windowSize)
        except Exception, e:
            if raiseExceptions:
                raise
            else:
                return 'Choose a valid number as the window size. Current: %s' % windowSize

        if winSize % 2 == 0:
            return 'The window size must be an odd number. Current: %i' % winSize

        winIndexes = range(winSize)

        if expression.strip() == '':
            return 'Please enter an expression to be evaulated for each sequence window'

        allowedWords = 'winSize,winIndexes,sum,max,min,if,else,for,in,len,range'.split(',')
        for word in re.findall('[a-zA-Z]{2,}',expression):
            if not word in allowedWords:
                if logUnsupported:
                    logLackOfSupport('Unsupported word encountered in createDnaBasedCustomTrack: ' + word)
                msg = 'Sorry, due to security concerns only a limited set of terms are allowed. Your term "%s" is not currently allowed. Please contact us if you think it should be added.' % word
                if raiseExceptions:
                    print msg
                    raise NotSupportedError(msg)
                else:
                    return msg

        import numpy

        a = numpy.zeros(winSize)
        c = numpy.zeros(winSize)
        g = numpy.zeros(winSize)
        t = numpy.zeros(winSize)
        n = numpy.zeros(winSize)

        try:
            aeval = cls._getDnaBasedExpressionInterpreter(locals())
            aeval(expression)
        except Exception, e:
            if raiseExceptions:
                raise
            else:
                return e

    @staticmethod
    def createCustomTrack(genome, inTrackName, outTrackName, windowSize, func, username=''):
        if type(inTrackName) is str:
            inTrackName = inTrackName.split(':')
        if type(outTrackName) is str:
            outTrackName = outTrackName.split(':')
        if type(windowSize) is str:
            windowSize = int(windowSize)
        #if type(func) is str:
        #    func = Interpreter()(func)

        inTrackName = GalaxyInterface._cleanUpTracks([inTrackName], genome, True)[0]

        #What is this?...
        if len(outTrackName)==2 and outTrackName[1]=='':
            outTrackName = outTrackName[0].split(':')
            print 'Splitting outTN ...'

        if ExternalTrackManager.isGalaxyTrack(outTrackName):
            outTrackName = ExternalTrackManager.getStdTrackNameFromGalaxyTN(outTrackName)

        if USE_PARALLEL:
            from quick.application.parallel.JobWrapper import CustomTrackCreatorJobWrapper
            from quick.application.parallel.JobHandler import JobHandler
            startTime = time.time()
            print "Starting custom track...<br>"

            jobWrapper = CustomTrackCreatorJobWrapper(TrackViewBasedCustomTrackCreator, genome, inTrackName, outTrackName, int(windowSize), func, username)

            uniqueId = datetime.now().strftime('%Y%m%d-%H%M%S%f')
            import pickle
            pickle.dumps(jobWrapper)
            jobHandler = JobHandler(uniqueId, True)
            jobHandler.run(jobWrapper)
            print "...done, took %f ms<br>" % (time.time() - startTime)
        else:
            TrackViewBasedCustomTrackCreator.createTrackGW(genome, inTrackName, outTrackName, int(windowSize), func, username)

    #@staticmethod
    #def createCustomTrackChr(genome, trackName, windowSize, funcStr, chr):
    #    GalaxyInterface.cleanUpTrackName(trackName)
    #    TrackViewBasedCustomTrackCreator.createTrackChr(genome, trackName, int(windowSize), Interpreter()(funcStr), chr)

    @staticmethod
    def createSegmentation(genome, inTrackName, outTrackName, categorizerMethodLines, minSegLen=5, username=''):
        GalaxyInterface.cleanUpTrackName(inTrackName)
        exec( os.linesep.join( ['def categorizerMethod(val,diff):'] + categorizerMethodLines) )
        FunctionCategorizer(inTrackName, categorizerMethod, genome, minSegLen).createNewTrack(outTrackName, username)

    @staticmethod
    def combineToTargetControl(inBedFnTarget, inBedFnControl, outWigFn):
        outF = open(outWigFn,'w')
        outF.write('track type=bedGraph'+os.linesep)
        for mark,fn in [['1',inBedFnTarget], ['0',inBedFnControl]]:
            for line in open(fn):
                if not any(line.startswith(x) for x in ['#','track']):
                    cols = line.split()
                    newCols = cols[:3] +[mark]
                    outF.write( '\t'.join(newCols) + os.linesep)
        outF.close()

    @staticmethod
    def startPreProcessing(genome, trackNameFilter=[], username='', mergeChrFolders=True):
        if isinstance(trackNameFilter, basestring):
            trackNameFilter = trackNameFilter.split(':')
        print '<PRE>'
        print 'Genome: %s' % genome
        print 'Base track for preprocessing: %s' % trackNameFilter
        PreProcessAllTracksJob(genome, trackNameFilter, username=username, mergeChrFolders=mergeChrFolders).process()
        print '</PRE>'

    @staticmethod
    def integrateTrackFromHistory(genome, historyTrackName, integratedTrackName, privateAccess=True, username=''):
        assert ExternalTrackManager.isGalaxyTrack(historyTrackName)
        assert all(type(tn) in [list,tuple] for tn in [historyTrackName, integratedTrackName])

        GalaxyInterface.cleanUpTrackName(historyTrackName)

        path = createOrigPath(genome, integratedTrackName)
        assert not os.path.exists(path), 'Path already exists in standardized tracks: ' + path

        galaxyFn = ExternalTrackManager.extractFnFromGalaxyTN(historyTrackName)
        suffix = ExternalTrackManager.extractFileSuffixFromGalaxyTN(historyTrackName)
        origFn = path + os.sep + 'fromHistory.' + suffix

        GalaxyInterface._integrateTrack(genome, galaxyFn, origFn, integratedTrackName, privateAccess, username)

    @staticmethod
    def _integrateTrack(genome, inFn, origFn, integratedTrackName, privateAccess=True, username=''):
        ensurePathExists(origFn)
        shutil.copy(inFn, origFn)
        os.chmod(origFn, 0664)

        #logMessage('genome, integratedTrackName:  '+genome+', '+repr(integratedTrackName))
        GalaxyInterface.startPreProcessing(genome, integratedTrackName, username)

        ti = TrackInfo(genome, integratedTrackName)
        ti.private=privateAccess
        ti.store()

    @classmethod
    #constructs unique id from galaxyFn and withinRunId. If this function is used several times per run, uniqueness must be ensured by using different withinRunId
    def expandBedSegmentsFromTrackNameUsingGalaxyFn(cls, inTrackName, genome, upFlank, downFlank, galaxyFn, withinRunId='1', treatTrackAs='segments', removeChrBorderCrossing=False):
        uniqueStaticId = GalaxyRunSpecificFile(['uniqueIdForExpandSegmentsMethod',withinRunId],galaxyFn).getId()
        outTrackName = GalaxyRunSpecificFile(['expandedSegments',withinRunId],galaxyFn).getExternalTrackName()
        cls.expandBedSegmentsFromTrackName(inTrackName, outTrackName, uniqueStaticId, genome, upFlank, downFlank, treatTrackAs, removeChrBorderCrossing)
        return outTrackName

    @classmethod
    #expands segments of inTrackName to a new track with outTrackName
    def expandBedSegmentsFromTrackName(cls, inTrackName, outTrackName, uniqueStaticId, genome, upFlank, downFlank, treatTrackAs='segments', removeChrBorderCrossing=False):
        if isinstance(inTrackName, basestring):
            inTrackName = inTrackName.split(':')
        if isinstance(outTrackName, basestring):
            outTrackName = outTrackName.split(':')
        if isinstance(uniqueStaticId, basestring):
            uniqueStaticId= uniqueStaticId.split(':')

        #extract inTrackName to fn
        origSegsFn = StaticFile(uniqueStaticId+['inFn.bed']).getDiskPath(True)
        TrackExtractor.extractOneTrackManyRegsToOneFile( \
            inTrackName, GlobalBinSource(genome), origSegsFn, fileFormatName='bed', \
            globalCoords=True, asOriginal=False, allowOverlaps=False)
        #construct expandedFn from outTrackName
        expandedFn = createOrigPath(genome, outTrackName, 'outFn.bed' )
        #expand segments to expandedFn
        cls.expandBedSegments(origSegsFn, expandedFn, genome, upFlank, downFlank, treatTrackAs, removeChrBorderCrossing)
        #pre-process outTrackName
        cls.startPreProcessing(genome, outTrackName)


    @staticmethod
    def expandBedSegments(inFn, outFn, genome, upFlank, downFlank, treatTrackAs='segments', removeChrBorderCrossing=False, suffix='bed'):
        assert int(upFlank) >= 0 or int(downFlank) >= 0
        assert treatTrackAs in ['points', 'segments', 'upstream', 'middle', 'downstream']
        upFlank, downFlank = int(upFlank), int(downFlank)

        from gold.origdata.GESourceWrapper import ElementModifierGESourceWrapper
        class PointSegmentExpander(ElementModifierGESourceWrapper):
            def __init__(self, geSource, genome=None, upFlank=0, downFlank=0, \
                         treatTrackAs='segments', removeChrBorderCrossing=False):

                ElementModifierGESourceWrapper.__init__(self, geSource, genome=genome)
                self._upFlank = upFlank
                self._downFlank = downFlank
                self._treatTrackAs = treatTrackAs
                self._removeChrBorderCrossing = removeChrBorderCrossing

            def _iter(self):
                pass

            def _next(self, brt, ge, i):
                strand = ge.strand if ge.strand is not None else True


                if self._treatTrackAs in ['upstream', 'middle', 'downstream']:
                    trackType = 'points'
                    if (self._treatTrackAs =='upstream' and strand == False) or \
                        (self._treatTrackAs == 'downstream' and strand == True):
                        ge.start = ge.end - 1

                    if self._treatTrackAs == 'middle':
                        ge.start = (ge.end + ge.start)/2

                    ge.end = ge.start + 1
                else:
                    trackType = 'segments'

                if strand:
                    leftFlank, rightFlank = self._upFlank, self._downFlank
                else:
                    leftFlank, rightFlank = self._downFlank, self._upFlank

                #try:
                if self._genome:
                    chrSize = GenomeInfo.getChrLen(self._genome, ge.chr)
                else:
                    chrSize = sys.maxint
                #except Exception, e:
                #    logMessage(e)
                #    chrSize = sys.maxint

                newStart = ge.start - leftFlank
                newEnd = (ge.end if ge.end is not None else ge.start + 1) + rightFlank

                if self._removeChrBorderCrossing and (newStart < 0 or newEnd > chrSize):
                    return None

                ge.start = max(0, newStart)
                if trackType == 'points' and suffix == 'gtrack':
                    ge.end = None
                else:
                    ge.end = min(chrSize, newEnd)

                return ge

        from gold.origdata.GenomeElementSource import GenomeElementSource
        geSource = GenomeElementSource(inFn, genome, suffix=suffix)

        expander = PointSegmentExpander(geSource, genome=genome, upFlank=upFlank, downFlank=downFlank, \
                                        treatTrackAs=treatTrackAs, removeChrBorderCrossing=removeChrBorderCrossing)

        outSuffix = suffix if suffix != 'point.bed' else 'bed'
        from gold.origdata.FileFormatComposer import getComposerClsFromFileSuffix
        composerCls = getComposerClsFromFileSuffix(outSuffix)
        composer = composerCls(expander)
        composer.composeToFile(outFn)


    #MAIN TOOLS:
    @staticmethod
    def createIntensityTrack(mainTrackName, controlTrackNameList, outTrackName, regSpec, binSpec, genome, galaxyFn, numDiscreteVals=10):
        print GalaxyInterface.getHbFunctionOutputBegin(galaxyFn, withDebug=True)

        cleanedTrackNames = GalaxyInterface._cleanUpTracks([mainTrackName]+controlTrackNameList, genome, True)
        mainTrackName = cleanedTrackNames[0]
        controlTrackNameList = cleanedTrackNames[1:]

        if isinstance(outTrackName, basestring):
            outTrackName = outTrackName.split(':')

        if ExternalTrackManager.isGalaxyTrack(outTrackName):
            outTrackName = ExternalTrackManager.getStdTrackNameFromGalaxyTN(outTrackName)

        print regSpec, binSpec
        userBinSource = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome, mainTrackName, controlTrackNameList[0])
        #DebugConfig.PASS_ON_VALIDSTAT_EXCEPTIONS = True #as there is only one applicable stat, and informative error message is preferred to uniformative that simply states that analysisDef is
        print 'Note that if main track is of type segment, it will be converted to midpoints'

        for i, controlTN in enumerate(controlTrackNameList):
            tfName = TrackInfo(genome, controlTN).trackFormatName
            if not tfName.lower().endswith('function'):
                errorStr = 'Control track #%s has wrong track type ("%s"). \nOnly control tracks of type "function" is currently supported when creating intensity tracks.' % (i+1, tfName)
                print errorStr
                raise InvalidFormatError(errorStr)


        if len(controlTrackNameList)==1:
            job = AnalysisDefJob('[dataStat=SimpleBpIntensityStat] [outTrackName=' + '^'.join(outTrackName) + '] [numDiscreteVals=%i] -> CreateFunctionTrackStat'% numDiscreteVals, \
                                 controlTrackNameList[0], mainTrackName, userBinSource)
            finalNumDiscreteVals = numDiscreteVals
        else:
            encodedControlTrackNameList = '^^'.join(['^'.join(tn) for tn in controlTrackNameList])
            reducedNumDiscreteVals = numDiscreteVals
            job = AnalysisDefJob('[dataStat=BpIntensityStat] [tf1=TrivialFormatConverter/SegmentToMidPointFormatConverter] [outTrackName=' + '^'.join(outTrackName) + '] [numDiscreteVals=%i]'% numDiscreteVals+\
                                 '[reducedNumDiscreteVals=%i] [controlTrackNameList='%reducedNumDiscreteVals + encodedControlTrackNameList + '] -> CreateFunctionTrackStat', \
                                  mainTrackName, None, userBinSource)
            finalNumDiscreteVals = reducedNumDiscreteVals
        print HtmlCore().tableHeader(['Region'] + ['Interval %i: intensity(#points)' %i for i in range(1,finalNumDiscreteVals+1)])
        job.run()
        print HtmlCore().tableFooter()
        controlTnStrList = [prettyPrintTrackName(tn) for tn in controlTrackNameList]
        infoMsg = 'An intensity track has been created for the track %s, controlled for possible confounders in the following tracks : %s' \
            % ( prettyPrintTrackName(mainTrackName), ', '.join(controlTnStrList[:-1]) + (' and ' if len(controlTnStrList) > 1 else '') + controlTnStrList[-1])
        print GalaxyInterface.getHbFunctionOutputEnd(infoMsg, withDebug=True)

    @staticmethod
    def parseExtFormatAndExtractTrackManyBins(genome, trackName, regSpec, binSpec, globalCoords, extractionFormat, fn, applyBoundaryFilter=False):
        fileFormatName, asOriginal, allowOverlaps = TrackExtractor.getAttrsFromExtractionFormat(extractionFormat)
        GalaxyInterface.extractTrackManyBins(genome, trackName, regSpec, binSpec, globalCoords, fileFormatName, asOriginal, allowOverlaps, fn, applyBoundaryFilter)

    @staticmethod
    def extractTrackManyBins(genome, trackName, regSpec, binSpec, globalCoords, fileFormatName, asOriginal, allowOverlaps, fn, applyBoundaryFilter=False):
        trackName = GalaxyInterface._cleanUpTracks([trackName], genome, True)[0]
        bins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome, trackName)
        if applyBoundaryFilter:
            from quick.origdata.GERegionBoundaryFilter import GERegionBoundaryFilter
            bins = GERegionBoundaryFilter(bins, GlobalBinSource(genome))

        TrackExtractor.extractOneTrackManyRegsToOneFile(trackName, bins, fn, fileFormatName=fileFormatName, \
                                                        globalCoords=globalCoords, asOriginal=asOriginal, \
                                                        allowOverlaps=allowOverlaps)

    @staticmethod
    def parseExtFormatAndExtractTrackManyBinsToRegionDirsInZipFile(genome, trackName, regSpec, binSpec, globalCoords, extractionFormat, galaxyFn):
        fileFormatName, asOriginal, allowOverlaps = TrackExtractor.getAttrsFromExtractionFormat(extractionFormat)
        GalaxyInterface.extractTrackManyBinsToRegionDirsInZipFile(genome, trackName, regSpec, binSpec, globalCoords, \
                                                                  fileFormatName, asOriginal, allowOverlaps, extractionFormat, galaxyFn)

    @staticmethod
    def extractTrackManyBinsToRegionDirsInZipFile(genome, trackName, regSpec, binSpec, globalCoords, fileFormatName, asOriginal, allowOverlaps, extractionFormat, galaxyFn):
        #globalCoords=False
        #GalaxyInterface.cleanUpTrackName(trackName)
        trackName = GalaxyInterface._cleanUpTracks([trackName], genome, True)[0]
        bins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome, trackName)
        #TODO 20160629 boris: add argument for zip file name
        zipBaseFn = trackName[-1].replace(' ','_') + '.extract.zip'
        zipFile = GalaxyRunSpecificFile([zipBaseFn], galaxyFn)

        TrackExtractor.extractOneTrackManyToRegionFilesInOneZipFile \
            (trackName, bins, zipFile.getDiskPath(), fileFormatName=fileFormatName, globalCoords=globalCoords, \
             asOriginal=False, allowOverlaps=allowOverlaps, ignoreEmpty=True)

        core = HtmlCore()
        core.paragraph('This history element contains data extracted from the track %s.' % prettyPrintTrackName(trackName))
        core.paragraph('The data is extracted as %s, %s' %
                       (extractionFormat[0].lower() + extractionFormat[1:], bins.description[0].lower() + bins.description[1:]))
        core.paragraph('The data is compressed into this Zip file: %s' % zipFile.getLink(zipBaseFn))
        print core


    @staticmethod
    def generateGoogleMapFromHistoryResult(galaxyFn):
        print 'Her kommer tool for aa lage regulom..'

        id = extractIdFromGalaxyFn(galaxyFn)
        mapName = '_'.join(['Usermap'] + id)

#    @staticmethod
#    def getWebToolGuiPrototype(toolId):
#        return GeneralGuiToolsFactory.getWebTool(toolId)
        #if toolId == 'hb_generic_1':
        #    return GeneralGuiToolsFactory.getWebTool("tool1")
        #if toolId == 'hb_generic_2':
        #    from test.sandbox.div.Lomes import HbPrototypeGui
        #    return HbPrototypeGui()
        #if toolId == 'hb_generic_3':
        #    from test.sandbox.div.DraftGuiPrototyper import HbPrototypeGui
        #    return HbPrototypeGui()
        #raise Exception('no such prototype: ' + toolId)


class GalaxyInterface(GalaxyInterfaceTools, GalaxyInterfaceAux):
    ALL_SUBTYPES_TEXT = '-- All subtypes --'
    UCSC_TRACK_TUPLE = ('UCSC tracks', 'ucsc', False)
    APPEND_ASSEMBLY_GAPS = True
    ALLOW_OVERLAPPING_USER_BINS = False
    #APPEND_COUNTS = True

    @staticmethod
    @runtimeLogging
    def getMainTrackNames(genome, preTracks=[], postTracks=[], username='', addUcscCategory=True):
        #return ['HPV_200kb, allTss']
        #return ProcTrackOptions().getMainTypes(extraTracks)
        fullAccess = GalaxyInterface.userHasFullAccess(username)
        tracks = ProcTrackOptions.getSubtypes(genome, [], fullAccess)

        opts = []
        for track in tracks:
            opts.append((GalaxyInterface._getTrackNameText(genome, [track]), track, False))

        if IS_EXPERIMENTAL_INSTALLATION:
            from quick.origdata.UcscHandler import UcscHandler
            ucscHandler = UcscHandler()
            if addUcscCategory and ucscHandler.isGenomeAvailable(genome):
                opts.append(GalaxyInterface.UCSC_TRACK_TUPLE)
            if fullAccess:
                opts.append(('StoreBioInfo','StoreBioInfo',False))
        #return [('external','external',False)]+preTracks + opts + postTracks
        return preTracks + opts + postTracks

    @staticmethod
    @runtimeLogging
    #@takes(str, list)
    def getSubTrackNames(genome, parentTrack, deep=True, username='', state=None, includeAllSubtracksChoice=True):
        assert (not deep)
        fullAccess = GalaxyInterface.userHasFullAccess(username)

        if len(parentTrack) > 0 and GalaxyInterface.isUcscTrackName(parentTrack):
            from quick.origdata.UcscHandler import UcscHandler
            ucscHandler = UcscHandler(state)
            opts, state = ucscHandler.getSubTrackNames(genome, parentTrack)
            #opts = []
            #for track in tracks:
            #    opts.append((track, track, False))
        elif len(parentTrack) > 0 and GalaxyInterface.isStoreBioTrackName(parentTrack):
            import zmq
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://localhost:5559")

            from config.Config import STOREBIOINFO_USER, STOREBIOINFO_PASSWD
            params = ['username:='+STOREBIOINFO_USER, 'password:='+STOREBIOINFO_PASSWD, 'operation:=getSubTrackName', \
                      'params:='+repr(parentTrack), 'class:=dataStorageServicePub']
            socket.send('##'.join(params))
            message = socket.recv()
            opts = ast.literal_eval(message)
        else:
            tracks = ProcTrackOptions.getSubtypes(genome, parentTrack, fullAccess)
            if includeAllSubtracksChoice:
                if len(tracks) > 0 and ProcTrackOptions.isValidTrack(genome, parentTrack, fullAccess):
                    tracks += [GalaxyInterface.ALL_SUBTYPES_TEXT]

            opts = []
            for track in tracks:
                opts.append((GalaxyInterface._getTrackNameText(genome, parentTrack + [track]), track, False))
        return opts, state

    @staticmethod
    def _getTrackNameText(genome, trackName):
        ti = TrackInfo(genome, trackName)
        subTrackCount = ti.subTrackCount
        if subTrackCount in [0,None] or \
            (subTrackCount == 1 and ti.isValid()):
            return trackName[-1]
        else:
            return '%s [%s]' % (trackName[-1], strWithStdFormatting(subTrackCount))

    @staticmethod
    def userHasFullAccess(username):
        from proto.config.Config import userHasFullAccess
        return userHasFullAccess(username)

    @staticmethod
    def getSupportedGalaxyFileFormats():
        from gold.application.DataTypes import getSupportedFileSuffixes
        return getSupportedFileSuffixes()

    @staticmethod
    def getSupportedGalaxyFileFormatsForBinning():
        from gold.application.DataTypes import getSupportedFileSuffixesForBinning
        return getSupportedFileSuffixesForBinning()

    @staticmethod
    def getSupportedGalaxyFileFormatsForFunction():
        from gold.application.DataTypes import getSupportedFileSuffixesForFunction
        return getSupportedFileSuffixesForFunction()

    @staticmethod
    @runtimeLogging
    #mainCategory in ['Descriptive statistics', 'Hypothesis testing']
    #returns a list of 4-tuples, consisting of (shortName, fullSpec, False, textualDescription)
    def getStatOptions(genome, trackName1, trackName2, mainCategory, state1=None, state2=None):
        try:
            realPreProc = False
            trackName1, trackName2 = GalaxyInterface._cleanUpTracks([trackName1, trackName2], genome, realPreProc, [state1,state2])

            #GalaxyInterface.cleanUpTrackNames(trackName1, trackName2)
            if not GalaxyInterface.areTrackNamesValid(genome, trackName1, trackName2):
                return []

            #trackName1 = GalaxyInterface._handleHistoryTrack(trackName1, '1')
            #trackName2 = GalaxyInterface._handleHistoryTrack(trackName2, '2')

            opts = []
            from gold.description.AnalysisManager import AnalysisManager
            for subCategory in AnalysisManager.getSubCategoryNames(mainCategory):
                fullCategory = AnalysisManager.combineMainAndSubCategories(mainCategory, subCategory)
                subCatAnalyses = []
                for analysis in AnalysisManager.getValidAnalysesInCategory(fullCategory, genome, trackName1, trackName2):
                    #print 'analysisDef: ', analysis.getDef(), '<br>'
                    fulldesc = GalaxyInterface.getTextFromAnalysisDef(analysis.getDef(), genome, trackName1, trackName2)
                    subCatAnalyses.append([str(analysis).split(':')[0] , quote( ('_' if analysis._reversed else '') + analysis.getDef(), ''), False, fulldesc])
                if len(subCatAnalyses)>0:
                    opts.append( [subCategory, '', True, ''])
                    opts += sorted(subCatAnalyses, key=smartStrLower)
            return opts
        except Exception,e:
            logException(e)
            return []

    #@staticmethod
    #def _handleHistoryTrack(tn, trackNum):
    #    if len(tn)==4 and tn[0].lower() == 'galaxy':
    #        fn = ExternalTrackManager.extractFnFromGalaxyTN(tn)
    #        suffix = ExternalTrackManager.extractFileSuffixFromGalaxyTN(tn)
    #        assert(externalType in suffix for externalType in ['wig','bed'])
    #
    #        geSource = ExternalTrackManager.getGESource(fn, suffix)
    #        return constructRedirectTrackName([getClassName(geSource)], 'ModelsForExternalTracks', 'chr21', 'Track'+trackNum+'-elements')
    #    else:
    #        return tn

    @staticmethod
    def _prepareRunLogging(): #analysisDef, regSpec, binSpec):
        #logMessage('run: ' + regSpec + ' ' + binSpec + ' ' + analysisDef)
        logging.getLogger(HB_LOGGER).addHandler(detailedJobRunHandler)

    @staticmethod
    def _tempAnalysisDefHacks(analysisDef):
        # fixme: Temporary hack, so that CompBinSplitting can be turned off in most cases.
        # note: Changes here have consequences for setting ALLOW_COMP_BIN_SPLITTING elsewhere,
        #   e.g., inGalaxyIntegrationTest, where one needs to set the constant in config.Config
        #   because of this method.
        import gold.util.CompBinManager
        if any(x in analysisDef for x in ['CategoryDivergenceMatrixStat', 'CategoryPointCountInSegsMatrixStat']):
            logMessage('hack')
            gold.util.CompBinManager.CompBinManager.ALLOW_COMP_BIN_SPLITTING = True
        else:
            from config.Config import ALLOW_COMP_BIN_SPLITTING as CFG_ALLOW_COMP_BIN_SPLITTING
            gold.util.CompBinManager.CompBinManager.ALLOW_COMP_BIN_SPLITTING = CFG_ALLOW_COMP_BIN_SPLITTING

    @staticmethod
    def _prepareRun(analysisDef, regSpec, binSpec, genome, trackName1, trackName2, trackNameIntensity=None, username=''):
        '''
        Constructs a userBinSource object based on regSpec and binSpec
        Constructs a fullRunArgs dict based on the bracket syntax in analysisDef
        Uses trackNames
        Returns these two objects.
        '''
        userBinSource = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome, trackName1, trackName2)

        GalaxyInterface._tempAnalysisDefHacks(analysisDef)

        fullRunArgs = {}
        if trackNameIntensity not in [[],None]:
            fullRunArgs['trackNameIntensity'] = '|'.join(trackNameIntensity)
        if username not in ['', None]:
            fullRunArgs['username'] = username
        return userBinSource, fullRunArgs

    @staticmethod
    def _handleRunResult(res, runDescription, userBinSource, genome, galaxyFn):
        assert(res is not None)

        presCollectionType = res.getPresCollectionType()
        if len(res.getResDictKeys()) > 0 and GalaxyInterface.APPEND_ASSEMBLY_GAPS and presCollectionType=='standard':
            gapRes = AssemblyGapJob(userBinSource, genome).run()
            res.includeAdditionalResults(gapRes, ensureAnalysisConsistency=False)

        #if len(res.getResDictKeys()) > 0 and GalaxyInterface.APPEND_COUNTS:
        #    try:
        #        countRes = CountBothTracksJob(userBinSource).run()
        #        res.includeAdditionalResults(countRes, ensureAnalysisConsistency=False)
        #    except IncompatibleTracksError:
        #        pass

        core = HtmlCore()
        core.line('Generating result figures and tables..')
        core.styleInfoEnd()
        print core

        #print runDescription
        core = HtmlCore()
        core.styleInfoBegin(styleId='run_description', styleClass='infomessagesmall rundescription')
        core.line(runDescription)
        core.styleInfoEnd()
        runDescriptionBox = str(core)

        res.setRunDescription(runDescriptionBox)

        GalaxyInterface._viewResults([res], galaxyFn)

#        adj._endProgress()

    @classmethod
    def runManual(cls, trackNames, analysisDef, regSpec, binSpec, genome, galaxyFn=None, trackNameIntensity=None, username='', \
                  printResults=True, printProgress=True, printHtmlWarningMsgs=True, applyBoundaryFilter=False, printRunDescription=True, **kwArgs):
        return cls._runCommon(trackNames, analysisDef, regSpec, binSpec, genome, galaxyFn, trackNameIntensity, username, printResults=printResults, \
                              printProgress=printProgress, printHtmlWarningMsgs=printHtmlWarningMsgs, applyBoundaryFilter=applyBoundaryFilter, \
                              printRunDescription=printRunDescription, fromMainTool=False, **kwArgs)

    @classmethod
    @usageAndErrorLogging
    #@takes(list,list,str,str,str,str,str,list,str)
    def run(cls, trackName1, trackName2, analysisDef, regSpec, binSpec, genome=DEFAULT_GENOME, galaxyFn=None, trackNameIntensity=None, username='', \
            state1=None, state2=None, demoID=None, printHtmlBeginEnd=True, **kwArgs):
        try:
            #startTime = time.time()
            if printHtmlBeginEnd:
                print GalaxyInterface.getHtmlBeginForRuns(galaxyFn)
            if demoID is not None:
                print GalaxyInterface._getDemoResultsIntro(demoID)
            print GalaxyInterface.getHtmlForToggles()

            return cls._runCommon([trackName1, trackName2], analysisDef, regSpec, binSpec, genome, galaxyFn, trackNameIntensity, username, [state1, state2], **kwArgs)
        except Exception, e:
            core = HtmlCore()
            core.styleInfoEnd()
            core.styleInfoBegin(styleClass='errormessagelarge')
            core.header('An error of type ' + getClassName(e) + ' occured during the analysis: ')
            core.paragraph(str(e), indent=True)
            core.paragraph(str(HtmlCore().emphasize( \
                           "Click 'Toggle debug' in the top right corner for more information. If this error seems " \
                           "to be a bug in the system, we are grateful if you report it. " \
                           "To report a bug, click the title of the history item to expand it and click the bug icon. " \
                           "In the bug report window, type in a message describing what caused the problem, " \
                           "and click the 'Report' button.")))
            core.styleInfoEnd()
            print str(core)
            raise
        finally:
            #print 'Run finished using %.1f seconds. ' % (time.time() - startTime)
            if printHtmlBeginEnd:
                print GalaxyInterface.getHtmlEndForRuns()

    @staticmethod
    def _runCommon(trackNames, analysisDef, regSpec, binSpec, genome=DEFAULT_GENOME, galaxyFn=None, trackNameIntensity=None, username='', \
                   states=None, printResults=True, printProgress=True, printHtmlWarningMsgs=True, applyBoundaryFilter=False,
                   printRunDescription=True, fromMainTool=True, **kwArgs):
        assert len(trackNames) > 0
        if len(trackNames) == 1:
            trackNames.append(None)
        trackNames.append(trackNameIntensity)

        GalaxyInterface._prepareRunLogging() #analysisDef, regSpec, binSpec)

        if printProgress:
            print str(HtmlCore().styleInfoBegin(styleClass='debug'))
            print 'Analysis initiated at time: %s \n\n' % datetime.now()

        if fromMainTool:
            trackNames[0], trackNames[1], analysisDef = GalaxyInterface._cleanUpAnalysisDef(trackNames[0], trackNames[1], analysisDef)

        try:
            trackNames = GalaxyInterface._cleanUpTracks(trackNames, genome, True, states, raiseIfAnyWarnings=printHtmlWarningMsgs)
        except Warning, e:
            core = HtmlCore()
            core.styleInfoEnd()
            core.styleInfoBegin(styleClass='warningmessagelarge')
            core.header('Warnings occured during the analysis: ')
            core.paragraph(str(e), indent=True)
            core.paragraph(str(HtmlCore().emphasize( \
                           "Click 'Toggle debug' in the top right corner for more information.")))
            core.styleInfoEnd()
            core.styleInfoBegin(styleClass='debug')
            print str(core)

        userBinSource, fullRunArgs = GalaxyInterface._prepareRun \
            (analysisDef, regSpec, binSpec, genome, trackNames[0], trackNames[1], trackNames[-1], username)

        if applyBoundaryFilter:
            from quick.origdata.GERegionBoundaryFilter import GERegionBoundaryFilter
            userBinSource = GERegionBoundaryFilter(userBinSource, GlobalBinSource(genome))

        trackName1 = trackNames[0]

        if not USE_PARALLEL or ('minimal' in kwArgs and kwArgs['minimal']):
            job = AnalysisDefJob(analysisDef, trackNames[0], trackNames[1] if len(trackNames) > 1 else None, userBinSource, galaxyFn=galaxyFn, **fullRunArgs)
            res = job.run(printProgress=printProgress)
        else:
            print "Running non-minimal, parallel job"
            #import sqlalchemy
            #print sqlalchemy.__path__

            if galaxyFn == None: #then this is a test
                uniqueId = datetime.now().strftime('%Y%m%d-%H%M%S%f')
                print "Making unique id : %s" % uniqueId
            else:
                uniqueId = extractIdFromGalaxyFn(galaxyFn)[1]
                print "unique id extracted from galaxyfn"

            fullRunArgs["uniqueId"] = uniqueId
            job = AnalysisDefJob(analysisDef, trackNames[0], trackNames[1], userBinSource, **fullRunArgs)

            res = job.run(printProgress=printProgress)

            if DebugConfig.USE_PROFILING:
                from quick.application.parallel.Config import PASSPHRASE
                from config.Config import PP_MANAGER_PORT
                import time
                MyManager.register("shutdown")
                manager = MyManager(address=("", PP_MANAGER_PORT), authkey=PASSPHRASE)
                manager.connect()
                manager.shutdown()

        if printRunDescription:
            runDescription = GalaxyInterface.getRunDescription(trackNames[0], trackNames[1], analysisDef, regSpec, \
                                                               binSpec, genome, username, trackNameIntensity, galaxyFn, showRandomSeed=True)
        else:
            runDescription = ''

        if printResults:
            GalaxyInterface._handleRunResult(res, runDescription, userBinSource, genome, galaxyFn)
        else:
            if printProgress:
                print str(HtmlCore().styleInfoEnd())

        return res

    @staticmethod
    def getHelpText(topic):
        if topic == 'null_model':
            core = HtmlCore()
            core.paragraph('When specifying hypothesis tests, the null model is often not explicitly stated. The null model ' \
                            'is then implicitly defined via the null hypothesis and the assumptions of the test. ' \
                            'A null model is a model of the observed system where the effect under study has been "nullified" ' \
                            'in some way. One must also choose a test statistic, i.e. a function of the sample, ideally one that ' \
                            'quantifies the effect under study in a precise manner. The hypothesis test compares the value of ' \
                            'the test statistic for the sample, i.e. the observed data, with the values of the test statistic under ' \
                            'the null model. The P-value is then the probability of obtaining a test statistic at least as extreme ' \
                            'as the one observed, assuming the null model is true.')
            core.paragraph('The following are some observations on the null model:')
            core.unorderedList(['In the Genomic HyperBrowser, a null model is specified by the combination of: ' + \
                                    str(HtmlCore().orderedList(['a preservation rule for each track, fixing some elements or ' \
                                                                    'characteristics of the track as present in the data.', \
                                                                'a stochastic process, describing how the non-preserved elements should be randomized.'])), \
                                'Example 1: "Preserve segments (T1)" means to fix the segments in first track as they are, without changing positions or lengths.', \
                                'Example 2: "Preserve segment lengths and inter-segment gaps (T2); randomize positions (T2) (MC)" means that ' \
                                            'the segments and the gaps between neighboring segments track 2 are permuted and drawn alternately. ' \
                                            'MC means that the hypothesis test uses Monte Carlo simulation.', \
                                'In the user interface of the Genomic HyperBrowser, the user describes the data and the null models, ' \
                                    'while the system based on this chooses the appropriate statistical test.', \
                                'The null model should reflect the combination of stochastic and selective events that constitutes the ' \
                                    'evolution behind the observed genomic feature. It should reflect biological realism, but also allow ' \
                                    'sufficient variation to permit the construction of tests.',
                                'The results of a hypothesis test is highly dependent on the null model.',
                                'Unrealistically simple null models may lead to false positives. One simple example is null models where ' \
                                    'the randomized elements are allowed in the centromeres, while the genomic features under study are not ' \
                                    'characterized there.', \
                                'Examining the results obtained for a set of different null models may often contribute important information.'])
            core.paragraph('A more in-depth discussion of null models is found in [1].')
            core.paragraph('[1] Sandve GK et al., <a href="http://genomebiology.com/2010/11/12/R121/">The Genomic HyperBrowser: ' \
                           'inferential genomics at the sequence level</a>, Genome Biol. 2010;11(12):R121')
            return str(core)

        elif topic == 'mcfdr':
            core = HtmlCore()
            core.paragraph('MCFDR is a novel algorithm for multiple hypothesis testing using the combination of sequential Monte Carlo (MC) and False Discovery Rate (FDR). ' \
                           'MCFDR was introduced in [1] and provides large gains in computational efficiency. The main idea is that MC sampling is stopped either by ' \
                           'sequential MC or based on a threshold on FDR. The following options govern the MCFDR algorithm ' + \
                           str(HtmlCore().emphasize(str(HtmlCore().highlight('(note that for most cases, leaving these at their default values should work well):')))))
            core.descriptionLine('Minimal number of MC samples (numResamplings)', 'The minimal number of samples that must be generated for each analysis region.', indent=True)
            core.descriptionLine('Number of MC samples per chunk (numSamplesPerChunk)', 'Threshold on number of samples. For each analysis region, the sampling stops when this number of samples has been reached.', indent=True)
            core.descriptionLine('Maximal number of MC samples (maxSamples)', 'Threshold on number of samples. For each analysis region, the sampling stops when this number of samples has been reached.', indent=True)
            core.descriptionLine('Sequential MC threshold (mThreshold)', 'Threshold on number of extreme samples. For each analysis region, the sampling ' \
                                                                 'stops when this number of extreme samples have been found. ' \
                                                                 'Extreme samples means samples where the sampled test statistic is more extreme than the observed value.', indent=True)
            core.descriptionLine('MCFDR threshold on FDR (globalPvalThreshold)', 'Significance threshold. For each analysis region, the MCFDR algorithm stops when the FDR-adjusted p-value is smaller than this threshold.', indent=True)
            core.descriptionLine('False discovery rate threshold for local results (fdrThreshold)', 'Threshold on the acceptable proportion of false discoveries, i.e. false positives, for local results.', indent=True)
            core.descriptionLine('Random seed', 'The seed for the random number generator. Setting this to a manual number ensures that rerunning of the hypothesis test gives the same result.', indent=True)
            core.paragraph('Note the following rules deciding which type of algorithm that runs:')
            core.unorderedList(['If minSamples < maxSamples and fdrThreshold > 0, then the algorithm is a full MCFDR algorithm, automatically tuning the number of samples', \
                                'If minSamples < maxSamples and fdrThreshold == 0, the algorithm is reduced to sequential Monte Carlo', \
                                'If minSamples == maxSamples, the algorithm is reduced to a standard Monte Carlo'])
            core.paragraph('Four preset schemes have been implemented:')
            core.descriptionLine('Quick and rough indication','numResamplings: 20, numSamplesPerChunk: 10, maxSamples: 150, mThreshold: 10, globalPvalThreshold: 0.05, fdrThreshold: 1.0', indent=True)
            core.descriptionLine('Moderate resolution of global p-value','numResamplings: 100, numSamplesPerChunk: 50, maxSamples: 2000, mThreshold: 20, globalPvalThreshold: 0.001, fdrThreshold: 1.0', indent=True)
            core.descriptionLine('Moderate resolution of global and local p-values ','numResamplings: 100, numSamplesPerChunk: 50, maxSamples: 2000, mThreshold: 20, globalPvalThreshold: 0.001, fdrThreshold: 0.01', indent=True)
            core.descriptionLine('Fixed 10 000 samples (slow)','numResamplings: 10000, numSamplesPerChunk: 10000, maxSamples: 10000, mThreshold: 1, globalPvalThreshold: 1.0, fdrThreshold: 1.0', indent=True)
            core.paragraph('Other schemes can be set by using the "Execute batch commands" tool.')
            core.paragraph('[1] Sandve GK, Ferkingstad E, Nyg&aring;rd S: <a href="http://bioinformatics.oxfordjournals.org/content/27/23/3235">' \
                           'Sequential Monte Carlo multiple testing</a>. Bioinformatics  2011, 27(23):3235-41.')
            return str(core)

        from proto.hyperbrowser.StaticFile import StaticImage
        TRACK_TYPE_IMAGE = StaticImage(['illustrations','tracktypes.png'])
        core = HtmlCore()
        core.paragraph('A track is a dataset associated with the base pair positions of a genome. ' \
                       'A track consists of a set of track elements, either dispersed sparsely ' \
                       'on the genomic coordinates, or densely, i.e. with no gaps between them. ')
        core.paragraph('Each track is of one of 15 generic track types (introduced in [1]). The following image illustrates ' \
                       'the different track types (click for a larger version):')
        core.link(str(HtmlCore().image(TRACK_TYPE_IMAGE.getURL(), style="padding: 10px; width: 300px;")), \
                        TRACK_TYPE_IMAGE.getURL(), withLine=False)
        core.paragraph('[1] Gundersen S, Kalas M, Abul O, Frigessi A, Hovig E, Sandve GK: Identifying ' \
                        'elemental genomic track types and representing them uniformly. BMC ' \
                        'Bioinformatics 2011, 12:494.')
        TRACK_TYPE_HELP = str(core)

        HELP_TEXTS = {'track1':str(HtmlCore().paragraph('Select the first genomic track to analyse. Start by selecting the category and then the specific track. ' + \
                                'To select a track in your history, select "-- From history (bed, wig, ...)) --" and then the history element. ')) + TRACK_TYPE_HELP, \
                      'track2':str(HtmlCore().paragraph('Select the second genomic track to analyse. Select "No track" if a single-track analysis is desired. ')), \
                      'analysis':'Select which analysis to perform on your track(s). The analyses are ordered as hypothesis tests or descriptive statistics. ' \
                      'See the help boxes for tracks for information about track types and their abbreviations.', \
                      'trackType':'Select how to treat your track data, either in their original formats or converted to simplified representations (e.g. points instead of segments).', \
                      'options':'Customize null hypothesis, alternative hypothesis and other options associated with the analysis.', \
                      'binning':'Select the region of the genome in which to analyze and/or how the analysis region should be divided into bins.', \
                      'bounding_regions':'Bounding regions are the regions where a track is defined, e.g. where there theoretically may be data. ' \
                                         'This means that if there is no data in a bounding region, the absence of data is informative, i.e. that ' \
                                         'the lack of data is not just caused by not looking at the particular region. Hence, the bounding region ' \
                                         'for most tracks should be defined without for instance the centromeres. For tracks with no explicitly defined ' \
                                         'bounding regions, the bounding regions are implicitly defined as all (complete) chromosomes ' \
                                         'containing at least one track element.<br><br>' \
                                         '<b>Note:</b> Intersecting bounding regions currently only supported for two tracks. If using a third track ' \
                                         'or an intensity track, only the bounding regions of the two first tracks are considered.',\
                      'trackIntensity':'Select an intensity track (created on the basis of confounding tracks) that is to be controlled for in the analysis.'}

        text = HELP_TEXTS.get(topic)
        if text is None:
            return ''
        else:
            return text

    @staticmethod
    def isNmerTrackName(genome, tn):
        nmerTn = GenomeInfo.getNmerTrackName(genome)
        return tn is not None and tn[0:len(nmerTn)] == nmerTn and type(tn[-1]) is str and len(tn[-1])>0

    @staticmethod
    def isUcscTrackName(tn):
        return tn is not None and len(tn)>0 and tn[0] == GalaxyInterface.UCSC_TRACK_TUPLE[1]

    @staticmethod
    def isStoreBioTrackName(tn):
        return tn is not None and len(tn)>0 and tn[0] == 'StoreBioInfo'

    @staticmethod
    def _cleanUpAnalysisDef(trackName1, trackName2, analysisDef):
        if len(analysisDef) > 0:
            analysisDef = unquote(analysisDef.replace('X','%'))

            if analysisDef[0] == '_':
               analysisDef = analysisDef[1:]
               trackName1, trackName2 = trackName2, trackName1
        return trackName1, trackName2, analysisDef

    @staticmethod
    def _cleanUpTracks(trackNames, genome, realPreProc, states=None, raiseIfAnyWarnings=False):
        if states==None:
            states = [None]*len(trackNames)

        for i,tn in enumerate(trackNames):
            GalaxyInterface.cleanUpTrackName(tn)
            #logMessage('statOpt: '+str(tn))

            #print 'TrackName from Galaxy:', tn
            if ExternalTrackManager.isGalaxyTrack(tn):
                #assert os.sep not in tn[-1], 'History element name contains %s: %s' % (os.sep, tn[-1])
                from gold.util.CommonFunctions import replaceIllegalElementsInTrackNames
                tn[-1] = replaceIllegalElementsInTrackNames(tn[-1])

                if realPreProc:
                    trackNames[i] = ExternalTrackManager.getStdTrackNameFromGalaxyTN(tn)
                    ExternalTrackManager.getPreProcessedTrackFromGalaxyTN\
                        (genome, tn, printErrors=False, raiseIfAnyWarnings=raiseIfAnyWarnings)
                else:
                    geSource = ExternalTrackManager.getGESourceFromGalaxyOrVirtualTN(tn, genome)
                    if geSource.hasOrigFile():
                        trackNames[i] = ExternalTrackManager.constructVirtualTrackNameFromGalaxyTN(tn)
                    else:
                        trackNames[i] = ExternalTrackManager.constructRedirectTrackName \
                            ([getClassName(geSource)], 'ModelsForExternalTracks', 'chr21', tn[-1])#'Track'+trackNum+'-elements')
            elif GalaxyInterface.isNmerTrackName(genome, tn):
                from gold.extra.nmers.NmerTools import NmerTools
                nmer, tn = NmerTools.getNmerAndCleanedNmerTrackName(genome, tn)
                trackNames[i] = tn
                if not ProcTrackOptions.isValidTrack(genome, tn, True):
                    #print genome, tn
                    if realPreProc:
                        assert NmerTools.isNmerString(nmer), NmerTools.getNotNmerErrorString(nmer)
                        GalaxyInterface.createNmerTrack(genome, nmer.lower())
                    else:
                        trackNames[i] = ExternalTrackManager.constructRedirectTrackName \
                            ([NmerManager.GE_SOURCE.__name__], 'ModelsForExternalTracks', 'chr21', 'k-mer')
            elif GalaxyInterface.isUcscTrackName(tn):
                from quick.origdata.UcscHandler import UcscHandler
                ucscHandler = UcscHandler(states[i])
                if realPreProc:
                    ti = TrackInfo(genome, trackNames[i])
                    if ti.timeOfPreProcessing is None or (datetime.now() - ti.timeOfPreProcessing).days > 0:
                        ucscHandler.downloadTrack(genome, trackNames[i])
                        job = PreProcessAllTracksJob(genome, trackNames[i], raiseIfAnyWarnings=raiseIfAnyWarnings)
                        job.process()
                else:
                    from gold.origdata.GenomeElementSource import getGenomeElementSourceClass
                    geSourceCls = getGenomeElementSourceClass('', suffix=trackNames[i][-1])
                    trackNames[i] = ExternalTrackManager.constructRedirectTrackName \
                        ([geSourceCls.__name__], 'ModelsForExternalTracks', 'chr21', ucscHandler.getPrettyTrackNameStr())

            elif GalaxyInterface.isStoreBioTrackName(tn):
                #fixme: should be refactored with more content in StoreBioHelper functions..
                from quick.extra.StoreBioHelper import getSBFnAndHBTrackAndFn, downloadFirstFtpFile

                fn, hbTrackName, hbFileName = getSBFnAndHBTrackAndFn(tn)
                if realPreProc:
                    ti = TrackInfo(genome, trackNames[i])
                    if ti.timeOfPreProcessing is None or (datetime.now() - ti.timeOfPreProcessing).days > 0:
                        from quick.extra.StoreBioHelper import getUrlToSBFile
                        url, hbFileName, hbTrackName = getUrlToSBFile(tn)#, STOREBIOINFO_USER, STOREBIOINFO_PASSWD
                        fn = createOrigPath(genome, tn, hbFileName)
                        ensurePathExists(fn)
                        downloadFirstFtpFile(fn, url)#open(fn,'w').write(urllib2.urlopen(url).read())
                        job = PreProcessAllTracksJob(genome, trackNames[i], raiseIfAnyWarnings=raiseIfAnyWarnings)
                        job.process()

                else:
                    from gold.util.CommonFunctions import getFileSuffix
                    from quick.extra.StoreBioHelper import getPreviewFile
                    tempFile = getPreviewFile(tn)
                    if  tempFile:
                        suffix = getFileSuffix(hbFileName)
                        geSource = ExternalTrackManager.getGESource(tempFile.name, suffix)
                        trackNames[i] = ExternalTrackManager.constructRedirectTrackName \
                            ([getClassName(geSource)], 'ModelsForExternalTracks', 'chr21', tn[-1])

        return trackNames

    @staticmethod
    @runtimeLogging
    def runValid(trackName1, trackName2, statClassName, regSpec, binSpec, genome=DEFAULT_GENOME, galaxyFn=None, **kwArgs):
        #logMessage('runValid: ' + regSpec + ' ' + binSpec)
        #print 'runValidGenome: ',genome
        #print 'VALID: ',regSpec,binSpec
        realPreProc = False
        trackNames = [trackName1, trackName2, kwArgs.get('trackNameIntensity')]
        trackNames = GalaxyInterface._cleanUpTracks(trackNames, genome, False)

        for tn in trackNames:
            if not GalaxyInterface.isTrackNameValid(genome, tn):
                if DebugConfig.VERBOSE:
                    logMessage('Invalid Trackname: ' + str(genome) + ' - ' + str(tn) )
                return 'There was a problem with the track ' + prettyPrintTrackName(tn) + ', please select a different track.'

        if len(statClassName) == 0 or statClassName in [None,'None']:
            return 'No statistic selected: select a statistic or try a different combintion of tracks'

        errorString = GalaxyInterface._validateRegAndBinSpec(regSpec, binSpec, genome, trackNames)

        if errorString:
            return errorString
        return True

    @staticmethod
    def trackValid(genome, tn):
        GalaxyInterface.cleanUpTrackName(tn)

        if ExternalTrackManager.isHistoryTrack(tn):
            try:
                ExternalTrackManager.getGESourceFromGalaxyOrVirtualTN(tn, genome).parseFirstDataLine()
            except Exception, e:
                return e

        elif GalaxyInterface.isNmerTrackName(genome, tn):
            from gold.extra.nmers.NmerTools import NmerTools
            nmer, tn = NmerTools.getNmerAndCleanedNmerTrackName(genome, tn)
            if not NmerTools.isNmerString(nmer):
                return NmerTools.getNotNmerErrorString(nmer)

        elif GalaxyInterface.isUcscTrackName(tn) or GalaxyInterface.isStoreBioTrackName(tn):
            try:
                GalaxyInterface._cleanUpTracks([tn], genome, realPreProc=False)
            except Exception, e:
                return e

        elif not len(tn) == 0 and not ProcTrackOptions.isValidTrack(genome, tn, True):
            return 'The track is not valid. Perhaps it is not correctly preprocessed?'

        return True

    @staticmethod
    def getRunNameAndDescription(trackName1, trackName2, analysisDef, regSpec, binSpec, genome):
        #return 'TestName', 'TestDescription'
        trackName1, trackName2 = GalaxyInterface._cleanUpTracks([trackName1, trackName2], genome, False)
        descr = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome, trackName1, trackName2).description
        #logMessage('getRunNameAndDescription past : descr = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome).description..... ')
        return "HyperBrowser: '%s' on %s" % (unquote(analysisDef).split(':')[0].strip().replace('_',''), prettyPrintTrackName(trackName1)) +\
                (" vs %s" % prettyPrintTrackName(trackName2) if trackName2 else ""), descr
                #'Analysis performed in genome: %s (and more for description field of history element..)' % genome


    @staticmethod
    def areTrackNamesValid(genome, trackName1, trackName2):
        for tn in (trackName1,trackName2):
            if not GalaxyInterface.isTrackNameValid(genome, tn):
                return False
        return True

    @staticmethod
    def isTrackNameValid(genome, tn):
        if tn not in [None,[]] and \
                not ExternalTrackManager.isHistoryTrack(tn) and \
                TrackInfo(genome, tn).timeOfPreProcessing is None:
            return False
        else:
            return True

    @staticmethod
    @usageAndErrorLogging
    #NB! genome is obsolete as parameter, and to be removed
    def runBatchLines(batchLines, galaxyFn=None, genome=None, username='', printResults=True, printProgress=True):
        try:
            from proto.RSetup import r
            #r('options(warn=2)')

            if printResults:
                print GalaxyInterface.getHtmlBeginForRuns(galaxyFn)

            if printProgress:
                print GalaxyInterface.getHtmlForToggles(withRunDescription=False)
                print str(HtmlCore().styleInfoBegin(styleClass='debug'))
                print 'Running batch, with script: '
                print os.linesep.join(batchLines)
                print ''

            toolLines, evalLines, analysisLines, assignmentTuples = GalaxyInterface._parseBatchLines(batchLines)

            toolLines = GalaxyInterface._applyVariableAssignments(toolLines, assignmentTuples)
            evalLines = GalaxyInterface._applyVariableAssignments(evalLines, assignmentTuples)
            analysisLines = GalaxyInterface._applyVariableAssignments(analysisLines, assignmentTuples)

            if len(analysisLines) == len(toolLines) == len(evalLines) == 0:
                raise Exception('Error, no line with content supplied.. Expected run-specs with 5 (super-batch) or 6 (std batch) columns: ')

            GalaxyInterface._prepareRunLogging()

            htmlLinks = GalaxyInterface._executeToolLines(toolLines, galaxyFn, username, printProgress, printResults)
            htmlLinks += GalaxyInterface._executeToolLines(evalLines, galaxyFn, username, printProgress, printResults)

            if len(analysisLines) > 0:
                res = GalaxyInterface._executeAnalysisLines(analysisLines, genome, galaxyFn, username, printProgress)

                core = HtmlCore()
                core.line('Generating result figures and tables..')
                core.styleInfoEnd()

                if printResults:
                    print core
                    GalaxyInterface._viewResults(res, galaxyFn)

                return res

            if printProgress:
                print str(HtmlCore().styleInfoEnd())
            if printResults:
                print str(HtmlCore().unorderedList(htmlLinks))

            return True

        finally:
            if printResults:
                print GalaxyInterface.getHtmlEndForRuns()

    @staticmethod
    def _parseBatchLines(batchLines):
        toolLines = []
        evalLines = []
        analysisLines = []
        assignmentTuples = []

        for line in batchLines:
            line = line.strip()
            if line == '' or line[0] == '#':
                continue
            elif line[0] == '$':
                if line[1:].lower().startswith('tool['):
                    toolLines.append(line[1:])
                else:
                    evalLines.append(line[1:])
            elif line[0] == '@':
                assert '=' in line
                assignmentSymbolPos = line.find('=') #first equals sign is assignment (more equal signs are allowed in value expression)
                newVar = line[:assignmentSymbolPos].strip()
                for existingVar in [x[0] for x in assignmentTuples]:
                    assert not (newVar.startswith(existingVar) or existingVar.startswith(newVar) ), "Error in batch spec: defined variables prefixes of each other: %s and %s" % (existingVar, newVar)

                assignmentTuples.append( [newVar, line[assignmentSymbolPos+1:].strip()] )
            else:
                assert len(line.split(BATCH_COL_SEPARATOR)) in [5,6], 'Error, expected 5 or 6 columns: ' + str(line.split(BATCH_COL_SEPARATOR))
                analysisLines.append(line)

        return toolLines, evalLines, analysisLines, assignmentTuples

    @staticmethod
    def _applyVariableAssignments(executionLines, assignmentTuples):
        for aIndex in range(len(assignmentTuples)):
            variable,value = assignmentTuples[aIndex]
            for i in range(len(executionLines)):
                executionLines[i] = executionLines[i].replace(variable, value)

            #to allow nested abbreviations, i.e. first define @t1 and @t2, and the define @TNs=@t1/@t2
            for i in range(aIndex+1, len(assignmentTuples)):
                assignmentTuples[i][1] = assignmentTuples[i][1].replace(variable, value)

        return executionLines

    @staticmethod
    def _executeToolLines(toolLines, galaxyFn, username, printProgress, printResults):
        htmlLinks = []

        for batchToolId, line in enumerate(toolLines):
            import time
            startTime = time.time()
            batchLineSpecificFile, link = GalaxyInterface._getBatchResultFileAndLink(galaxyFn, batchToolId, line)
            htmlLinks.append( link )

            if printProgress:
                print 'Running tool line: ', line
            #try:
            if line.lower().startswith('tool['):
                GalaxyInterface._executeToolLine(batchLineSpecificFile, line, username, galaxyFn)
            else:
                res = GalaxyInterface._executeEvalLine(batchLineSpecificFile, line, galaxyFn)

                if printResults:
                    print>>open(batchLineSpecificFile.getDiskPath(), 'a'), 'Result:', res

            if printProgress:
                print 'Time spent executing line %s: %.1f seconds' % (line, time.time()-startTime)

        return htmlLinks

    @staticmethod
    def _getBatchResultFileAndLink(galaxyFn, batchToolId, line):
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile

        #batchLineSpecificId = extractIdFromGalaxyFn(galaxyFn) + [str(batchToolId)]
        #batchLineSpecificFile = GalaxyRunSpecificFile(['results.html'], batchLineSpecificId)
        batchLineSpecificFile = GalaxyRunSpecificFile([str(batchToolId), 'results.html'], galaxyFn)
        batchLineSpecificFile.getFile() #Creates the file

        return batchLineSpecificFile, batchLineSpecificFile.getLink('Results for batch run #%s: %s' % (batchToolId, line))

    @staticmethod
    def _executeToolLine(batchLineSpecificFile, line, username, galaxyFn):
        import re
        from collections import OrderedDict

        match = re.search('\[([A-Za-z0-9_-]+)\]', line)
        if not match:
            raise InvalidRunSpecException('Tool id not found in batch command line: ', line)
        toolId = match.groups()[0]
        match = re.search('\((.*)\)', line)
        if not match:
            raise InvalidRunSpecException('Choices not found in batch command line: ', line)
        choicesStr = match.groups()[0]
        #choicesStr.replace('\\|', '\\\\')
        rawChoices = choicesStr.split('|')
        globalsDict = {}
        builtins = {'False': False, 'True': True, 'OrderedDict': OrderedDict}
        for choice in rawChoices:
            match = re.search('^([A-Za-z0-9_-]+)\((.*)\)$', choice)
            if match:
                from collections import namedtuple
                tupleName, contents = match.groups()
                if tupleName not in builtins:
                    fieldNames = re.findall('([A-Za-z0-9_-]+)=', contents)
                    aeval = Interpreter()
                    aeval.symtable['namedtuple'] = namedtuple
                    globalsDict[tupleName] = aeval("namedtuple('%s', %s)" % (tupleName, fieldNames))

        globalsDict['OrderedDict'] = OrderedDict
        aeval = Interpreter()
        aeval.symtable.update(globalsDict)
        choices = [aeval(x) for x in rawChoices]
        #choices = [choice.replace('\\\\', '\\|') for choice in choices]

        webTool = getToolPrototype(toolId)
        ChoiceTuple = webTool.getNamedTuple()
        if ChoiceTuple is not None:
            choices = ChoiceTuple(*choices)

        if DebugConfig.USE_PROFILING:
            from gold.util.Profiler import Profiler
            profiler = Profiler()
            profiler.run('webTool.execute(choices, galaxyFn=batchLineSpecificFile.getDiskPath(), username=username)', globals(), locals())
            profiler.printStats()
            profiler.printLinkToCallGraph(['profile_runBatchLines'], galaxyFn)
        else:
            webTool.execute(choices, galaxyFn=batchLineSpecificFile.getDiskPath(), username=username)

    @staticmethod
    def _executeEvalLine(batchLineSpecificFile, line, galaxyFn):
        #import math
        import inspect
        aeval = Interpreter()
        aeval.symtable['GalaxyInterface'] = GalaxyInterface

        if '(' in line:
            funcStr = line.split('(')[0]
            func = aeval('GalaxyInterface.' + funcStr)
            funcArgs = inspect.getargspec(func)
            if funcArgs.defaults is not None:
                if 'galaxyFn' in funcArgs.args[-len(funcArgs.defaults):]:
                    assert line[-1] == ')'
                    line = line[:-1] + ', galaxyFn="%s")' % batchLineSpecificFile.getDiskPath()

        if DebugConfig.USE_PROFILING:
            from gold.util.Profiler import Profiler
            profiler = Profiler()
            res = profiler.run("aeval('GalaxyInterface.' + line)")
            profiler.printStats()
            profiler.printLinkToCallGraph(['profile_runBatchLines'], galaxyFn)
        else:
            #logMessage(line)
            #logMessage(repr(globals()))
            #logMessage(repr(locals()))
            res = aeval('GalaxyInterface.' + line)

        return res

    @staticmethod
    def _executeAnalysisLines(analysisLines, genome, galaxyFn, username, printProgress):
        from quick.batch.BatchRunner import SuperBatchRunner
        analysisGenomes = set([line.split(BATCH_COL_SEPARATOR)[0] for line in analysisLines])
        if not len(analysisGenomes)==1:
            raise NotSupportedError('Using bath-lines relating to multiple different genomes (%s) in a single batch run is not currently supported.' % analysisGenomes)
        genome = list(analysisGenomes)[0]

        analysisLinesWithoutGenome = [ line[ line.find(BATCH_COL_SEPARATOR)+1:] for line in analysisLines]
        if not GalaxyInterface.isAccessibleGenome(genome, username):
            raise Exception('Error: The specified genome (%s) is not accessible to the user (%s).' %\
                            (genome, username))

        res = SuperBatchRunner.runManyLines(analysisLinesWithoutGenome, genome, True, galaxyFn=galaxyFn, printProgress=printProgress)
        return res

    #get classes to extract a x/y-value from track in each user bin
    @staticmethod
    def getSummarizerStatOptions(trackName):
        return 'DummyClassName'

    @staticmethod
    def getTrackExtractionOptions(genome, trackName):
        from quick.application.UserBinSource import MinimalBinSource
        from gold.origdata.FileFormatComposer import findMatchingFileFormatComposers, getComposerClsFromFileSuffix

        trackNames = [trackName]
        GalaxyInterface._cleanUpTracks(trackNames, genome, realPreProc=False)
        trackName = trackNames[0]

        tf = PlainTrack(trackName).getTrackView(MinimalBinSource(genome)[0]).trackFormat

        extractionOptions = []
        matchingComposers = findMatchingFileFormatComposers(tf)
        for composerInfo in matchingComposers:
            allOverlapRules = tf.getAllOverlapRules()
            for allowOverlaps in allOverlapRules:
                extractionOptions.append( \
                    (composerInfo.trackFormatName.capitalize() + \
                        ' ' + TrackExtractor.getFileFormatText(composerInfo.fileFormatName) + \
                        (', ' + (TrackExtractor.ALLOW_OVERLAPS_TRUE_TEXT if allowOverlaps else \
                                 TrackExtractor.ALLOW_OVERLAPS_FALSE_TEXT) \
                                 if len(allOverlapRules) > 1 else ''), \
                     composerInfo.fileSuffix) )

        ti = TrackInfo(genome, trackName)
        if ti.fileType != '':
            try:
                extractionOptions.append(
                    (TrackExtractor.ORIG_FILE_FORMAT_TEXT.capitalize() + \
                        ' ' + TrackExtractor.getFileSuffixText(ti.fileType), \
                     getComposerClsFromFileSuffix(ti.fileType).getDefaultFileNameSuffix()))
            except Exception, e:
                logException(e)

                #Temporary fix for old tracks with wrong fileType. Should be removed when all tracks have been preprocessed.
                if not ti.fileType in GalaxyInterface.getSupportedGalaxyFileFormats() and ti.fileType is not None:
                    from gold.util.CommonFunctions import getFileSuffix
                    oldFileType = ti.fileType
                    ti.fileType = getFileSuffix(oldFileType)
                    ti.store()
                    logMessage("Changed file type of track '%s' from '%s' to '%s'" %
                               (':'.join(trackName), oldFileType, ti.fileType))

        return extractionOptions

    @staticmethod
    def isRScriptValid(trackName1, trackName2, rScriptAnalysisId):
        GalaxyInterface.cleanUpTrackName(trackName1)
        GalaxyInterface.cleanUpTrackName(trackName2)
        return True #currently, until it works all correctly...
        if any([tn[0].lower() == 'galaxy' and len(tn)==4 for tn in (trackName1, trackName2) if len(tn)>0] ):
            return True
        #analysis = Analysis(rScriptAnalysisId)
        #analysis.setTracks(trackName1, trackName2)
        #return analysis.isValid()

    @staticmethod
    def getTrackTypeOptions(analysisDef):
        #print 'From Morten: ',analysisDef
        analysis = AnalysisDefHandler(unquote(analysisDef))
        #return q.getOptionLabelsAsText(), q.getOptionsAsText()
        #trackTypeKeys = [ x for x in ['tf1','tf2'] if x in analysis.getChoices().keys() ]
        return [analysis.getFormatConverterOptionLabelsAsText(), analysis.getFormatConverterOptionsAsText()]
#        raise Exception(str(a) + ' ' + str(optionLabelKeys))
        #return a
        #assert False, str(q.getOptionLabelsAsText() ) + ' - ' + str(q.getOptionsAsText())
        #return q.getOptionLabelsAsText()[0:1], {a: q.getOptionsAsText()[a]}

    @staticmethod
    def getConfigOptions(analysisDef):
        analysis = AnalysisDefHandler(unquote(analysisDef))
        return [analysis.getInterfaceOptionLabelsAsText(), analysis.getInterfaceOptionsAsText()]
        #print 'From Morten: ',analysisDef
        #q = AnalysisDefHandler(unquote(analysisDef))
        #ret = [q.getOptionLabelsAsText(), q.getOptionsAsText()]
        #a = ret[0][0]
        #ret[0] = ret[0][1:]
        #del ret[1][a]
        #return ret

    #@staticmethod
    #def getConfigOptions(analysisDef):
    #    #print 'From Morten: ',analysisDef
    #    q = AnalysisDefHandler(unquote(analysisDef))
    #    return q.getOptionLabelsAsText(), q.getOptionsAsText()

    @staticmethod
    @takes(str, dict)
    def setConfigChoices(analysisDef, optionsDict):
        intensityTrigger = '_intensityTN'
        if intensityTrigger in optionsDict:
            print 'HANDLING INTENSITY TRACK..'
            intensityTN = optionsDict[intensityTrigger]
            optionsDict = copy(optionsDict)
            del optionsDict[intensityTrigger]
            intensityPrefix = '[' + intensityTrigger + '=' + intensityTN + ']'
        else:
            intensityPrefix = ''

        try:
            q = AnalysisDefHandler(unquote(analysisDef))
            for labelText in optionsDict:
                q.setChoice( unquote(labelText), unquote(optionsDict[labelText]) )
            q.syncH1WithTail()
            return intensityPrefix + q.getDefAfterChoices()

        except Exception, e:
            logException( e, message='Error in setConfigChoices with resulting definition: ' + q.getDefAfterChoices() )
            return ''
    #
    #@staticmethod
    #def _syncH1WithTail(analysisDef):
    #    optionKeys = analysisDef.getAllOptionsAsKeys()
    #    if 'H1' in optionKeys and 'tail' in optionKeys:
    #        try:
    #            tailChoice = analysisDef.getChoice('tail')
    #            analysisDef.setChoice('H1', tailChoice)
    #
    #        except (ShouldNotOccurError), e:
    #            logException(e, logging.WARNING,'Could not find H1, probably mismatch between tail and H1 in analysisDef (tail choice: %s)' % self.getChoice('tail') )
    #        except Exception, e:
    #            logException(e, logging.WARNING,'Could not find H1')
    #
    #    return analysisDef

    @staticmethod
    @takes(str, str, list, list)
    @returns(str)
    def getTextFromAnalysisDef(analysisDef, genome, trackName1, trackName2):
        realPreProc = False
        trackName1, trackName2, analysisDef = GalaxyInterface._cleanUpAnalysisDef(trackName1, trackName2, analysisDef)
        trackName1, trackName2 = GalaxyInterface._cleanUpTracks([trackName1, trackName2], genome, realPreProc)

        from gold.description.Analysis import Analysis
        text = str( Analysis(analysisDef, genome, trackName1, trackName2) )
        return AnalysisDefHandler.splitAnalysisText(text)[1]
        #return text[ text.find(':')+1 :]
        #return text.split(':')[-1]

    @staticmethod
    @takes(str, list)
    @returns(str)
    def getTrackInfo(genome, trackName):
        #genome ='hg18'
        #return 'further info on ' + ':'.join(trackName) + ' will come..'
        #try:
        GalaxyInterface.cleanUpTrackName(trackName)
        #return TrackInfo(genome, trackName).allInfo().decode('ascii','ignore')

        return TrackInfo(genome, trackName).allInfo()
        #except Exception,e:
        #    traceback.print_exc()
        #    brk(host='localhost', port=9000, idekey='galaxy')
        #    return str(e.__class__) + str(e) + str(trackName) + str(genome)

    @staticmethod
    @takes(str)
    @returns(str)
    def getGenomeInfo(genome):
        #return GenomeInfo(genome).allInfo().decode('ascii','ignore')
        if genome:
            return GenomeInfo(genome).allInfo()
        return 'Genome build is not selected'

    @staticmethod
    @returns(str)
    def getHbVersion():
        return HB_VERSION

    @staticmethod
    @runtimeLogging
    def getRunDescription(trackName1, trackName2, analysisDef, regSpec, binSpec, genome=DEFAULT_GENOME, \
                          username='', trackNameIntensity=None, galaxyFn=None, showRandomSeed=False):
        #logMessage('getRunDescription: ' + regSpec + ' ' + binSpec + ' ' + analysisDef)
        #assert username != None

        #Clean up and if necessary switch tracknames:
        #trackName1, trackName2, analysisDef, dummy = GalaxyInterface._handleSpecs(trackName1, trackName2, analysisDef, genome)

        #trackName1 = GalaxyInterface._handleHistoryTrack(trackName1, '1')
        #trackName2 = GalaxyInterface._handleHistoryTrack(trackName2, '2')
        #
        #if analysisDef[0] == '_':
        #    analysisDef = analysisDef[1:]
        #    trackName1, trackName2 = trackName2, trackName1
        if GalaxyInterface.userHasFullAccess(username):
            from quick.util.CommonFunctions import createHyperBrowserURL
            urlForTrackAutoSelection = createHyperBrowserURL(genome, trackName1, trackName2)
        else:
            urlForTrackAutoSelection = None

        if showRandomSeed:
            from gold.util.RandomUtil import getManualSeed
            manualSeed = getManualSeed()
        else:
            manualSeed = None

        try:
            #if GalaxyInterface.userHasFullAccess(username):
            revEngBatchLine = GalaxyInterface._revEngBatchLine(trackName1, trackName2, trackNameIntensity, \
                                                               analysisDef, regSpec, binSpec, genome, \
                                                               manualSeed=manualSeed)
            if galaxyFn is not None:
                batchLineStaticFile = GalaxyRunSpecificFile(['batchlines.txt'], galaxyFn).writeTextToFile(revEngBatchLine)
            #else:
                #revEngBatchLine = None
        except Exception, e:
            logException(e, message='Error in _revEngBatchLine')
            revEngBatchLine = None
        except:
            revEngBatchLine = None

        realPreProc = False
        trackName1, trackName2, analysisDef = GalaxyInterface._cleanUpAnalysisDef(trackName1, trackName2, analysisDef)
        trackName1, trackName2, trackNameIntensity = GalaxyInterface._cleanUpTracks([trackName1, trackName2, trackNameIntensity], genome, realPreProc)
        userBinSource = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome, trackName1, trackName2)

        from gold.description.RunDescription import RunDescription
        try:
            return RunDescription.getRunDescription(trackName1, trackName2, trackNameIntensity, analysisDef, userBinSource, \
                                                    revEngBatchLine, urlForTrackAutoSelection, manualSeed)
        except Exception, e:
            logException(e,level=logging.WARN,message='Error in generating run description')
            return 'Sorry. The system was not able to generate a description of this analysis.'

    #@staticmethod
    #def getAnalysisInfo(analysisDef):
    #    return 'further info on ' + str( Analysis(analysisDef) ) + ' will come..'

    #@staticmethod
    #def getBinningInfo(regSpec, binSpec):
    #    return 'further info on ' + regSpec + ', ' + binSpec + ' will come..'

    @staticmethod
    #@takes(str, list, list)
    #@returns(str) #list of 'Hypothesis testing' and/or 'Descriptive statistics'
    def getAnalysisCategories(genome, trackName1, trackName2):
        from gold.description.AnalysisManager import AnalysisManager
        catNames = AnalysisManager.getMainCategoryNames()
        #return [ (c,c,False) for c in reversed(sorted(catNames, key=smartStrLower)) ]
        if trackName2 in [None, []]:
            return [(c,c,False) for c in catNames]
        else:
            return [(c,c,False) for c in reversed(catNames)]

    @staticmethod
    def getValidAnalysisDefFromTitle(analysisTitle, genome, trackName1, trackName2):
        #GalaxyInterface.cleanUpTrackName(trackName1)
        #GalaxyInterface.cleanUpTrackName(trackName2)
        trackName1, trackName2 = GalaxyInterface._cleanUpTracks([trackName1, trackName2], genome, realPreProc=False)
        from gold.description.AnalysisManager import AnalysisManager
        return quote(AnalysisManager.getValidAnalysisDefFromTitle(unquote(analysisTitle), genome, trackName1, trackName2), '')

    @staticmethod
    def getAnalysisList(genome, category, trackName1, trackName2, state1=None, state2=None):
        return GalaxyInterface.getStatOptions(genome, trackName1, trackName2, category, state1, state2)

    @staticmethod
    def getTrackInfoRecord(genome, trackName):
        GalaxyInterface.cleanUpTrackName(trackName)
        return TrackInfo(genome, trackName).getUIRepr()

    @staticmethod
    def setTrackInfoRecord(genome, trackName, attrDict, allSubtypes, username):
        fullAccess = GalaxyInterface.userHasFullAccess(username)
        GalaxyInterface.cleanUpTrackName(trackName)
        if allSubtypes:
            if ProcTrackOptions.isValidTrack(genome, trackName, fullAccess):
                GalaxyInterface.setTrackInfoRecord(genome, trackName, attrDict, False, username)

            subTypes = ProcTrackOptions.getSubtypes(genome, trackName, fullAccess)
            for subType in subTypes:
                GalaxyInterface.setTrackInfoRecord(genome, trackName + [subType], attrDict, True, username)

        elif fullAccess:
            trackInfo = TrackInfo(genome, trackName)
            trackInfo.setAttrs(attrDict, username)
            trackInfo.store()

    #@staticmethod
    #def _getName(genome, experimental=False, username=''):
    #    usersFn = createOrigPath(genome, [], '_users.txt')
    #    if os.path.exists(usersFn):
    #        if username == '' or not any(user.strip() == username for user in open(usersFn)):
    #            return None
    #        # fixme: To be removed in next major update. Only here to allow RC access to experimental
    #        #        tracks with access restrictions.
    #        experimental=True
    #
    #    nameFn = createOrigPath(genome, [], '_name.txt' if experimental else '#name.txt')
    #    if os.path.exists(nameFn):
    #        return open(nameFn, 'r').read().strip()
    #    return None
    #
    @classmethod
    def isAccessibleGenome(cls, genome, username):
        if not genome or genome == '?':
            return False

        #Caching hack to increase speed of displaying genome selection menu
        if hasattr(cls, 'cachedGenomeInfoDict'):
            gi = cls.cachedGenomeInfoDict[genome]
        else:
            gi = GenomeInfo(genome)

        if not gi.isInstalled():
            #logMessage('Error: Genome not installed: ' + genome)
            return False
        if gi.isExperimental and not IS_EXPERIMENTAL_INSTALLATION:
            #logMessage('Error: Genome is experimental (and installation is not): ' + genome)
            return False
        if gi.isPrivate and not username in gi.privateAccessList:
            #logMessage('Error: User (%s) has no access to private genome: %s' % (username, genome))
            return False
        return True

    @classmethod
    def getAllGenomes(cls, username=''):
        genomeDir = ORIG_DATA_PATH
        candidateGenomes = sorted([fn for fn in os.listdir(genomeDir) if \
                                    os.path.isdir(genomeDir + os.sep + fn) \
                                    and not os.path.islink(genomeDir + os.sep + fn)
                                    and not any(fn.startswith(x) for x in ['.','#','_'])], key=str.lower)
        #if 'hg18' in candidateGenomes:
        #    candidateGenomes.insert(0, candidateGenomes.pop(candidateGenomes.index('hg18')))

        #Caching hack to increase speed of displaying genome selection menu
        if not hasattr(cls, 'cachedGenomeInfoDict'):
            cls.cachedGenomeInfoDict = GenomeInfo.getGenomeInfoDictForGenomeList(candidateGenomes)
        
        genomes = []
        for candidate in candidateGenomes:
            #logMessage('Candidate: %s' % candidate)

            if GalaxyInterface.isAccessibleGenome(candidate, username):
                genomes.append((cls.cachedGenomeInfoDict[candidate].fullName, candidate, False))
                #genomes.append((GenomeInfo(candidate).fullName, candidate, False))

        #logMessage('Genomes: %s' % genomes)
        genomes.sort()
        return genomes

    @staticmethod
    def _getBinningCategoryTuplesCommon(genome, trackName1, trackName2, ubSourceRegistryCls):
        trackName1, trackName2 = GalaxyInterface._cleanUpTracks([trackName1, trackName2], genome, False)
        ubSourceRegistry = ubSourceRegistryCls(genome, [trackName1, trackName2])
        return ubSourceRegistry.getNameAndKeyTuplesOfAllUserBinSources()

    @classmethod
    def getBinningCategoryTuples(cls, category, genome, trackName1, trackName2):
       from gold.description.AnalysisManager import AnalysisManager
       assert category in AnalysisManager.getMainCategoryNames()
       if category == 'Hypothesis testing':
           from quick.application.UserBinManager import UserBinSourceRegistryForHypothesisTests
           ubSourceRegistryCls = UserBinSourceRegistryForHypothesisTests
       elif category == 'Descriptive statistics':
           from quick.application.UserBinManager import UserBinSourceRegistryForDescriptiveStats
           ubSourceRegistryCls = UserBinSourceRegistryForDescriptiveStats
       else:
           raise ShouldNotOccurError()
       return cls._getBinningCategoryTuplesCommon(genome, trackName1, trackName2, ubSourceRegistryCls)

    @classmethod
    def getBinningCategoryTuplesForExtraction(cls, genome, trackName1, trackName2=None):
        from quick.application.UserBinManager import UserBinSourceRegistryForExtraction
        return cls._getBinningCategoryTuplesCommon(genome, trackName1, trackName2, UserBinSourceRegistryForExtraction)

    @staticmethod
    def _getUserBinSource(regSpec, binSpec, genome, trackName1=None, trackName2=None):
        from quick.application.UserBinManager import UserBinSourceRegistry
        ubSourceRegistry = UserBinSourceRegistry(genome, [trackName1, trackName2])
        return ubSourceRegistry.getUserBinSource(regSpec, binSpec)

    @staticmethod
    def _validateRegAndBinSpec(regSpec, binSpec, genome, trackNames):
        from quick.application.UserBinManager import UserBinSourceRegistry
        ubSourceRegistry = UserBinSourceRegistry(genome, trackNames)
        return ubSourceRegistry.validateRegAndBinSpec(regSpec, binSpec)

    @staticmethod
    def _revEngBatchLine(trackName1, trackName2, trackNameIntensity, analysisDef, regSpec, binSpec, genome, manualSeed=None):
        #GalaxyInterface.cleanUpTrackName(trackName1)
        #GalaxyInterface.cleanUpTrackName(trackName2)
        cleanedTrackName1, cleanedTrackName2, cleanedtrackNameIntensity = GalaxyInterface._cleanUpTracks([trackName1, trackName2, trackNameIntensity], genome, realPreProc=False)
        if trackNameIntensity not in [None,'',[],()]:
            tniChoice = '[trackNameIntensity=%s]' % '^'.join([quote(x,safe='') for x in trackNameIntensity])
            analysisDef = analysisDef.replace('->', tniChoice+' ->')
        from gold.description.RunDescription import RunDescription
        return RunDescription.getRevEngBatchLine(trackName1, trackName2, cleanedTrackName1, cleanedTrackName2, \
                                                 analysisDef, regSpec, binSpec, genome, manualSeed)

    @staticmethod
    def cleanUpTrackName(trackName):
        if trackName is not None:
            for i in range(len(trackName)):
                trackName[i] = trackName[i].replace(GalaxyInterface.ALL_SUBTYPES_TEXT,'')
            while len(trackName)>0 and trackName[-1] == '':
                del trackName[-1]

    @staticmethod
    def _viewResults(resultList, galaxyFn):
        if DebugConfig.USE_PROFILING:
            from gold.util.Profiler import Profiler

            profiler = Profiler()
            profiler.run('GalaxyInterface._viewResultsCore(resultList, galaxyFn)', globals(), locals())

            print str(HtmlCore().styleInfoBegin(styleClass='debug'))
            profiler.printStats()
            if DebugConfig.USE_CALLGRAPH:
                profiler.printLinkToCallGraph(['profile_handleRunResults'], galaxyFn)
            print str(HtmlCore().styleInfoEnd())
        else:
            GalaxyInterface._viewResultsCore(resultList, galaxyFn)

    @staticmethod
    def _viewResultsCore(resultList, galaxyFn):
        if galaxyFn is not None:
            from gold.result.ResultsViewer import ResultsViewerCollection
            rvColl = ResultsViewerCollection(resultList, galaxyFn)
            rvColl.storePickledResults()
            print rvColl
        else:
            print 'Only printing plain python representations, due to lack of galaxyFn:'
            print resultList

    @staticmethod
    def getIllustrationRelURL(analysisDef):
        fn = AnalysisDefHandler(unquote(analysisDef)).getIllustrationFn()
        if fn != None:
            return os.sep.join([STATIC_REL_PATH, 'images', 'illustrations',fn])
        else:
            return None

    @staticmethod
    def getHtmlBeginForRuns(galaxyFn):
        extraJavaScriptCode = '''
var done = false;
var job = { filename: "%(file)s", pid: %(pid)d };

var dead = document.cookie.indexOf("dead=" + job.pid) >= 0 ? true : false;

function check_job() {
    if (!done) {
        if (!dead) {
            $.getJSON("%(prefix)s/hyper/check_job", job, function (status) {
                    if (!status.running)
                        document.cookie = "dead=" + job.pid;
                    location.reload(true);
                }
            );
        } else {
            alert("This job did not finish successfully: " + job.filename);
        }
    }
}

function toggle(id) {
    $("#" + id).toggle();
    return false;
}

function toggleDebug() {
    $(".debug").toggle();
    return false;
}

function toggleInfo() {
    $(".infomessagesmall").toggle();
    return false;
}

setTimeout("if (!done) check_job();", 3000);
''' % {'file': galaxyFn, 'pid': os.getpid(), 'prefix': URL_PREFIX }
        return str(HtmlCore().begin(extraJavaScriptCode=extraJavaScriptCode, \
                                    extraCssFns=['hb_base.css']))

    @staticmethod
    def getHtmlForToggles(withRunDescription=True):
        core = HtmlCore()
        if withRunDescription:
            innerCore = HtmlCore()
            innerCore.styleInfoBegin(style='text-align:right')

            innerCore.styleInfoBegin(styleClass='run_description_link', inline=True)
            innerCore.toggle('Inspect parameters of the analysis', styleId='run_description', otherAnchor='debug')
            innerCore.styleInfoEnd(inline=True)

            innerCore.toggle('Toggle debug', styleClass='debug', withDivider=True)

            innerCore.styleInfoEnd()

            core.paragraph(str(innerCore))
        else:
            core.styleInfoBegin(style='text-align:right')
            core.toggle('Toggle debug', styleClass='debug')
            core.styleInfoEnd()
        return str(core)

    @staticmethod
    def getHtmlEndForRuns():
        core = HtmlCore()
        core.script('done = true;')
        core.hideToggle(styleClass='debug')
        core.hideToggle(styleClass='explanation')
        core.hideToggle(styleId='run_description')
        core.end()
        return str(core)

    @staticmethod
    def getHbFunctionOutputBegin(galaxyFn, withDebug=True):
        html = GalaxyInterface.getHtmlBeginForRuns(galaxyFn) + os.linesep
        html += GalaxyInterface.getHtmlForToggles(withRunDescription=False) + os.linesep

        if withDebug:
            html += str(HtmlCore().styleInfoBegin(styleClass='debug'))

        return html

    @staticmethod
    def getHbFunctionOutputEnd(infoMsg, withDebug=True):
        core = HtmlCore()

        if withDebug:
            core.styleInfoEnd()

        core.paragraph('This history element contains pre-processed track data.')
        core.paragraph(infoMsg)
        core.paragraph('This custom track can be analyzed by selecting this history element as one of the input tracks of an analysis.')
        core.end()

        return str(core) + os.linesep + GalaxyInterface.getHtmlEndForRuns()

    @staticmethod
    def getDemoAnalysisIntro(demoID):
        core = HtmlCore()
        core.styleInfoBegin(styleClass='infomessagesmall')
        if demoID == 'H3K27me3 vs SINE':
            core.paragraph('''
                This demo shows hypothesis testing using the Genomic HyperBrowser. The analysis is part of an
                analysis of the relation between H3K27me3 histone modifications and SINE repeats,
                as presented in the main article describing our system (a link to the corresponding
                section of the article will be provided when the article is published).''')
            core.paragraph('''
                H3K27me3 histone modifications and SINE repeats are selected as the two tracks of interest.
                When clicking on "Start analysis", the significance of the observed overlap between H3K27me3
                and SINE will be calculated using a Monte Carlo-based approach.''')
            core.paragraph('''
                The alternative hypothesis and the null model assumptions can be changed under "Options".
                We have pre-selected 200 Monte Carlo iterations to make the demo run faster, but for a real
                analysis a higher number, like 20000, should be used. The analysis will be performed in bins
                of size 5 million base pairs in chromosome 17 of mouse (mm8), excluding the 3 million first base pairs, which are centromeric.''')
        elif demoID == 'Gene Coverage':
            core.paragraph('''This demo shows a very simple example of using the Genomic HyperBrowser: finding out how much of the genome is covered by genes.
                           This is done by simply selecting a gene track, and selecting count as analysis.
                           ''')
            core.paragraph('''Note that even this very simple question reveals a complication: there is no unanimous definition of exactly what constitute genes.
                When selecting a gene track, one therefore has to select which gene source to use.
                In the demo the Consensus Coding Sequence (CCDS) has been used.
                ''')
            core.paragraph('''We here also select "Cytobands" in the "Region and scale"-box, in order to do
                           a local analysis of the coverage of genes in all cytobands.
                           ''')
        elif demoID == 'H3K4me3 vs T-cell expression':
            core.paragraph('''This demo shows an analysis that involves the use of ad hoc created tracks.
                The second track consists of segments 1kb downstream of TSS, where each segment is marked
                with the expression of the corresponding gene in a T-cell microarray experiment.
                This second track would then typically be created ac hoc by extracting an expression track,
                consisting of gene regions with an attached expression value, to history
                This track would then be expanding 1kb flanks from the TSS, by using the "Extract BED segments" tool.
                The resulting track could then be selected as a track from history. See the screencast for more details.
                ''')
            core.paragraph('''The question raised is whether there is a connection between the expression mark associated
                           with a 1kb segment and the number of nucleosomes with H3K4me3 histone modifications falling inside it.
                           ''')
            core.paragraph('''
                The analysis is part of an analysis of the relation between histone modifications and gene expression,
                as presented in the main article describing our system (a link to the corresponding
                section of the article will be provided when the article is published).
                ''')
        elif demoID == 'MLV vs Expanded FirstEF promoters':
            core.paragraph('''This demo shows local analysis using the Genomic HyperBrowser.
                The question raised is whether virus (MLV) integrates more into FirstEF promoters (including 2kb flanks) than expected by chance.
                This analysis is performed in 30 Mbp bins throughout the genome, and the local variation of the virus-promoter relation can thus be investigated.
                ''')
            core.paragraph('''This analysis is included in the main article describing our system (a link to the corresponding
                section of the article will be provided when the article is published).
               ''')
        elif demoID == 'Exon boundaries vs melting fork probs':
            core.paragraph('''
                This demo shows how to take confounding tracks into account when doing analyses in the HyperBrowser.
                The question raised is whether exon boundaries (left sides) coincide with positions of high probability of melting bubble formation.
                ''')
            core.paragraph('''
                The main point with the analysis is the possibly confounding effect GC content plays on a study of the direct relation between exons and melting bubbles.
                This is because both exons and melting bubbles are by themselves related to GC content
                (GC content is generally higher in exons, melting temperature is higher with G and C than with A or T).
                To see whether exons and melting bubbles (melting fork probabilities) coincide more than expected given their common dependence on GC content,
                we sample exons in the null model based on dependency between exons and GC content.
                This is done by selecting ".. randomize positions by intensity" as null model,
                and selecting an intensity track of exon probability given GC content.
                The screencast of this example will show how such intensity tracks can be created.
                ''')
            core.paragraph('''
                The analysis is part of an analysis of the relation between histone modifications and gene expression,
                as presented in the main article describing our system (a link to the corresponding
                section of the article will be provided when the article is published).
                As this analysis is somewhat intricate, it is easier to understand after consulting the discussion of confounder track handling in the article.
                ''')
        #elif demoID == '': #sample regulome
        #    core.paragraph('''
        #                   ''')
        else:
            core.paragraph("Intro for " + demoID)
        core.styleInfoEnd()
        return str(core)

    @staticmethod
    def _getDemoResultsIntro(demoID):
        core = HtmlCore()
        core.styleInfoBegin(styleClass='infomessagesmall')
        if demoID == 'H3K27me3 vs SINE':
            core.paragraph('''
                This page shows the result of the H3K27me3 vs SINE repeats-demo, which shows how to do hypothesis
                testing in the Genomic HyperBrowser. The analysis is part of an analysis of the relation between
                H3K27me3 histone modifications and SINE repeats, as presented in the main article describing our
                system (a link to the corresponding section of the article will be provided when the article is
                published).''')
            core.paragraph('''
                The main point with this case, as discussed in the article, is how the computed p-value will
                depend on the selected null model. Depending on the selected null model, you will get from zero
                to several significant bins when asking whether H3K27me3-segments and SINE repeats overlap more
                than expected by chance at the base pair level. These varying results for different null models make up
                a table in the article summarizing the results for this case.''')
            core.paragraph('''
                Note that different tests are used across null models, with some null models allowing a quick
                parametric solution (based on the binomial distribution), while others require Monte Carlo-based
                calculation of significance.''')
        elif demoID == 'Gene Coverage':
            core.paragraph('''
                This page shows the result of the Gene Coverage demo. According to the CCDS gene definition, 25.97% of the genome consists of genes.
                By looking at "Table: values per bin", one can also look at coverage proportion for each of the cytobands.
                ''')
            core.paragraph('''
                The "Assembly gap coverage" row shows the proportion of base pairs that are missing (i.e. not sequenced) in the
                genome assembly used. If this value is high for a particular bin (or for the global analysis), you should be sceptical about
                your results. Most assembly gaps are centromeres or other heterochromatic regions.
                ''')
        elif demoID == 'H3K4me3 vs T-cell expression':
            core.paragraph('''
                This page shows the result of the demo of H3K4me3 vs gene expression.
                The analysis is part of an analysis of the relation between histone modifications and gene expression,
                as presented in the main article describing our system (a link to the corresponding
                section of the article will be provided when the article is published).
                ''')
            core.paragraph('''
                Figure 2 of the article mentioned above shows the correlation between gene expression and histone modification count inside TSS flanks
                for 21 histone modifications and 4 variants of TSS flanks. The value of the test statistic for this demo (0.23) thus makes up one out of 84 data points in Figure 2.
                ''')
        elif demoID == 'MLV vs Expanded FirstEF promoters':
            core.paragraph('''
                This page shows the result of the demo of MLV vs Expanded FirstEF promoters.
                The analysis is included in the main article describing our system (a link to the corresponding
                section of the article will be provided when the article is published).
                ''')
            core.paragraph('''
                The focus of this analysis is the local variation. This can be inspected by clicking on results for the test in "each bin separately".
                It can also be inspected visually by clicking "See full details" and clicking "Plot: values per bin"-"Figure" for FDR-adjusted p-values.
                ''')
            core.paragraph('''
                The local results can be exported to the history by clicking "As track in history"-"Load" in the same table. FDR-adjusted p-values can then
                be visualized in the UCSC Genome Browser by clicking on the name of the new history element, and then clicking "display at UCSC main".
                ''')

        elif demoID == 'Exon boundaries vs melting fork probs':
            core.paragraph('''
                This page shows the result of the demo of Exon boundaries vs melting fork probabilities.
                The analysis is included in the main article describing our system (a link to the corresponding
                section of the article will be provided when the article is published).
                ''')
            core.paragraph('''
                The question raised is whether exon boundaries (left sides) coincide with positions of high probability of melting bubble formation,
                more than expected by chance, but given their common dependency on GC content.
                Although the relation between exons and melting bubbles is clearly significant when not taking GC content into consideration (see discussion in article),
                the relation here usually turns out significant in 1 out of 17 bins at 10% FDR.
                By clicking on "A collection of FDR-corrected p-values per bin" one can further see values for each chromosome,
                and see that the only chromsome with signifint relation was chromosome M, the mithocondrial DNA.
                This suggest that the relation between exons and melting temperature may just be a reflection of their common dependency with GC content.
                ''')
        else:
            core.paragraph("Results page intro for " + demoID)
        core.styleInfoEnd()
        return str(core)
