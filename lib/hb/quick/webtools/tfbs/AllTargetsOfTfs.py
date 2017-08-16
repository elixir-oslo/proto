from collections import OrderedDict

import gold.gsuite.GSuiteConstants as GSuiteConstants
import quick.webtools.restricted.visualization.visualizationPlots as vp
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.ProcTrackOptions import ProcTrackOptions
from quick.extra.TrackIntersection import TrackIntersection
from quick.extra.tfbs.TfTrackNameMappings import TfTrackNameMappings
from quick.extra.tfbs.TfbsTrackNameMappings import TfbsGSuiteNameMappings,\
    TfbsTrackNameMappings
from quick.multitrack.MultiTrackCommon import getGSuiteFromGSuiteFile, getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool

from quick.webtools.mixin.DebugMixin import DebugMixin

'''
Created on Nov 12, 2014
@author: Antonio Mora
Last update: Antonio Mora; Jun 14, 2016
'''



class AllTargetsOfTfs(GeneralGuiTool, DebugMixin):
    REGIONS_FROM_HISTORY = 'Track from History'
    SELECT = '--- Select ---'
    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]
    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]
    
    @staticmethod
    def getToolName():
        return 'Scan targets of a transcription factor'

    @staticmethod
    def getInputBoxNames():
        return [('', 'basicQuestionId'),
                ('Genome', 'genome'),\
                ('Genomic Regions Source', 'genomicRegionsSource'),\
                ('Genomic Regions', 'genomicRegions'),\
                #('Upstream Flank Size (bp)','upFlankSize'),\
                #('Downstream Flank Size (bp)','downFlankSize'),\
                ('TF Source', 'sourceTfs'),\
                ('TF Tracks', 'tfTracks'),\
                ] + DebugMixin.getInputBoxNamesForDebug()

    @classmethod
    def getOptionsBoxBasicQuestionId(cls):
        return '__hidden__', None

    @classmethod
    def getOptionsBoxGenome(cls, prevChoices):
        return [cls.SELECT, 'hg19', 'mm9'] #'__genome__'

    @staticmethod
    def getInfoForOptionsBoxGenome():
        return 'Before starting, please select a genome. The only two currently available genome versions are: "Homo sapiens hg19" and \
        "Mus musculus mm9".'

    @classmethod
    def getOptionsBoxGenomicRegionsSource(cls, prevChoices):
        if prevChoices.genome != cls.SELECT:
            return [cls.SELECT] + ['Hyperbrowser repository (single tracks)'] + ['Hyperbrowser repository (cell-specific multi-tracks)'] + \
            ['History (user-defined)']

    @staticmethod
    def getInfoForOptionsBoxGenomicRegionsSource(prevChoices):
        if prevChoices.genome == 'hg19':
            return 'This tool will allow you to determine overlap between one transcription factor track and one or more genomic region tracks \
            (compare binding of one transcription factor across multiple regions).<p>In this step,\
            you can choose between three sources of genomic region tracks: The single tracks stored in the hyperbrowser repository, the cell-line\
            specific multi-tracks (GSuite) stored in the GSuite hyperbrowser repository, or tracks that you have previously uploaded to Galaxy History.<p>\
            The single tracks in the hyperbrowser repository include:<ul>\
            <li><a href="http://www.ensembl.org/Homo_sapiens/Info/Index">Ensemble Genes, Exons and Introns</a></li>\
            <li><a href="http://www.ncbi.nlm.nih.gov/refseq/rsg/">RefSeq Genes, Exons and Introns</a></li>\
            <li><a href="http://genome.ucsc.edu/cgi-bin/hgTables?hgta_doSchemaDb=hg19&hgta_doSchemaTable=switchDbTss">SwitchGear TSS Database</a></li>\
            <li><a href="http://enhancer.lbl.gov/cgi-bin/imagedb3.pl?form=search&show=1&search.form=no&search.result=yes">Vista Enhancers Database</a></li>\
            <li><a href="http://enhancer.binf.ku.dk/presets/">FANTOM5/Transcribed-Enhancer-Atlas Robust Enhancers</a></li>\
            <li><a href="http://enhancer.binf.ku.dk/presets/">FANTOM5/Transcribed-Enhancer-Atlas Ubiquitous Enhancers -cell-based</a></li>\
            <li><a href="http://enhancer.binf.ku.dk/presets/">FANTOM5/Transcribed-Enhancer-Atlas Ubiquitous Enhancers -anatomy-based</a></li>\
            </ul><p>The multi-tracks in the GSuite hyperbrowser repository include:<ul>\
            <li><a href="http://genome.ucsc.edu/cgi-bin/hgTrackUi?g=wgEncodeHistoneSuper">Enhancer-associated histone marks per cell type (H3K4me1, H3K27ac, and H3K36me3, for GM12878, H1HESC, HeLaS3, HepG2, HUVEC, K562, and NHEK cells)</a></li>\
            <li><a href="http://enhancer.binf.ku.dk/presets/">Enhancer per tissue/organ (FANTOM5 enhancers for 41 different tissues/organs)</a></li>\
            <li><a href="http://enhancer.binf.ku.dk/presets/">Enhancer per cell type (FANTOM5 enhancers for 71 different cell types)</a></li>\
            <li><a href="http://genome.ucsc.edu/cgi-bin/hgTrackUi?g=wgEncodeDNAseSuper">Open chromatin per cell type (ENCODE synthesis data for Gliobla, GM12878, GM12892, H1HESC, HeLaS3, HepG2, HUVEC, K562, Medullo, and NHEK cells)</a></li>\
            <li><a href="http://genome.ucsc.edu/cgi-bin/hgTrackUi?g=wgEncodeAwgSegmentation">Segmentation per cell type (Segway predictions for GM12878, H1HESC, HeLaS3, HepG2, HUVEC, and K562 cells, plus ChromHMM predictions for K562 cells)</a></li>\
            </ul><p>'
        elif prevChoices.genome == 'mm9':
            return 'This tool will allow you to determine overlap between one transcription factor track and one or more genomic region tracks \
            (compare binding of one transcription factor across multiple regions).<p>In this step,\
            you can choose between three sources of genomic region tracks: The single tracks stored in the hyperbrowser repository, the cell-line\
            specific multi-tracks (GSuite) stored in the GSuite hyperbrowser repository, or tracks that you have previously uploaded to Galaxy History.\
            The single tracks in the hyperbrowser repository include:<ul>\
            <li><a href="http://www.ensembl.org/Mus_musculus/Info/Index">Ensemble Genes</a></li>\
            <li><a href="http://www.ncbi.nlm.nih.gov/refseq/rsg/">RefSeq Genes, Exons, Introns and Intergenic regions</a></li>\
            <li><a href="http://fantom.gsc.riken.jp/5/data/">FANTOM5 Cage Peak Robust</a></li>\
            </ul><p>The multi-tracks in the GSuite hyperbrowser repository include:<ul>\
            <li><a href="http://genome.ucsc.edu/cgi-bin/hgTrackUi?g=wgEncodeHistoneSuper">Enhancer-associated histone marks per cell type (H3K4me1, H3K27ac, and H3K36me3, for ES-E14 and MEL cells)</a></li>\
            <li><a href="http://genome.ucsc.edu/cgi-bin/hgTrackUi?g=wgEncodeDNAseSuper">Open chromatin per cell type (ENCODE synthesis data for ES-E14 and MEL cells)</a></li>\
            </ul><p>'
        else:
            return

    @classmethod
    def getOptionsBoxGenomicRegions(cls, prevChoices):
        if prevChoices.genomicRegionsSource != cls.SELECT:
            if prevChoices.genomicRegionsSource == 'Hyperbrowser repository (single tracks)':
                dic1 = TfbsTrackNameMappings.getTfbsTrackNameMappings(prevChoices.genome)
                falses1 = ['False']*len(dic1.keys())
                return OrderedDict(zip(list(dic1.keys()),falses1)) #OrderedDict(zip(('A','B'),('False','False')))
            elif prevChoices.genomicRegionsSource == 'Hyperbrowser repository (cell-specific multi-tracks)':
                dic2 = TfbsGSuiteNameMappings.getTfbsGSuiteNameMappings(prevChoices.genome)
                falses2 = ('False')*len(dic2.keys())
                return OrderedDict(zip(list(dic2.keys()),falses2))
            elif prevChoices.genomicRegionsSource == 'History (user-defined)':
                return ('__history__','bed','category.bed','gtrack','gsuite')
        else:
            return

    '''@classmethod
    @staticmethod
    def getOptionsBoxUpFlankSize(prevChoices):
        return ['0','100','200','300','400','500','600','700','800','900','1000']

    @staticmethod
    def getOptionsBoxDownFlankSize(prevChoices):
        return ['0','100','200','300','400','500','600','700','800','900','1000']
    '''

    #@staticmethod
    #def getResetBoxes():
    #    return ['genomicRegionsSource']

    @classmethod
    def getOptionsBoxSourceTfs(cls, prevChoices):
        if prevChoices.genomicRegions:
            if prevChoices.genomicRegions != cls.SELECT:
                return [cls.SELECT] + TfTrackNameMappings.getTfTrackNameMappings(prevChoices.genome).keys() + \
                [cls.REGIONS_FROM_HISTORY]
                # For ex.: 'UCSC TFBS Conserved Sites','UCSC-Txn Factor ChIP V3','History elements'.
            else:
                return
        else:
            return

    @staticmethod
    def getInfoForOptionsBoxSourceTfs(prevChoices):
        if prevChoices.genome == 'hg19':
            return 'This tool will allow you to determine overlap between one transcription factor track and one or more genomic region tracks \
            (compare binding of one transcription factor across multiple regions).<p>In this step,\
            you can choose between three sources of transcription factor tracks: The TFBS Conserved Track (<a href="http://genome.ucsc.edu/cgi-bin/hgTables?hgta_doSchemaDb=hg19&hgta_doSchemaTable=tfbsConsSites">see for details</a>),\
            the track with ChIP-seq uniform peaks from ENCODE (<a href="http://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg19&g=wgEncodeAwgTfbsUniform">see for details</a>),\
            or tracks that you have previously uploaded to Galaxy History.'
        elif prevChoices.genome == 'mm9':
            return 'This tool will allow you to determine overlap between one transcription factor track and one or more genomic region tracks \
            (compare binding of one transcription factor across multiple regions).<p>In this step,\
            you can choose between two sources of transcription factor tracks: Either Stanford & Yale TFBS ChIP-seq track (<a href=\
            "http://genome.ucsc.edu/cgi-bin/hgTables?db=mm9&hgta_group=regulation&hgta_track=wgEncodeSydhTfbs">see for details</a>), or\
            tracks that you have previously uploaded to Galaxy History.'
        else:
            return

    @classmethod
    def getOptionsBoxTfTracks(cls, prevChoices):
        if prevChoices.sourceTfs:
            if prevChoices.sourceTfs == cls.REGIONS_FROM_HISTORY:
                return ('__history__','bed','category.bed','gtrack')
            elif prevChoices.sourceTfs == cls.SELECT:
                return
            else:
                tfSourceTN = TfTrackNameMappings.getTfTrackNameMappings(prevChoices.genome)[ prevChoices.sourceTfs ]
                subtypes = ProcTrackOptions.getSubtypes(prevChoices.genome, tfSourceTN, True)
                return subtypes
        else:
            return

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        cls._setDebugModeIfSelected(choices)

        genome = choices.genome
        genomicRegionsSource = choices.genomicRegionsSource
        genomicRegions = choices.genomicRegions
        #upFlankSize = int(choices.upFlankSize)
        #downFlankSize = int(choices.downFlankSize)
        sourceTfs = choices.sourceTfs
        tfTracks = choices.tfTracks

        # Get TF track name:
        if sourceTfs == cls.REGIONS_FROM_HISTORY:
            galaxyTN = tfTracks.split(':')
            tfTrackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, galaxyTN)
        else:
            tfTrackName = TfTrackNameMappings.getTfTrackNameMappings(genome)[ sourceTfs ] + [tfTracks]

        # Get Genomic Regions track names:
        selectedTrackNames = []

        if isinstance(genomicRegions,dict):
            selectedGenRegions = [key for key,val in genomicRegions.iteritems() if val == 'True']
        else:
            selectedGenRegions = genomicRegions

        if genomicRegionsSource=='Hyperbrowser repository (single tracks)':
            for i in selectedGenRegions:
                selectedTrackNames.append(TfbsTrackNameMappings.getTfbsTrackNameMappings(genome)[ i ])
        elif genomicRegionsSource=='Hyperbrowser repository (cell-specific multi-tracks)':
            for i in selectedGenRegions:
                genElementGSuiteName = TfbsGSuiteNameMappings.getTfbsGSuiteNameMappings(genome)[ i ]
                gSuite = getGSuiteFromGSuiteFile(genElementGSuiteName)
                for track in gSuite.allTracks():
                    selectedTrackNames.append(track.trackName)
        elif genomicRegionsSource=='History (user-defined)':
            if genomicRegions.split(":")[1] == "gsuite":
                gSuite = getGSuiteFromGalaxyTN(selectedGenRegions)
                for track in gSuite.allTracks():
                    selectedTrackNames.append(track.trackName)
            else:
                galaxyTN = selectedGenRegions.split(':')
                gRegTrackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, galaxyTN)
                selectedTrackNames.append(gRegTrackName)
        else:
            return

        #Intersection:
        title = 'Targets of ' + tfTrackName[-1] + ' TF track'
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.header(title)
        htmlCore.divBegin('resultsDiv')
        htmlCore.tableHeader(['Genomic Region', 'Number of Target Regions', 'Download bed file of Target Regions', 'Send bed file to history'], sortable=True, tableId='resultsTable')

        n = 0
        allTargetBins = []; dataY = []; allRefSetNames = []
        #print 'all:', selectedTrackNames, '<p>'
        #print 'tf:', tfTrackName, '<p>'
        for i in selectedTrackNames:
            n = n+1
            #newGalaxyFn = galaxyFn.split(".")[0] + str(n) + "." + "dat"

            tfIntersection = TrackIntersection(genome, i, tfTrackName, galaxyFn, str(n))
            #tfIntersection.expandReferenceTrack(upFlankSize, downFlankSize)
            regFileNamer = tfIntersection.getIntersectedRegionsStaticFileWithContent()
            targetBins = tfIntersection.getIntersectedReferenceBins()

            '''print 'Target Bins = ', targetBins, '<p>'
            if genomicRegionsSource=='Hyperbrowser repository (single tracks)':
                print '\"', tfTracks, '\" in \"', ":".join((i[len(i)-2],i[len(i)-1])), '":<p>'
            elif genomicRegionsSource=='History (user-defined)':
                print '\"', tfTracks, '\" in \"', i[len(i)-1], '":<p>'
            else:
                listGenRegion = i[0].split(":")
                maxIndex = len(listGenRegion)-1
                print '\"', tfTracks, '\" in \"', ":".join((listGenRegion[maxIndex-1],listGenRegion[maxIndex])), '":<p>'
            print '<p>Number of Targets = ', len(targetBins), 'regions.</p>'
            print '<p>', regFileNamer.getLink('Download bed-file'), ' of all regions with 1 or more hits.</p>'
            print '<p>', regFileNamer.getLoadToHistoryLink('Download bed-file to History'), ' of all regions with 1 or more hits.</p>'
            print '<p>==============================================</p>'
            #with open(galaxyFn, 'w') as outFile:
                #print>>outFile, 'TargetBins=', targetBins, '<p>'
                #print >>outFile, selectedGenRegions, '<p>' '''
            # Collect all target bins and data to plot:
            allTargetBins = allTargetBins + targetBins
            dataY = dataY + [TrackIntersection.prepareDataForPlot(genome, targetBins)]
            refSetName = i[len(i)-1]
            allRefSetNames = allRefSetNames + [refSetName]

            # Print output to table:
            line = [refSetName] + [len(targetBins)] + [regFileNamer.getLink('Download bed-file')] + [regFileNamer.getLoadToHistoryLink('Download bed-file to History')]
            #print line, '<p>'
            htmlCore.tableLine(line)

        line = ['Total'] + [len(allTargetBins)] + [''] + ['']
        dataY = dataY + [TrackIntersection.prepareDataForPlot(genome, allTargetBins)]
        allRefSetNames = allRefSetNames + ['Total']

        htmlCore.tableLine(line)
        htmlCore.tableFooter()
        htmlCore.divEnd()
        htmlCore.hideToggle(styleClass='debug')
        htmlCore.end()
        print htmlCore
        #print 'ALL Target Bins = ', allTargetBins, '<p>'
        #print 'dataY = ', dataY, '<p>'

        # Plot:
        if genome == 'hg19':
            chrNames = ['chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chr20','chr21','chr22','chrX','chrY']        
        if genome == 'mm9':
            chrNames = ['chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chrX','chrY']
            
        titleText = 'Targets per Chromosome'
        dataX = [[dataY[i][j] for i in range(len(dataY))] for j in range(len(dataY[0]))]
        seriesType = ['column']*len(dataX)
        categories = allRefSetNames
        yAxisTitle = 'Number of Targets'
        seriesName = chrNames
        shared=False
        legend =True
        xAxisRotation=0
        #print 'dataX = ', dataX, '<p>'

        htmlCore = HtmlCore()
        htmlCore.begin()
        title = 'Targets of ' + tfTrackName[-1] + ' TF track per chromosome'
        htmlCore.header(title)
        htmlCore.line('<a href="#" id="linkContainer1">Click to see plot</a>')
        htmlCore.divBegin(divId='plotDiv', style=' margin: 0 auto')
        htmlCore.line(vp.addJSlibs())
        htmlCore.line(vp.useThemePlot())
        htmlCore.line(vp.addJSlibsExport())
        plot = vp.drawChart(dataX, type='column', legend =legend, height=600, xAxisRotation=xAxisRotation, seriesType=seriesType, seriesName=seriesName, shared=shared, titleText=titleText, overMouseAxisX=True, categories=categories, showChartClickOnLink=True)
        htmlCore.line(plot)
        htmlCore.divEnd()
        htmlCore.end()
        print htmlCore

    @classmethod
    def validateAndReturnErrors(cls, choices):
        genome = choices.genome
        genomicRegionsSource = choices.genomicRegionsSource
        genomicRegions = choices.genomicRegions
        sourceTfs = choices.sourceTfs
        tfTracks = choices.tfTracks

        # Check genome
        if genome == cls.SELECT:
            return 'Please select a genome build.'

        # Check that all boxes have data:
        if genomicRegionsSource == AllTargetsOfTfs.SELECT:
            return 'Please select a genomic region source.'
        if not genomicRegions:
            return 'Please select a genomic region.'

        # Check tracks for Genomic Regions-History:
        if genomicRegionsSource=='History (user-defined)':
            if len(genomicRegions.split(":")) > 1:
                if genomicRegions.split(":")[1] == "gsuite":
                    errorString = GeneralGuiTool._checkGSuiteFile(genomicRegions)
                    if errorString:
                        return errorString
                    else:
                        gSuite = getGSuiteFromGalaxyTN(genomicRegions)
                        sizeErrorString = GeneralGuiTool._checkGSuiteTrackListSize(gSuite, 1, 1000)
                        if sizeErrorString:
                            return sizeErrorString
                        else:
                            reqErrorString = GeneralGuiTool._checkGSuiteRequirements \
                                (gSuite,
                                 AllTargetsOfTfs.GSUITE_ALLOWED_FILE_FORMATS,
                                 AllTargetsOfTfs.GSUITE_ALLOWED_LOCATIONS,
                                 AllTargetsOfTfs.GSUITE_ALLOWED_TRACK_TYPES,
                                 AllTargetsOfTfs.GSUITE_DISALLOWED_GENOMES)
                            if reqErrorString:
                                return reqErrorString
                else:
                    errorString = GeneralGuiTool._checkTrack(choices, 'genomicRegions', 'genome')
                    if errorString:
                        return errorString

        if sourceTfs == AllTargetsOfTfs.SELECT:
            return 'Please select a TF source.'
        if not tfTracks:
            return 'Please select a TF track.'

        # Check tracks for TFs-History:
        if sourceTfs=='History (user-defined)':
            tfErrorString = GeneralGuiTool._checkTrack(choices, 'tfTracks', 'genome')
            if tfErrorString:
                return tfErrorString

        return None

    @staticmethod
    def getOutputFormat(choices=None):
        return 'html'

    @staticmethod
    def getToolIllustration():
        return ['illustrations','tools','TF1.jpg']

    @staticmethod
    def getToolDescription():
        return '<b>Transcription Factor Analysis Workbench, v.1.0</b><p>\
        This tool performs an intersection between two types of tracks: One or more selected genomic regions\
        and a track of putative TF binding sites, which allows the user to explore:<p>\
        * Genes, exons or promoters in the vicinity of putative binding sites for a given Transcription Factor.<p>\
        * Transcription Factor Binding Sites for a given Transcription Factor across multiple samples.<p>\
        The tool works with pre-determined tracks of TF binding sites, either from the hyperbrowser repository\
        or from History. If you have your own TF Track, you can upload it to History using "Get Data"\
        and then select TF Source = History Element.<p>\
        The tool offers a certain number of useful genomic tracks and multi-tracks to be compared to the TF track. If\
        the genomic track you need is not here, you can upload it to History using "Get Data" and\
        then select Genomic Region = History Element.\
        If you don\'t have a TF track but a specific binding motif, consensus sequence or PWM, you must\
        first build a track with this information and upload it from TF Source = History Element.<p>\
        <p>The following picture illustrates the goal/scope of this tool.<p>'

    @staticmethod
    def isHistoryTool():
        return True

    @staticmethod
    def getFullExampleURL():
        return 'https://hyperbrowser.uio.no/gsuite/u/hb-superuser/p/tfaw---the-transcription-factor-analysis-workbench'

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

    @staticmethod
    def isDebugMode():
        '''
        Specifies whether the debug mode is turned on.
        '''
        return False
