import os

from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.extra.TrackIntersection import GeneIntersection
from quick.extra.tfbs.TfInfo import TfInfo


class GeneTargetsOfRegions(object):
    @staticmethod
    def findGeneTargets(genome, regionsTn, upFlankSize, downFlankSize, galaxyFn):
        assert genome in ['hg18','hg19','mm9']
        #tfTrackNameMappings = TfInfo.getTfTrackNameMappings(genome)
        #tfTrackName = tfTrackNameMappings[tfSource] + [selectedTF]

        geneIntersection = GeneIntersection(genome, 'Ensembl', regionsTn, galaxyFn)
        geneIntersection.expandReferenceTrack(upFlankSize, downFlankSize)
        expansionStr = ' flanked' if not (upFlankSize == downFlankSize == 0) else ''
        #print '<p>There are %i Ensemble genes being targets of your selected TF (%s), based on intersecting TF target positions with%s %sgene regions.</p>' % (geneIntersection.getNumberOfIntersectedBins(), selectedTF, expansionStr, 'Ensembl')
        print '<p>There are %i Ensemble genes being targets of your selected regions, based on intersecting your supplied regions with%s %sgene regions.</p>' % (geneIntersection.getNumberOfIntersectedBins(), expansionStr, 'Ensembl')

        idFileNamer = geneIntersection.getGeneIdStaticFileWithContent()
        print '<p>', idFileNamer.getLink('Download list'), ' of all Ensemble IDs with 1 or more hits.</p>'

        regFileNamer = geneIntersection.getIntersectedRegionsStaticFileWithContent()
        print '<p>', regFileNamer.getLink('Download bed-file'), ' of all Ensembl gene regions with 1 or more hits.</p>'

        targetBins = geneIntersection.getIntersectedReferenceBins()
        res = geneIntersection.getIntersectionResult()
        resDictKey = geneIntersection.getUniqueResDictKey()
        setOfNumOccurrences = set([res[bin][resDictKey] for bin in targetBins])

        byNumOccurrencesStaticFile = GalaxyRunSpecificFile(['genes_by_num_occurrences.html'], galaxyFn)
        f = byNumOccurrencesStaticFile.getFile()
        for numOccurrences in reversed(sorted(setOfNumOccurrences)):
            f.write('Gene regions having %i occurrences:<br>' % numOccurrences + '<br>' + os.linesep)
            f.write(', '.join([ '<a href=http://www.ensembl.org/Homo_sapiens/Gene/Summary?g='+str(bin.val).split('|')[0]+'>'+str(bin.val).split('|')[0]+'</a>' for bin in targetBins if res[bin][resDictKey]==numOccurrences]) + '<br><br>' + os.linesep)
        f.close()

        print '</p>Inspect list of all intersected genes (by ID), ', byNumOccurrencesStaticFile.getLink('ordered by number of occurrences') + ' inside, and with links to gene descriptions.<br>'

class GeneTargetsOfTF(GeneTargetsOfRegions):
    @staticmethod
    def findGeneTargets(genome, tfSource, selectedTF, upFlankSize, downFlankSize, galaxyFn):
        tfTrackNameMappings = TfInfo.getTfTrackNameMappings(genome)
        tfTrackName = tfTrackNameMappings[tfSource] + [selectedTF]
        GeneTargetsOfRegions.findGeneTargets(genome, tfTrackName, upFlankSize, downFlankSize, galaxyFn)

    #@staticmethod
    #def findGeneTargets(genome, tfSource, selectedTF, upFlankSize, downFlankSize, galaxyFn):
    #    assert genome == 'hg18'
    #    tfTrackNameMappings = TfInfo.getTfTrackNameMappings(genome)
    #    tfTrackName = tfTrackNameMappings[tfSource] + [selectedTF]
    #
    #    geneIntersection = GeneIntersection(genome, 'Ensembl', tfTrackName, galaxyFn)
    #    geneIntersection.expandReferenceTrack(upFlankSize, downFlankSize)
    #    expansionStr = ' flanked' if not (upFlankSize == downFlankSize == 0) else ''
    #    print '<p>There are %i Ensemble genes being targets of your selected TF (%s), based on intersecting TF target positions with%s %sgene regions.</p>' % (geneIntersection.getNumberOfIntersectedBins(), selectedTF, expansionStr, 'Ensembl')
    #
    #    idFileNamer = geneIntersection.getGeneIdStaticFileWithContent()
    #    print '<p>', idFileNamer.getLink('Download list'), ' of all Ensemble IDs with 1 or more hits.</p>'
    #
    #    regFileNamer = geneIntersection.getIntersectedRegionsStaticFileWithContent()
    #    print '<p>', regFileNamer.getLink('Download bed-file'), ' of all Ensembl gene regions with 1 or more hits.</p>'
    #
    #    targetBins = geneIntersection.getIntersectedReferenceBins()
    #    res = geneIntersection.getIntersectionResult()
    #    resDictKey = geneIntersection.getUniqueResDictKey()
    #    setOfNumOccurrences = set([res[bin][resDictKey] for bin in targetBins])
    #
    #    byNumOccurrencesStaticFile = GalaxyRunSpecificFile(['genes_by_num_occurrences.html'], galaxyFn)
    #    f = byNumOccurrencesStaticFile.getFile()
    #    for numOccurrences in reversed(sorted(setOfNumOccurrences)):
    #        f.write('Gene regions having %i TF occurrences:<br>' % numOccurrences + '<br>' + os.linesep)
    #        f.write(', '.join([ '<a href=http://www.ensembl.org/Homo_sapiens/Gene/Summary?g='+str(bin.val)+'>'+str(bin.val)+'</a>' for bin in targetBins if res[bin][resDictKey]==numOccurrences]) + '<br><br>' + os.linesep)
    #    f.close()
    #
    #    print '</p>Inspect list of all intersected genes (by ID), ', byNumOccurrencesStaticFile.getLink('ordered by number of TF occurrences') + ' inside, and with links to gene descriptions.<br>'
    #
    #@staticmethod
    #def findGeneTargets(genome, tfSource, selectedTF, upFlankSize, downFlankSize, galaxyFn):
    #    assert genome == 'hg18'
    #    galaxyId = extractIdFromGalaxyFn(galaxyFn)
    #    externalId = galaxyId
    #    uniqueWebPath = getUniqueWebPath(galaxyId)
    #
    #    #if tfSource == 'UCSC tfbs conserved':
    #    #    tfTrackName = ['Gene regulation','TFBS','UCSC prediction track']
    #    #else:
    #    #    raise
    #    tfTrackNameMappings = TfInfo.getTfTrackNameMappings(genome)
    #    tfTrackName = tfTrackNameMappings[tfSource]
    #
    #    #assert upFlankSize == downFlankSize == 0 #Should instead extend regions to include flanks
    #
    #    analysisDef = 'Counts: The number of track1-points'+\
    #                  '[tf1:=SegmentToStartPointFormatConverter:]'+\
    #                  '-> CountPointStat'
    #
    #    geneRegsTrackName = GenomeInfo.getStdGeneRegsTn(genome)
    #    origGeneRegsFn = getOrigFn(genome, geneRegsTrackName, '.category.bed')
    #    if not (upFlankSize == downFlankSize == 0):
    #        flankedGeneRegsTempFn  = uniqueWebPath + os.sep + 'flankedGeneRegs.category.bed'
    #        GalaxyInterface.expandBedSegments(origGeneRegsFn, flankedGeneRegsTempFn, genome, upFlankSize, downFlankSize)
    #        #print 'flankedGeneRegsTempFn: ',flankedGeneRegsTempFn
    #        regSpec, binSpec = 'file', flankedGeneRegsTempFn
    #    else:
    #        regSpec, binSpec = 'file', origGeneRegsFn
    #
    #    trackName1 = tfTrackName
    #    trackName2 = None
    #
    #    print '<div class="debug">'
    #    userBinSource, fullRunArgs = GalaxyInterface._prepareRun(trackName1, trackName2, analysisDef, regSpec, binSpec, genome)
    #    res = AnalysisDefJob(analysisDef, trackName1, trackName2, userBinSource, **fullRunArgs).run()
    #    #print res
    #    print '</div>'
    #
    #    resDictKeys = res.getResDictKeys()
    #    assert len(resDictKeys)==1, resDictKeys
    #    resDictKey = resDictKeys[0]
    #    targetBins = [bin for bin in res.keys() if res[bin][resDictKey]>0]
    #    #print '%i Ensemble genes being targets of TF %s:<br>' % (len(targetBins), selectedTF)
    #    #print ','.join([str(bin) for bin in targetBins]),'<br>'
    #    #print ', '.join([str(bin.val) for bin in targetBins])
    #
    #    #alt:
    #    print '%i Ensemble genes being targets of TF %s.<br>' % (len(targetBins), selectedTF)
    #
    #    from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
    #    idFileNamer = GalaxyRunSpecificFile(['allGeneIds'],'txt',galaxyFn)
    #    #idFile = idFileNamer.getFile()
    #    #idFile.write(', '.join([str(bin.val) for bin in targetBins if res[bin][resDictKey]>0]) + os.sep)
    #    #idFile.close()
    #    idFileNamer.writeTextToFile(', '.join([str(bin.val) for bin in targetBins if res[bin][resDictKey]>0]) + os.sep)
    #    #print '<a href=%s>Download list</a> of all ensemble IDs with 1 or more hits' % idFileNamer.getURL()
    #    print idFileNamer.getLink('Download list'), ' of all ensemble IDs with 1 or more hits.'
    #
    #    setOfNumOccurrences = set([res[bin][resDictKey] for bin in targetBins])
    #
    #    for numOccurrences in reversed(sorted(setOfNumOccurrences)):
    #        print 'Gene regions having %i TF occurrences:<br>' % numOccurrences
    #        print ', '.join([str(bin.val) for bin in targetBins if res[bin][resDictKey]==numOccurrences])
    #        print '<br><br>'
