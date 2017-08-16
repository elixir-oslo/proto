from quick.extra.TrackExtractor import TrackExtractor
from quick.application.UserBinSource import UserBinSource

if __name__ == "__main__":
    #trackNames = [['genes','refseq'], ['melting','discr','3mers'], ['sequence']]
    #regions = UserBinSource('chr1:800000-900000','50000')
    #TrackExtractor.extractManyToRegionDirs(trackNames, regions, '/usit/titan/u1/sveinugu/testdata/local/regions/', False)
    #TrackExtractor.extractManyToOneDir(trackNames, regions, '/usit/titan/u1/sveinugu/testdata/local/one/', False)
    #TrackExtractor.extractManyToRegionDirs(trackNames, regions, '/usit/titan/u1/sveinugu/testdata/global/regions/', True)
    #TrackExtractor.extractManyToOneDir(trackNames, regions, '/usit/titan/u1/sveinugu/testdata/global/one/', True)

    #trackNames = [['bs','bothDBs'], ['melting','discr','3mers'],['curvature'],['repeats'],['nucleosome'],['DNaseHS','clusters'],['acetylation','H2AK5ac'],['cpg_island'],['sequence']]
    #regions = UserBinSource('file','/usit/titan/u1/geirksa/_data/Upstreams2kbWith5bs.bed')
    #TrackExtractor.extractManyToRegionDirs(trackNames, regions, '/usit/titan/u1/geirksa/_output/allWith5bs/', False)
    ##TrackExtractor.extractManyToRegionDirs(trackNames, regions, '/usit/titan/u1/geirksa/_output/wenjie7OctGlobal/', True)
    #
    #trackNames = [['bs','oRegAnno','REST'], ['melting','discr','3mers'],['curvature'],['repeats'],['nucleosome'],['DNaseHS','clusters'],['acetylation','H2AK5ac'],['cpg_island'],['sequence']]
    #regions = UserBinSource('chr1:1-30000000','30000')
    #TrackExtractor.extractManyToRegionDirs(trackNames, regions, '/usit/titan/u1/geirksa/_output/REST_chr1_30Mb/', False)
    
    #trackNames = [['sequence'],['bs','bothDBs']]
    #regions = UserBinSource('file','/usit/titan/u1/geirksa/_data/IRF_200bpWins.bed')
    #TrackExtractor.extractManyToOneDir(trackNames, regions, '/usit/titan/u1/geirksa/_allergi/IRF200bpOneDS/',False)
    
    #trackNames = [['sequence']]
    #regions = UserBinSource('file','/usit/titan/u1/geirksa/_data/2kbUpstreamsNoIRFNoGenes.bed')
    #TrackExtractor.extractManyToOneDir(trackNames, regions, '/usit/titan/u1/geirksa/_allergi/IRFNegData/',False)
    
    #trackNames = [['bs','ucsc'], ['bs','cisred'],['bs','bothDBs']]
    #regions = UserBinSource('file','/usit/titan/u1/geirksa/_data/IRF_200bpWins.bed')
    #TrackExtractor.extractManyToOneDir(trackNames, regions, '/usit/titan/u1/geirksa/_allergi/IRF200bpStaticPredsOneDs/',True,True)
    #TrackExtractor.extractManyToRegionDirs(trackNames, regions, '/usit/titan/u1/geirksa/_allergi/IRF200bpStaticPredsManyDs/',True,True)

    #trackNames = [['genes','refseq']]
    #regions = UserBinSource('file','/usit/titan/u1/geirksa/_data/ets1.bed')
    #TrackExtractor.extractManyToOneDir(trackNames, regions, '/usit/titan/u1/geirksa/_allergi/ETS1/',True,True)
    
    #trackName = ['Phenotype and Disease Associations','HPV specific','1kb up USCS exons']
    #regions = UserBinSource('file','/data1/rrresearch/standardizedTracks/hg18/Phenotype and Disease Associations/Virus integration/HPV/.hpv.bed')
    #TrackExtractor.extractOneTrackManyRegsToOneFile(trackName, regions, '/usit/titan/u1/geirksa/_output/ExonsCloseToHPV.bed', True, True)
    
    trackName = ['Genes and gene subsets', 'Genes', 'CCDS']
    regions = UserBinSource('file','/usit/invitro/hyperbrowser/standardizedTracks/hg18/Phenotype and disease associations/Assorted experiments/Virus integration, Derse et al. (2007)/MLV/MLV.bed')
    TrackExtractor.extractOneTrackManyToRegionFilesInOneZipFile(trackName, regions, '/norstore_osl/hyperbrowser/nosync/nobackup/test/HPV_CCDS.zip', globalCoords=True, asOriginal=True, allowOverlaps=False, ignoreEmpty=True)
