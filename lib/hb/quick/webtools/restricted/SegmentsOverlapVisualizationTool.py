from gold.gsuite import GSuiteConstants
from gold.origdata.BedComposer import BedComposer
from gold.origdata.GESourceWrapper import ElementModifierGESourceWrapper
from gold.origdata.TrackGenomeElementSource import FullTrackGenomeElementSource
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool

# Author: Diana Domanska


#instead of Track1, Track2 I should put GSuite

'''
Input:
1 - Reference track
2 - Tracks

Calculation:
Calculate overlaps in segments among Reference track and other tracks
Give colors for segments which are overlaped

Output:
Bed file

'''

#Class Color keep information about RGB colors
class Color(object):
    def __init__(self):
        self.colorList = []
    def addColor(self, r, g, b):
        color = (r, g, b)
        self.colorList.append(color)
    def getRGB(self, pos):
        return str(self.colorList[pos][0]) + ',' + str(self.colorList[pos][1]) + ',' + str(self.colorList[pos][2])

colorTab = Color()
colorTab.addColor(0, 0, 0)
colorTab.addColor(255, 215, 0)
colorTab.addColor(205, 104, 137)
colorTab.addColor(0, 0, 255)
colorTab.addColor(139, 102, 139)
colorTab.addColor(107, 142, 35)
colorTab.addColor(0, 255, 255)
colorTab.addColor(255, 165, 0)
colorTab.addColor(121, 205, 205)
colorTab.addColor(0, 199, 140)
colorTab.addColor(125, 199, 50)


#Class MyElementModifier give a color and copy tracks
class MyElementModifier(ElementModifierGESourceWrapper):
    def __init__(self, geSource, segCoverageProp , genome = None):
        super(MyElementModifier, self).__init__(geSource, genome=genome)
        self._segCoverageProp = segCoverageProp
        # init of extra class members, as needed

    def _iter(self):
        from collections import deque
        self._geQueue = deque()

    def _mustSplit(self, ge, i):
        counter = 0
        for j in range(0, len(self._segCoverageProp)):
            if self._segCoverageProp[j][i] > 0:
                counter+=1

        if counter > 1:
            return True
        else:
            return False

    def _splitAndColor(self, ge, i):
        listGe = []
        
        #FIXME: sum is a built-in function in Python, it is not advisable to be used as a variable name
        sumVal=0.00000000001 #FIXME: Why initialized to this value?

        for j in range(0, len(self._segCoverageProp)):
            sumVal += float(self._segCoverageProp[j][i])

        startNew = 0
        endNew = ge.start
        start = ge.start
        end = ge.end

        for j in range(0, len(self._segCoverageProp)):

            if self._segCoverageProp[j][i] > 0:
                self._segCoverageProp[j][i] = self._segCoverageProp[j][i] / sumVal
                ge2 = ge.getCopy()

                if j==0:
                    startNew = start
                else:
                    startNew = endNew

                if j == len(self._segCoverageProp)-1:
                    endNew = end
                else:
                    endNew = startNew + int(self._segCoverageProp[j][i]*((end-start)))

                ge2.start = startNew
                ge2.end = endNew
                ge2.itemrgb = colorTab.getRGB(j+1)

                listGe.append(ge2)

        return listGe

    def next(self):

        try:
            brt, ge, i = self._brtAndGeIter.next()
            if not self._mustSplit(ge, i):
                ge.itemrgb = colorTab.getRGB(0)
                self._geQueue.append(ge)
            else:
                for newGe in self._splitAndColor(ge, i):
                    #newGe.itemrgb = colorTab.getRGB(int(newGe.itemrgb))
                    self._geQueue.append(newGe)

        except StopIteration:
            pass

        try:
            ge = self._geQueue.popleft()
            return ge
        except IndexError:
            raise StopIteration

#future iter1
#class SegmentsOverlapVisualizationTool(UserBinSelector):
class SegmentsOverlapVisualizationTool(GeneralGuiTool):
    exception = None

    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]
    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    TRACK_ALLOWED_TRACK_TYPES = [GSuiteConstants.SEGMENTS, GSuiteConstants.VALUED_SEGMENTS]


    @staticmethod
    def getToolName():
        return "Color-code query segments based on overlap against reference tracks"

    @staticmethod
    def getInputBoxNames():


        return [('Select genome','targetTrackGenome'), \
                ('Select query track from HyperBrowser repository','targetTrack'), \
                ('Select reference GSuite file from history', 'refTrackCollection'), \
                ('Colors:', 'colors')
                ]
                #future iter1
                #+ UserBinSelector.getUserBinInputBoxNames()

    @staticmethod
    def getOptionsBoxTargetTrackGenome():
        return GeneralGuiTool.GENOME_SELECT_ELEMENT

    @staticmethod
    def getOptionsBoxTargetTrack(prevChoices): # refTrack
        return GeneralGuiTool.TRACK_SELECT_ELEMENT

    @staticmethod
    def getOptionsBoxRefTrackCollection(prevChoices): # history
        #return '__history__', 'gsuite'
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxColors(cls, prevChoices):

        if not prevChoices.refTrackCollection:
            return

        start = '<div style="float:left;width:50px; height:20px; margin-right:5px; background-color:rgb('
        end = ')"></div>'

        try:
            refGSuite = getGSuiteFromGalaxyTN(prevChoices.refTrackCollection)
        except Exception as e:
            cls.exception = str(e)
            return

        maxSize = 10
        size = refGSuite.numTracks()
        if size > maxSize:
            errorString = 'Selected GSuite must have at most %s tracks' %maxSize
            errorString += '.<br /> Current number of tracks = ' + str(refGSuite.numTracks())
            cls.exception = errorString
            return

        col = [['Track','Color']]
        i=1
        for trackTitle in refGSuite.allTrackTitles():
            c=[]
            c.append(trackTitle)
            c.append(start + colorTab.getRGB(i) + end)
            col.append(c)
            i+=1

        return col

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        genome = choices.targetTrackGenome
        queryTrackName = choices.targetTrack.split(':')

        from quick.multitrack.MultiTrackCommon import getGSuiteDataFromGalaxyTN
        trackTitles, refTrackNameList, genome = getGSuiteDataFromGalaxyTN(choices.refTrackCollection)

        regSpec = 'track'
        binSpec = choices.targetTrack

        #future iter1
        #regSpec, binSpec = UserBinSelector.getRegsAndBinsSpec(choices)

        results = []
        for refTrack in refTrackNameList:
            analysisDef = '-> ProportionCountStat'
            res = GalaxyInterface.runManual([refTrack], analysisDef, regSpec, binSpec, genome, username=username, galaxyFn=galaxyFn) # res is of class Results
            segCoverageProp = [res[seg]['Result'] for seg in res.getAllRegionKeys()]#to heatmap
            results.append(segCoverageProp)


        geSource = FullTrackGenomeElementSource(genome,  queryTrackName)
        modGeSource = MyElementModifier(geSource, results, genome)
        composer = BedComposer(modGeSource, extraTrackLineAttributes={'itemRgb': '"On"'})
        composer.composeToFile(galaxyFn)

    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True


    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        if cls.exception:
            return cls.exception

        #check track
        errorString = GeneralGuiTool._checkTrack(choices, 'targetTrack', 'targetTrackGenome')
        if errorString:
            return errorString

        genome, tn, tf = GeneralGuiTool._getBasicTrackFormat(choices, 'targetTrack', 'targetTrackGenome')
        errorString = ''
        from os import linesep
        if tf not in SegmentsOverlapVisualizationTool.TRACK_ALLOWED_TRACK_TYPES:
            errorString += '%s is not a supported track type for this tool. Supported track types are ' %tf
            errorString += str(SegmentsOverlapVisualizationTool.TRACK_ALLOWED_TRACK_TYPES) + linesep
            return errorString

        if choices.refTrackCollection is not None:

            targetTrackGenome = choices.targetTrackGenome
            errorString = GeneralGuiTool._checkGSuiteFile(choices.refTrackCollection)
            if errorString:
                return errorString

            refGSuite = getGSuiteFromGalaxyTN(choices.refTrackCollection)

            #check genome
            errorString = GeneralGuiTool._checkGenomeEquality(targetTrackGenome, refGSuite.genome)
            if errorString:
                return errorString

            errorString = GeneralGuiTool._checkGSuiteRequirements \
                (refGSuite,
                 SegmentsOverlapVisualizationTool.GSUITE_ALLOWED_FILE_FORMATS,
                 SegmentsOverlapVisualizationTool.GSUITE_ALLOWED_LOCATIONS,
                 SegmentsOverlapVisualizationTool.GSUITE_ALLOWED_TRACK_TYPES,
                 SegmentsOverlapVisualizationTool.GSUITE_DISALLOWED_GENOMES)
            if errorString:
                return errorString
            #number of tracks

            errorString = GeneralGuiTool._checkGSuiteTrackListSize(refGSuite, maxSize=10)
            if errorString:
                return errorString
        else:
            return None

        #errorString = GeneralGuiTool._checkTrack(choices, genome, ...)
        #if errorString
        #    return errorString

        #errorString = GeneralGuiTool._checkGSuiteFile(choices.history)
        #if not errorString:
        #    return errorString
        #
        #
        #errorString = GeneralGuiTool._checkGenomeEquality()
        #
        #
        #galaxyFn = choices.history.split(':')
        #gSuiteFn = ExternalTrackManager.extractFnFromGalaxyTN(galaxyFn)
        #errorString = GeneralGuiTool._checkGSuiteTrackListSize(gSuiteFn)

        #validate chromosme arms
        #from quick.webtools.UserBinSelector import UserBinSelector

    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    #@staticmethod
    #def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()

        core.paragraph('This tool computes the proportions of overlap between the segments '
                       'of a query track against each track in a collection of reference tracks '
                       'described in a GSuite file. The overlap proportions are output in a '
                       'BED file with the query segments, where each query segment is partitioned '
                       'and colored according to the overlap with each reference track.')

        core.divider()
        core.paragraph('To carry out the analysis, please follow these steps:')
        core.orderedList(['Select a genome build. Both the query track and the reference tracks'
                          'need to use the same genome build.',
                          'Select a query track from the HyperBrowser repository',
                          'Select a reference track collection as a GSuite file from history',
                          'Every track from the GSuite file is represented by a separate color, '
                          'presented to the user in a table.',
                          'Click "Execute"'])

        core.divider()
        core.paragraph('The resulting BED file can be visualized in external genome browsers. '
                       'To browse the segments, click the title of the resulting history element '
                       'and click "display at UCSC main". The UCSC Genome Browser will appear, '
                       'with the segments with color-coding imported as a track.')

        core.divider()
        core.smallHeader('Requirements for query track')
        core.descriptionLine('Track types', ', '.join(cls.TRACK_ALLOWED_TRACK_TYPES), emphasize=True)


        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
                                      disallowedGenomes=cls.GSUITE_DISALLOWED_GENOMES)

        return str(core)
        #
        #htmlCore.divBegin(divId ='toolExample')
        #htmlCore.line('<b>Example</b>')
        #htmlCore.line('<b>Input:</b>')
        #htmlCore.line('Genome build: Human Feb. 2009 (GRCh37/hg19) (hg19)')
        #htmlCore.line('Select track: Phenotype_and_disease_associations:Assorted_experiments:Virus_integration,_HPV_specific,_Kraus_et_al')
        #htmlCore.line('Select GSuite file from history: Genes and gene subsets:Genes')
        #htmlCore.line('<b>Output:</b>')
        #htmlCore.line('BED file with specific colors for overlaped segments:')
        #htmlCore.line("""
        #<pre>
        #track name=Phenotype_and_disease_associations:Assorted_experiments:Virus_integration,_HPV_specific,_Kraus_and_Schmitz,_including_50kb_flanks itemRgb="On"
        #chr1	9498749	9598750	.	0	-	0	0	0,0,0
        #chr1	10647467	10697468	.	0	-	0	0	255,215,0
        #chr1	10697468	10747468	.	0	-	0	0	205,104,137
        #chr1	14421006	14521007	.	0	-	0	0	0,0,0
        #chr1	24678924	24729089	.	0	+	0	0	255,215,0
        #chr1	24729089	24778925	.	0	+	0	0	205,104,137
        #chr1	94938092	94988048	.	0	+	0	0	255,215,0
        #</pre>
        #""")
        #
        #htmlCore.divEnd()
        #
        #return htmlCore

    @staticmethod
    def getToolIllustration():
        '''
        Specifies an id used by StaticFile.py to reference an illustration file
        on disk. The id is a list of optional directory names followed by a file
        name. The base directory is STATIC_PATH as defined by Config.py. The
        full path is created from the base directory followed by the id.
        '''
        return ['div','color_code_ucsc.png']

    @staticmethod
    def getFullExampleURL():
        return 'u/hb-superuser/p/visualizing-segments-overlapping-against-reference-tracks---example'

    #@classmethod
    #def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'bed'#some problem with bed
