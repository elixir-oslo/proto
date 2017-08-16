from gold.origdata.FileFormatComposer import findMatchingFileFormatComposers, getComposerClsFromFileFormatName
from gold.origdata.GenomeElementSource import GenomeElementSource
from gold.track.TrackFormat import TrackFormat
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class UniversalConverterTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Convert between GTrack/BED/WIG/bedGraph/GFF/FASTA files"

    @staticmethod
    def getInputBoxNames():
        return [('Select a specific genome?', 'selectGenome'), \
                ('Genome build:', 'genome'), \
                ('Select file from history:', 'history'), \
                ('Select conversion:', 'conversion')]
    
    @staticmethod    
    def getOptionsBoxSelectGenome():
        return ['No', 'Yes']
    
    @staticmethod    
    def getOptionsBoxGenome(prevChoices):
        if prevChoices[0] == 'Yes':
            return "__genome__"
    
    @staticmethod    
    def getOptionsBoxHistory(prevChoices):
        return '__history__', 'gtrack', 'bed', 'point.bed', 'category.bed', \
                              'valued.bed', 'wig', 'targetcontrol.bedgraph', \
                              'bedgraph', 'gff', 'gff3', 'fasta'
        
    @staticmethod
    def getOptionsBoxConversion(prevChoices):
        if prevChoices.history:
            try:
                geSource = UniversalConverterTool._getGESource(prevChoices)
                matchingComposers = findMatchingFileFormatComposers(TrackFormat.createInstanceFromGeSource(geSource))
                return ['%s -> %s (track type: %s)' % \
                        (geSource.getFileFormatName(), composerInfo.fileFormatName, composerInfo.trackFormatName) \
                        for composerInfo in matchingComposers if geSource.getFileFormatName() != composerInfo.fileFormatName]
            except:
                return []
    
    @staticmethod
    def _getGESource(choices):
        genome = choices.genome if choices.selectGenome == 'Yes' else None
        galaxyTN = choices.history.split(':')
        suffix = ExternalTrackManager.extractFileSuffixFromGalaxyTN(galaxyTN)
        fn = ExternalTrackManager.extractFnFromGalaxyTN(galaxyTN)
        return GenomeElementSource(fn, genome=genome, printWarnings=False, suffix=suffix)
    
    @staticmethod
    def _getComposerCls(choices):
        fileFormatName = choices.conversion.split(' -> ')[1].split(' (')[0]
        return getComposerClsFromFileFormatName(fileFormatName)
        
    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        
        try:
            geSource = cls._getGESource(choices)
            composerCls = cls._getComposerCls(choices)
            composerCls(geSource).composeToFile(galaxyFn)
        except Exception, e:
            import sys
            print >> sys.stderr, e

    @staticmethod
    def validateAndReturnErrors(choices):
        genome = choices.genome if choices.selectGenome == 'Yes' else None
        
        if genome == '':
            return 'Please select a genome build.'
    
        error = GeneralGuiTool._checkHistoryTrack(choices, 'history', genome)
        if error:
           return error
            
        if choices.conversion is None:
            suffix = ExternalTrackManager.extractFileSuffixFromGalaxyTN(choices.history.split(':'))
            return 'No conversions available for the selected file. Please make ' \
                   'sure that the file type is correct. Current file type: %s' % suffix
        
    #@staticmethod
    #def getSubToolClasses():
    #    return None
    #
    @staticmethod
    def isPublic():
        return True

    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    #@staticmethod
    #def getRedirectURL(choices):
    #    return ''
    #
    #@staticmethod
    #def isHistoryTool():
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    return []
    #
    @staticmethod
    def getToolDescription():
        core = HtmlCore()
        core.paragraph('This tool converts files between the following file formats:')
        core.descriptionLine('GTrack', "See the 'Show GTrack specification' tool", emphasize=True)
        core.descriptionLine('BED', str(HtmlCore().link('BED specification', \
                                        'http://genome.ucsc.edu/FAQ/FAQformat.html')), emphasize=True)
        core.descriptionLine('WIG', str(HtmlCore().link('WIG specification', \
                                        'http://genome.ucsc.edu/goldenPath/help/wiggle.html')), emphasize=True)
        core.descriptionLine('bedGraph', str(HtmlCore().link('bedGraph specification', \
                                            'http://genome.ucsc.edu/goldenPath/help/bedgraph.html')), emphasize=True)
        core.descriptionLine('GFF', str(HtmlCore().link('GFF version 3 specification', \
                                            'http://www.sequenceontology.org/gff3.shtml')), emphasize=True)
        core.descriptionLine('FASTA', str(HtmlCore().link('bedGraph specification', \
                                            'http://www.ncbi.nlm.nih.gov/BLAST/blastcgihelp.shtml')), emphasize=True)
        core.paragraph('The input data type is defined by the format field of the history element of the data. '
                       'The available conversions for the selected format are automatically '
                       'shown in the conversion selection box')
        
        core.divider()
        
        core.smallHeader('Genome')
        core.paragraph('Some GTrack files require a specified genome to be valid, e.g. if bounding regions '
                       'are specified without explicit end coordinates.')
        
        core.divider()
        
        core.smallHeader('GTrack subtypes')
        core.paragraph('If the conversion to extended GTrack is selected, GTrack subtype information may be '
                       'added to the output file. The following GTrack subtypes are automatically detected from '
                       'the contents of the input file:')

        from gold.origdata.GtrackComposer import StdGtrackComposer
        core.unorderedList(str(HtmlCore().link(x, x)) for x in StdGtrackComposer.GTRACK_PRIORITIZED_SUBTYPE_LIST)
        core.divider()
        
        core.smallHeader('Notice')
        core.paragraph("The GFF support is somewhat preliminary. For conversions between BED and GFF, we "
                       "recommend the specialized Galaxy tools: 'BED-to-GFF converter' and 'GFF-to-BED converter'.")
        
        core.divider()
        
        core.smallHeader('Example 1')
        core.paragraph('Input file (BED)')
        core.styleInfoBegin(styleClass='debug')
        core.append(
'''chrM    71      82      A       1000    +       71      79      0,0,255 2       4,4,    0,8
chrM    103     105     B       800     .       103     105     0,255,0 1       2       0
chr21   3       13      C       645     -       3       13      255,0,0 3       2,2,2   0,5,8''')
        core.styleInfoEnd()
        
        core.paragraph('Output file (Extended GTrack)')
        core.styleInfoBegin(styleClass='debug')
        core.append(
'''##gtrack version: 1.0
##track type: valued segments
##uninterrupted data lines: true
###seqid	start	end	value	strand	name	thickstart	thickend	itemrgb	blockcount	blocksizes	blockstarts
chrM	71	82	1000	+	A	71	79	0,0,255	2	4,4,	0,8
chrM	103	105	800	.	B	103	105	0,255,0	1	2	0
chr21	3	13	645	-	C	3	13	255,0,0	3	2,2,2	0,5,8''')
        core.styleInfoEnd()
        
        core.divider()
        
        core.smallHeader('Example 2')
        core.paragraph('Input file (WIG)')
        core.styleInfoBegin(styleClass='debug')
        core.append(
'''track type=wiggle_0
fixedStep chrom=chrM start=11 step=10 span=5
4.500
-3.700
fixedStep chrom=chrM start=1013 step=10 span=5
2.100
11.00
fixedStep chrom=chr21 start=201 step=10 span=5
21.10''')
        core.styleInfoEnd()
        
        core.paragraph('Output file (bedGraph)')
        core.styleInfoBegin(styleClass='debug')
        core.append(
'''track type=bedGraph
chrM	10	15	4.500
chrM	20	25	-3.700
chrM	1012	1017	2.100
chrM	1022	1027	11.00
chr21	200	205	21.10''')
        core.styleInfoEnd()
        
        core.paragraph('Output file (GTrack)')
        core.styleInfoBegin(styleClass='debug')
        core.append(
'''##gtrack version: 1.0
##track type: valued segments
##1-indexed: true
##end inclusive: true
##fixed length: 5
##fixed gap size: 5
##gtrack subtype: wig fixedstep
##subtype url: http://gtrack.no/wig_fixedstep.gtrack
##subtype adherence: strict
###value
####seqid=chrM; start=11; end=25
4.5
-3.7
####seqid=chrM; start=1013; end=1027
2.1
11.0
####seqid=chr21; start=201; end=205
21.1''')
        core.styleInfoEnd()
        return str(core)
    #
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    
    @staticmethod
    def getFullExampleURL():
        return 'u/hb-superuser/p/convert-between-gtrackbedwigbedgraphgfffasta-files'

    #@classmethod
    #def isBatchTool(cls):
    #    return cls.isHistoryTool()
    #
    #@staticmethod
    #def isDebugMode():
    #    return False
    #
    @staticmethod    
    def getOutputFormat(choices):
        if choices.history and choices.conversion:
            composerCls = UniversalConverterTool._getComposerCls(choices)
            return composerCls.getDefaultFileNameSuffix()
        return 'gtrack'
