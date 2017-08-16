def getSupportedFileSuffixesForBinning():
    return ['gtrack', 'bed', 'point.bed', 'category.bed', 'valued.bed', 'wig', \
            'targetcontrol.bedgraph', 'bedgraph', 'gff', 'gff3', 'category.gff', \
            'narrowpeak', 'broadpeak']


def getSupportedFileSuffixesForPointsAndSegments():
    return getSupportedFileSuffixesForBinning()


def getSupportedFileSuffixesForGSuite():
    return getSupportedFileSuffixesForPointsAndSegments() + \
           ['fasta', 'microarray',
            'tsv', 'vcf', 'maf']
# Last three are temporarily added for supporting GSuite repositories via
# manual manipulation


def getSupportedFileSuffixesForFunction():
    return ['hbfunction']


def getSupportedFileSuffixes():
    return getSupportedFileSuffixesForGSuite() + \
           getSupportedFileSuffixesForFunction()


# Defined to stop searching for GTrackGenomeElementSource subtypes online.
def getUnsupportedFileSuffixes():
    return ['bam', 'bai', 'tab', 'tbi', 'bigwig', 'bw', 'bigbed', 'bb', 'fastq', 'fq', \
            'csfasta', 'csqual', 'doc', 'docx', 'xls', 'xlsx', 'gp', 'gappedPeak', 'peaks', \
            'bedcluster', 'bedlogr', 'bedrnaelement', 'bedrrbs', 'cel', 'matrix', \
            'pdf', 'peptidemapping', 'shortfrags', 'spikeins', 'pair', 'txt', \
            'xml', 'svs', 'gz', 'tar', 'z', 'tgz', 'zip']
#            'xml', 'svs', 'maf', 'gz', 'tar', 'z', 'tgz', 'zip']
