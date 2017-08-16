from collections import OrderedDict
'''
Created on Oct-Nov, 2014
@author: Antonio Mora
Last update: Antonio Mora; Mar 8, 2015
'''

class TfTrackNameMappings:
    @staticmethod
    def getTfTrackNameMappings(genome):
        if genome == 'hg18':
            return OrderedDict([
                ('UCSC tfbs conserved',['Gene regulation','Transcription factor regulation','TFBS predictions','UCSC conserved sites']),
                ('Bar-Joseph target gene predictions',['Gene regulation','Transcription factor regulation','Gene target predictions','Ernst et al (2010)']),
                ('Genome-wide ChIP-seq',['Gene regulation','Transcription factor regulation','Experimentally determined','ChIP-seq','Peaks']),
                ('Genome-wide ChIP-chip',['Gene regulation','Transcription factor regulation','Experimentally determined','ChIP-chip']),
                ('TFBS prediction within ChIP-seq (MITF)',['Gene regulation','Transcription factor regulation','Prediction within experimental'])\
                ])
            
        elif genome == 'mm9':
            return OrderedDict([('Stanford & Yale ChIP-seq',['Gene regulation','TFBS','Stanford & Yale', 'Peaks']) ])
        elif genome == 'hg19':
            return OrderedDict([
                ('UCSC-ENCODE TFBS Conserved Sites',['Gene regulation','Transcription factor regulation','TFBS predictions','UCSC conserved sites']),\
                ('UCSC-ENCODE TFBS ChIP',['Private','Antonio','UCSC-Txn Factor ChIP V3new'])\
                ])  # Add track of pioneer factors.
        else:
            return {}

