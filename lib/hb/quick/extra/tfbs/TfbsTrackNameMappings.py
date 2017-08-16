from collections import OrderedDict
from config.Config import HB_SOURCE_DATA_BASE_DIR
'''
Created on Nov 12, 2014
@author: Antonio Mora
Last update: Antonio Mora; Mar 18, 2015
'''

class TfbsTrackNameMappings:
    @staticmethod
    def getTfbsTrackNameMappings(genome):
        if genome == 'hg18':
            return
        elif genome == 'mm9':
            return OrderedDict([\
            ('Genes --Ensembl',['Genes and gene subsets','Genes','Ensembl']),\
            ('Genes --RefSeq',['Genes and gene subsets','Genes','Refseq']),\
            ('Exons --RefSeq',['Genes and gene subsets','Exons','Refseq']),\
            ('Introns --RefSeq',['Genes and gene subsets','Introns','Refseq']),\
            ('Intergenic --RefSeq',['Genes and gene subsets','Intergenic','Refseq']),\
            ('Super-Enhancers -mESC',['Private','Antonio','ESE14','Enhancers','SuperEnhancers2013WhytePMID23582322']),\
        
            #('E14-DNaseI --UW rep1',['Private','Antonio','DNaseI','wgEncodeUwDnaseEse14129olaME0PkRep1']),\
            #('E14-DNaseI --UW rep2',['Private','Antonio','DNaseI','wgEncodeUwDnaseEse14129olaME0PkRep2']),\
            #('E14-H3K4me1 --LICR',['Private','Antonio','Histone modifications','wgEncodeLicrHistoneEse14H3k04me1ME0129olaStdPk']),\
            #('E14-H3K4me1 --SYDH',['Private','Antonio','Histone modifications','wgEncodeSydhHistEse14H3k04me1StdPk']),\
            #('E14-H3K4me3 --LICR',['Private','Antonio','Histone modifications','wgEncodeLicrHistoneEse14H3k04me3ME0129olaStdPk']),\
            #('E14-H3K4me3 --SYDH',['Private','Antonio','Histone modifications','wgEncodeSydhHistEse14H3k04me3StdPk']),\
            #('E14-H3K9me3 --SYDH',['Private','Antonio','Histone modifications','wgEncodeSydhHistEse14H3k09me3StdPk']),\
            #('E14-H3K36me3 --LICR',['Private','Antonio','Histone modifications','wgEncodeLicrHistoneEse14H3k36me3ME0129olaStdPk']),\
            #('E14-H3K9ac --LICR',['Private','Antonio','Histone modifications','wgEncodeLicrHistoneEse14H3k09acME0129olaStdPk']),\
            #('E14-H3K27ac --LICR',['Private','Antonio','Histone modifications','wgEncodeLicrHistoneEse14H3k27acME0129olaStdPk']),\
            ('FANTOM5 Cage Peak Robust',['Private','Antonio','Promoters','FANTOM5 CAGE Robust'])   
            ])
        elif genome == 'hg19':
            return OrderedDict([\
            ('Genes --Ensembl',['Genes and gene subsets','Genes','Ensembl']),\
            ('Genes --RefSeq',['Genes and gene subsets','Genes','Refseq']),\
            ('Exons --Ensembl',['Genes and gene subsets','Exons','Ensembl exons']),\
            ('Exons --RefSeq',['Genes and gene subsets','Exons','Refseq exons']),\
            ('Introns --Ensembl',['Genes and gene subsets','Introns','Ensembl introns']),\
            ('Introns --RefSeq',['Genes and gene subsets','Introns','Refseq introns']),\
            ('FANTOM5 Robust Promoters',['Private','Antonio','Promoters','FANTOM5 CAGE Robust']),\
            ('SWITCHDB TSS',['Private','Antonio','Promoters','switchDbTss']),\
            #('DNaseHSS Roadmap Epigenomics',['Chromatin','Roadmap Epigenomics','DNaseHS']),\
            ('Vista Enhancers',['Private','Antonio','Enhancers','Vista Enhancers']),\
            ('FANTOM5 Robust Enhancers',['Private','Antonio','Enhancers','FANTOM5 Enhancers Robust']),\
            ('FANTOM5 Ubiquitous Enhancers cell-based',['Private','Antonio','Enhancers','FANTOM5 Ubiquitous Enhancers primary cell based']),\
            ('FANTOM5 Ubiquitous Enhancers anatomy-based',['Private','Antonio','Enhancers','FANTOM5 Ubiquitous Enhancers tissue based'])

            #('FANTOM5 Blood vessel endothelial cell expressed enhancers',['Private','Antonio','FANTOM5 cell-specific enhancers','Blood vessel endothelial cell expressed enhancers']),\
            #('FANTOM5 Cardiac fibroblast expressed enhancers',['Private','Antonio','FANTOM5 cell-specific enhancers','Cardiac fibroblast expressed enhancers']),\
            #('FANTOM5 Cardiac myocyte expressed enhancers',['Private','Antonio','FANTOM5 cell-specific enhancers','Cardiac myocyte expressed enhancers']),\
            #('FANTOM5 Lymphocyte B lineage expressed enhancers',['Private','Antonio','FANTOM5 cell-specific enhancers','Lymphocyte B lineage expressed enhancers']),\
            #('FANTOM5 Neutrophil expressed enhancers',['Private','Antonio','FANTOM5 cell-specific enhancers','Neutrophil expressed enhancers']),\
            #('FANTOM5 T cell expressed enhancers',['Private','Antonio','FANTOM5 cell-specific enhancers','T cell expressed enhancers']),\
            #('FANTOM5 Blood expressed enhancers',['Private','Antonio','FANTOM5 anatomy-specific enhancers','Blood expressed enhancers']),\
            #('FANTOM5 Blood vessel expressed enhancers',['Private','Antonio','FANTOM5 anatomy-specific enhancers','Blood vessel expressed enhancers']),\
            #('FANTOM5 Heart expressed enhancers',['Private','Antonio','FANTOM5 anatomy-specific enhancers','Heart expressed enhancers']),\
            #('K562-OpenChrom --Synthesis',['Private','Antonio','K562 cells','Open Chromatin','wgEncodeOpenChromSynthK562Pk']),\
            #('K562-DNaseI Footprints',['Chromatin','DNaseI','Footprints','K562']),\
            #('K562-DNaseI DGF --UW',['Chromatin','DNaseI','DnaseDgf Peaks','K562','UW']),\
            #('K562-Methylation450 --HAIB',['Private','Antonio','K562 cells','Methylation','wgEncodeHaibMethyl450K562SitesRep1']),\
            #('K562-MethylationRRBS --HAIB rep1',['Private','Antonio','K562 cells','Methylation','wgEncodeHaibMethylRrbsK562HaibSitesRep1']),\
            #('K562-MethylationRRBS --HAIB rep2',['Private','Antonio','K562 cells','Methylation','wgEncodeHaibMethylRrbsK562HaibSitesRep2'])
            #('K562-Insulators --UW rep1',['Private','Antonio','K562 cells','Insulators','wgEncodeUwTfbsK562CtcfStdPkRep1']),\
            #('K562-Insulators --UW rep2',['Private','Antonio','K562 cells','Insulators','wgEncodeUwTfbsK562CtcfStdPkRep2'])
            ])

        else:
            return {}

class TfbsGSuiteNameMappings:
    @staticmethod
    def getTfbsGSuiteNameMappings(genome):
        if genome == 'hg18':
            return
        elif genome == 'mm9':
            return OrderedDict([\
            ('Enhancer histone marks per cell type (H3K4me1, H3K27ac, and H3K36me3, for ES-E14 and MEL cells)', HB_SOURCE_DATA_BASE_DIR + '/TfTool/mm9_enhancer_histone_markers_cell_type_2.gsuite'),\
            ('Open chromatin per cell type (ENCODE synthesis data for ES-E14 and MEL cells)', HB_SOURCE_DATA_BASE_DIR + '/TfTool/mm9_open_chromatin_cell_type_2.gsuite')
            ])
        elif genome == 'hg19':
            return OrderedDict([\
            ('Enhancer histone marks per cell type (H3K4me1, H3K27ac, and H3K36me3, for GM12878, H1HESC, HeLaS3, HepG2, HUVEC, K562, and NHEK cells)', HB_SOURCE_DATA_BASE_DIR + '/TfTool/hg19_enhancer_histone_markers_cell_type.gsuite'),\
            ('Enhancer per tissue/organ (FANTOM5 enhancers for 41 different tissues/organs)', HB_SOURCE_DATA_BASE_DIR + '/TfTool/hg19_enhancers_anatomy.gsuite'),\
            ('Enhancer per cell type (FANTOM5 enhancers for 71 different cell types)', HB_SOURCE_DATA_BASE_DIR + '/TfTool/hg19_enhancers_cell_type.gsuite'),\
            ('Open chromatin per cell type (ENCODE synthesis data for Gliobla, GM12878, GM12892, H1HESC, HeLaS3, HepG2, HUVEC, K562, Medullo, and NHEK cells)', HB_SOURCE_DATA_BASE_DIR + '/TfTool/hg19_open_chromatin_cell_type.gsuite'),\
            ('Segmentation per cell type (Segway predictions for GM12878, H1HESC, HeLaS3, HepG2, HUVEC, and K562 cells, plus ChromHMM predictions for K562 cells)', HB_SOURCE_DATA_BASE_DIR + '/TfTool/hg19_segmentation_cell_type.gsuite')
            ])

class HiCNameMappings:
    @staticmethod
    def getHiCNameMappings(genome):
        if genome == 'mm9':
            return OrderedDict([\
            ('HiC --cortex',['DNA structure','Hi-C','Inter- and intrachromosomal','cortex','cortex-100k']),\
            ('HiC --mESC',['DNA structure','Hi-C','Inter- and intrachromosomal','mESC','mESC-100k']),\
            ('HiC --proB',['DNA structure','Hi-C','Inter- and intrachromosomal','proB','proB-egs-all-100k'])
            ])
        elif genome == 'hg19':
            return OrderedDict([\
            ('HiC --GM06990',['DNA structure','Hi-C','Inter- and intrachromosomal','GM06990','GM06990-100k']),\
            ('HiC --GM12878',['DNA structure','Hi-C','Inter- and intrachromosomal','GM12878','GM12878-HiC-HindIII-R1-100k']),\
            ('HiC --hESC',['DNA structure','Hi-C','Inter- and intrachromosomal','hESC','hESC-100k']),\
            ('HiC --IMR90',['DNA structure','Hi-C','Inter- and intrachromosomal','IMR90','IMR90-100k']),\
            ('HiC --K562',['DNA structure','Hi-C','Inter- and intrachromosomal','K562','K562-100k']),\
            ('HiC --RWPE1-ERG',['DNA structure','Hi-C','Inter- and intrachromosomal','RWPE1-ERG','RWPE1-ERG-all-200k']),\
            ('HiC --RWPE1-GFP',['DNA structure','Hi-C','Inter- and intrachromosomal','RWPE1-GFP','RWPE1-GFP-all-200k'])
            ])
