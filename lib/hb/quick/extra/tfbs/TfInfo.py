from collections import OrderedDict

class TfInfo:
    @staticmethod
    def getTfTrackNameMappings(genome):
        if genome == 'hg18':
            #return {'UCSC tfbs conserved':['Gene regulation','TFBS','UCSC prediction track'],
            #        'Bar-Joseph target gene predictions':['Gene regulation','TFBS','Bar-Joseph predictions'],
            #        'Genome-wide ChIP-seq':['Gene regulation','TFBS','ChIP-seq','Peaks'],
            #        'Genome-wide ChIP-chip':['Gene regulation','TFBS','High throughput']}

            #return OrderedDict([('UCSC tfbs conserved',['Gene regulation','TFBS','UCSC prediction track']),
            #        ('Bar-Joseph target gene predictions',['Gene regulation','TFBS','Bar-Joseph predictions']),
            #        ('Genome-wide ChIP-seq',['Gene regulation','TFBS','ChIP-seq','Peaks']),
            #        ('Genome-wide ChIP-chip',['Gene regulation','TFBS','High throughput']),
            #        ('TFBS prediction within ChIP-seq (MITF)',['Gene regulation','TFBS','Prediction within experimental','MITF']) ])
            return OrderedDict([('UCSC tfbs conserved',['Gene regulation','Transcription factor regulation','TFBS predictions','UCSC conserved sites']),
                    ('Bar-Joseph target gene predictions',['Gene regulation','Transcription factor regulation','Gene target predictions','Ernst et al (2010)']),
                    ('Genome-wide ChIP-seq',['Gene regulation','Transcription factor regulation','Experimentally determined','ChIP-seq','Peaks']),
                    ('Genome-wide ChIP-chip',['Gene regulation','Transcription factor regulation','Experimentally determined','ChIP-chip']),
                    ('TFBS prediction within ChIP-seq (MITF)',['Gene regulation','Transcription factor regulation','Prediction within experimental']) ])
            
        elif genome == 'mm9':
            return OrderedDict([('Stanford & Yale tfbs conserved',['Gene regulation','TFBS','Stanford & Yale', 'Peaks']) ])
        elif genome == 'hg19':
            return OrderedDict([('UCSC tfbs conserved',['Gene regulation','Transcription factor regulation','TFBS predictions','UCSC conserved sites']), ('ENCODE TFs',['Private','GK','MS4','SelectedEncodeTfs']) ])
        else:
            return {}