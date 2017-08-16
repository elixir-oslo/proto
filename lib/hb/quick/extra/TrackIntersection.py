import os
from collections import Counter

from gold.util.CommonFunctions import getOrigFn
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.GalaxyInterface import GalaxyInterface
from quick.util.GenomeInfo import GenomeInfo

'''
Created on ???
@author: Geir-Kjetil Sandve???
Last update: Antonio Mora; Feb 27, 2015
'''

class BasicTrackIntersection(object):
    def __init__(self, genome, referenceTrackFn, queryTrack):
        self._genome = genome
        self._referenceTrackFn = referenceTrackFn
        self._queryTrackName = queryTrack
        self._intersectedReferenceBins = None
        self._result = None

    def getNumberOfIntersectedBins(self):
        return len(self.getIntersectedReferenceBins() )

    def run(self):
        assert self._referenceTrackFn is not None

        if (isinstance(self._referenceTrackFn, basestring)):
            regSpec, binSpec = 'file', self._referenceTrackFn
        elif (type(self._referenceTrackFn)==list):
            regSpec, binSpec = 'track', ':'.join(self._referenceTrackFn)

        trackName1 = self._queryTrackName
        trackName2 = None

        from gold.description.TrackInfo import TrackInfo

        formatName = TrackInfo(self._genome, trackName1).trackFormatName
#        formatConv = ''
#        if 'segments' in formatName:
#            formatConv = '[tf1:=SegmentToStartPointFormatConverter:]'

#        analysisDef = formatConv + '-> CountPointStat'

        from gold.statistic.CountStat import CountStat
        #analysisDef = '-> CountSegmentStat' if 'segments' in formatName else '-> CountPointStat'
        analysisDef = CountStat

        # print '_referenceTrackFn' + str(self._referenceTrackFn)
        # print '_queryTrackName' + str(self._queryTrackName)
        #
        # print 'trackName1' + str(trackName1)
        # print 'trackName2' + str(trackName2)




        #analysisDef = CountStat

        #print '<div class="debug">'
        #trackName1, trackName2, analysisDef = GalaxyInterface._cleanUpAnalysisDef(trackName1, trackName2, analysisDef)
        #trackName1, trackName2 = GalaxyInterface._cleanUpTracks([trackName1, trackName2], genome, realPreProc=True)
        #
        #userBinSource, fullRunArgs = GalaxyInterface._prepareRun(trackName1, trackName2, analysisDef, regSpec, binSpec, self._genome)
        #res = AnalysisDefJob(analysisDef, trackName1, trackName2, userBinSource, **fullRunArgs).run()


        #if it is not a gSuite
        #res = GalaxyInterface.runManual([trackName1, trackName2], analysisDef, regSpec, binSpec, self._genome, printResults=False, printHtmlWarningMsgs=False)

        #if gSuite
        from gold.application.HBAPI import PlainTrack
        from gold.application.HBAPI import doAnalysis
        from gold.description.AnalysisDefHandler import AnalysisSpec

        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, self._genome)
        res = doAnalysis(AnalysisSpec(analysisDef), analysisBins, [PlainTrack(self._queryTrackName)])
        #print 'ccc'
        #resultDict = res.getGlobalResult()


        resDictKeys = res.getResDictKeys()



        if len(resDictKeys) == 1:
        #assert len(resDictKeys)==1, resDictKeys
            resDictKey = resDictKeys[0]
            targetBins = [bin for bin in res.keys() if res[bin][resDictKey]>0]
            self._result = res
            self._intersectedReferenceBins = targetBins

    def getIntersectedReferenceBins(self):
        if self._intersectedReferenceBins is None:
            self.run()
        return self._intersectedReferenceBins

    def getIntersectionResult(self):
        if self._result is None:
            self.run()
        return self._result

    def getUniqueResDictKey(self):
        resDictKeys = self._result.getResDictKeys()
        assert len(resDictKeys)==1, resDictKeys
        return resDictKeys[0]

class TrackIntersection(BasicTrackIntersection):
    def __init__(self, genome, referenceTrackFn, queryTrack, galaxyFn, subDirId=None):
        BasicTrackIntersection.__init__(self, genome, referenceTrackFn, queryTrack)
        self._galaxyFn = galaxyFn
        self._subDirId = subDirId
        pass

    #def setReferenceTrackFn(self, referenceTrack):
    #    self._referenceTrackFn = referenceTrackFn

    def _getFileId(self, fileName):
        if self._subDirId:
            return [self._subDirId, fileName]
        else:
            return [fileName]

    def expandReferenceTrack(self, upFlankSize, downFlankSize):
        if not (upFlankSize == downFlankSize == 0):
            self._intersectedReferenceBins = None

            flankedGeneRegsTempFn  = GalaxyRunSpecificFile(self._getFileId('flankedGeneRegs.category.bed'), self._galaxyFn).getDiskPath()
            GalaxyInterface.expandBedSegments(self._referenceTrackFn, flankedGeneRegsTempFn, self._genome, upFlankSize, downFlankSize)
            self._referenceTrackFn = flankedGeneRegsTempFn
            #print 'flankedGeneRegsTempFn: ',flankedGeneRegsTempFn

    def getIntersectedRegionsStaticFileWithContent(self):
        intersectedRegs = self.getIntersectedReferenceBins()
        staticFile = GalaxyRunSpecificFile(self._getFileId('intersected_regions.bed'), self._galaxyFn)
        self.writeRegionListToBedFile(intersectedRegs, staticFile.getDiskPath() )
        return staticFile

    @staticmethod
    def writeRegionListToBedFile(regList, fn):
        from quick.util.CommonFunctions import ensurePathExists
        ensurePathExists(fn)
        f = open(fn, 'w')

        if regList!=None:
            for reg in regList:
                f.write( '\t'.join([reg.chr, str(reg.start), str(reg.end)]) + os.linesep )
        f.close()

    @staticmethod
    def prepareDataForPlot(genome, targetBins):
        chrs = []; dataY = [] # froms = []; tos = []
        for i in range(0,len(targetBins)):
            tmp = str(targetBins[i]).split(":")
            chrs = chrs + [tmp[0]]
            #tmp2 = str(tmp[1]).split("-")
            #froms = froms + [tmp2[0]]
        c = Counter(chrs)
        if genome == 'hg19':
            chrNames = ['chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chr20','chr21','chr22','chrX','chrY']        
        if genome == 'mm9':
            chrNames = ['chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chrX','chrY']        
        for i in chrNames:
            dataY = dataY + [c[i]]
        return dataY #[[None if x==0 else x for x in dataY]]

    @staticmethod
    def getFileFromTargetBins(targetBins, galaxyFn, subDirId=None):
        staticFile = GalaxyRunSpecificFile(([subDirId] if subDirId else []) + ['intersected_regions.bed'], galaxyFn)
        fn = staticFile.getDiskPath()
        from quick.util.CommonFunctions import ensurePathExists
        ensurePathExists(fn)
        f = open(fn, 'w')
        for region in targetBins:
            tmp = region[0].split(':')
            chrom = tmp[0]
            tmp2 = tmp[1].split('-')
            start = tmp2[0]
            end = tmp2[1]
            tfs = region[1]
            f.write( '\t'.join([chrom, str(start), str(end), tfs]) + os.linesep )
        f.close()
        return staticFile

    @staticmethod
    def getOccupancySummaryFile(summaryTable, galaxyFn, subDirId=None):
        staticFile = GalaxyRunSpecificFile(([subDirId] if subDirId else []) + ['intersected_regions.bed'], galaxyFn)
        fn = staticFile.getDiskPath()
        from quick.util.CommonFunctions import ensurePathExists
        ensurePathExists(fn)
        f = open(fn, 'w')
        line = ['#TF Motif', 'Motif count in region', 'Percentage(motif in full region)', 'Percentage(motif in co-bound regions)']
        f.write('\t'.join(line) + os.linesep)
        for region in summaryTable:
            line = [str(region[0]),str(region[1]),str(region[2]),str(region[3])]
            f.write('\t'.join(line) + os.linesep)
        f.close()
        return staticFile

class GeneIntersection(TrackIntersection):
    def __init__(self, genome, geneSource, queryTrack, galaxyFn):
        assert geneSource == 'Ensembl'
        geneRegsTrackName = GenomeInfo.getStdGeneRegsTn(genome)
        geneRegsTrackFn = getOrigFn(genome, geneRegsTrackName, '.category.bed')
        TrackIntersection.__init__(self, genome, geneRegsTrackFn, queryTrack, galaxyFn)

    def getGeneIdStaticFileWithContent(self):
        targetBins = self.getIntersectedReferenceBins()
        idFileNamer = GalaxyRunSpecificFile(self._getFileId('allGeneIds.txt'), self._galaxyFn)
        idFileNamer.writeTextToFile(os.linesep.join([str(bin.val).split('|')[0] for bin in targetBins]) + os.linesep)
        return idFileNamer
