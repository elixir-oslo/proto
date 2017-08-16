from collections import OrderedDict

from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.extra.tfbs.TfbsTrackNameMappings import HiCNameMappings
from quick.extra.tfbs.getTrackRelevantInfo import getTrackRelevantInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool

'''
Created on Mar 7, 2015
@author: Antonio Mora
Last update: Antonio Mora; Mar 8, 2015
'''

class AntoniosTool(GeneralGuiTool):
    REGIONS_FROM_HISTORY = 'History (user-defined)'
    SELECT = '--- Select ---'

    @staticmethod
    def getToolName():
        return 'Scan Promoter-Enhancer Interaction data'

    @staticmethod
    def getInputBoxNames():
        return [('Genome', 'genome'),\
        ('PEI Source', 'sourceHic'),\
        ('PEI Regions', 'hicdic'),\
        ('Annotation Source', 'sourceAnnotation'),\
        ('Annotated Regions', 'annotation')
        ]

    @staticmethod
    def getOptionsBoxGenome():
        return ['hg19','mm9']

    @classmethod
    def getOptionsBoxSourceHic(cls, prevChoices):
        return [cls.SELECT] + ['Hyperbrowser repository'] + [cls.REGIONS_FROM_HISTORY]

    @classmethod
    def getOptionsBoxHicdic(cls, prevChoices):
        if prevChoices.sourceHic == 'Hyperbrowser repository':
            dic = HiCNameMappings.getHiCNameMappings(prevChoices.genome)
            falses = ('False')*len(dic.keys())
            return OrderedDict(zip(list(dic.keys()),falses))
        elif prevChoices.sourceHic == cls.REGIONS_FROM_HISTORY:
            return ('__history__','bed','category.bed','gtrack')
        else:
            return

    @classmethod
    def getOptionsBoxSourceAnnotation(cls, prevChoices):
        return [cls.SELECT] + ['Hyperbrowser repository'] + [cls.REGIONS_FROM_HISTORY]

    @classmethod
    def getOptionsBoxAnnotation(cls, prevChoices):
        if prevChoices.sourceAnnotation == 'Hyperbrowser repository':
            return
        elif prevChoices.sourceAnnotation == cls.REGIONS_FROM_HISTORY:
            return ('__history__','bed','category.bed','gtrack')
        else:
            return

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        genome = choices.genome
        sourceHic = choices.sourceHic
        hicdic = choices.hicdic
        annotation = choices.annotation

        # Get Genomic Regions track names:
        selectedTrackNames = []
        if isinstance(hicdic,dict):
            selectedHiCRegions = [key for key,val in hicdic.iteritems() if val == 'True']
        else:
            selectedHiCRegions = hicdic

        if sourceHic == 'Hyperbrowser repository':
            selectedTrackNames = []
            for i in selectedHiCRegions:
                hicTrackName = HiCNameMappings.getHiCNameMappings(genome)[ i ]
                selectedTrackNames.append(hicTrackName)

                print '<p>', i, '</p>'
                print getTrackRelevantInfo.getNumberElements(genome, hicTrackName)
                print getTrackRelevantInfo.getSegmentSizes(genome, hicTrackName)
                #print getTrackRelevantInfo.getAnchor(genome, hicTrackName)
                targetBins = getTrackRelevantInfo.getGenomicElements(genome, hicTrackName)
                print targetBins
                print '<p>==============================================</p>'
            
                analysis = AntoniosTool.getHiCFileFromTargetBins(targetBins, galaxyFn)
                print '<p>', analysis.getLoadToHistoryLink('Send file to History'), '</p>'
                print '<p>==============================================</p>'
        elif sourceHic == cls.REGIONS_FROM_HISTORY:
            galaxyTN = selectedHiCRegions.split(':')
            hicTrackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, galaxyTN)

            print '<p>', selectedHiCRegions, '</p>'
            print '<p>', hicTrackName, '</p>'
            numElements = getTrackRelevantInfo.getNumberElements(genome, hicTrackName)
            print 'numElements=', sum(numElements), numElements
            print getTrackRelevantInfo.getSegmentSizes(genome, hicTrackName)
            trackElements = getTrackRelevantInfo.getGenomicElements(genome, hicTrackName)
            print len(trackElements), trackElements
            print '<p>==============================================</p>'
            
            analysis = AntoniosTool.getHiCFileFromTargetBins(trackElements, galaxyFn)
            print '<p>', analysis.getLoadToHistoryLink('Send file to History'), '</p>'
            print '<p>==============================================</p>'

    # General plan: Fantom5 navigator: Input gene, get interacting enhancers, check expression of those per robust/permissive, per tissue, check expression of those in time.
    # I must add and check all FANTOM5 Phase2 data!!!:  http://fantom.gsc.riken.jp/5/data/
    # I must add and check all Roadmap Epigenomics data:  http://www.ncbi.nlm.nih.gov/geo/roadmap/epigenomics/?search=&display=50

    @staticmethod
    def getHiCFileFromTargetBins(targetBins, galaxyFn):
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
        staticFile = GalaxyRunSpecificFile(['PEI_regions.bed'], galaxyFn)
        fn = staticFile.getDiskPath()
        from quick.util.CommonFunctions import ensurePathExists
        ensurePathExists(fn)
        f = open(fn, 'w')
        import os
        for region in targetBins:
            chrom = region[0]
            start = region[1]
            end = region[2]
            f.write( '\t'.join([chrom, str(start), str(end)]) + os.linesep )
        f.close()
        return staticFile

    @staticmethod
    def getOutputFormat(choices=None):
        return 'html'

    @staticmethod
    def getToolIllustration():
        return ['illustrations','tools','TF1.jpg']

    @staticmethod
    def getToolDescription():
        return '<b>Transcription Factor Binding Site Scanning Tool, v.1.0</b><p>\
        This tool performs an intersection between two types of tracks: a selected genomic region\
        and a track of putative TF binding sites, which allows the user to explore:<p>\
        * Genes, exons or promoters in the vicinity of putative binding sites for a given Transcription Factor.<p>\
        * Transcription Factor Binding Sites for a given Transcription Factor.\
        The sites are determined through putative TF binding sites found in open chromatin regions such\
        as enhancers and DNaseI hypersensitive regions.<p>\
        The tool works with pre-determined tracks of TF binding sites, either from the hyperbrowser repository\
        or from History. If you have your own TF Track, you can upload it to History using "Get Data"\
        and then select TF Source = History Element.<p>\
        The tool offers a certain number of useful genomic tracks and multi-tracks to be compared to the TF track. If\
        the genomic track you need is not there, you can upload it to History using "Get Data" and\
        then select Genomic Region = History Element.\
        If you don\'t have a TF track but a specific binding motif, a consensus sequence or a PWM, you can\
        also build a track with this information and upload it from TF Source = History Element.<p>\
        <p>The following picture illustrates the goal/scope of this tool.<p>'

    @staticmethod
    def isHistoryTool():
        return True

    @staticmethod
    def getFullExampleURL():
        return 'u/hb-superuser/p/use-case---tfs-in-enhancers'

    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True
