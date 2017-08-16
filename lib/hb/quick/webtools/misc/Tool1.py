import os

from config.Config import DATA_FILES_PATH
from gold.application.LogSetup import setupDebugModeAndLogging
from gold.util.CommonFunctions import mean, prettyPrintTrackName
from quick.webtools.misc.Tool3 import CreateGCFunction
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import MultiGeneralGuiTool, GeneralGuiTool


#Geirs tool:
class Tool1(MultiGeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Geir's ad hoc tools"

    @staticmethod
    def getSubToolClasses():
        return [CreateBpLevelTrackTool, ChrNamesTool, MapTfTool, ScanFastaByPwmTool, PlotFigure1Tool, PlotFigure2Tool, ExtractLocalFdrsBelowThresholdTool, CreateGCFunction, PrunePubmedPaperSummaries, ComputeFdrValues, AliaksanderDemo, NewRunApiDemo, CubeDemo, HotSpotDemo, MultiplyTool, CheckProfileAndDebugStatus, SetGTrackValueColumn, TestRTool, TestGEWriterTool, PlainScatterPlot, RevCompMergeTool, CheckPoissonDistributionTool,MultiplyTool,DemoCatGSuiteTool, AssignGradesTool, AdhocReceptorRepertoirTool, ComputeMeanScoresTool2]


class CreateBpLevelTrackTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Create bp level track: Create bp level function track from segment track"

    @staticmethod
    def getInputBoxNames():
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).
        '''
        return ['Select genome', 'Select segment track','Only consider binary coverage','Value type for output','Out-trackname' ] #Alternatively: [ ('box1','key1'), ('box2','key2') ]


    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()
        '''
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to other
        methods. These are lists of results, one for each input box (in the
        order specified by getInputBoxOrder()).

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - Returns: string

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.

        History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return '__genome__'

    @staticmethod
    def getOptionsBox2(prevChoices):
        return '__track__'

    @staticmethod
    def getOptionsBox3(prevChoices): # Alternatively: getOptionsBoxKey2()
        '''
        See getOptionsBox1().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return ['No (coverage depth track)', 'Yes (binary coverage track)']

    @staticmethod
    def getOptionsBox4(prevChoices):
        return ['As coverage track','Floating point']

    @staticmethod
    def getOptionsBox5(prevChoices):
        return ''

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        genome = choices[0]
        tn = choices[1].split(':')
        if choices[2] == 'Yes (binary coverage track)':
            depthType = 'binary'
            withOverlaps = 'no'
            valDataType = 'bool8'
            useFloatValues = 'False'
        elif choices[2]== 'No (coverage depth track)':
            depthType = 'coverage'
            withOverlaps = 'yes'
            valDataType = 'int32'
            useFloatValues = 'False'
        else:
            raise

        if choices[3] == 'Floating point':
            valDataType = 'float64'
            useFloatValues = 'True'

        outTn = choices[4].replace(':','^')

        analysisDef = 'dummy [dataStat=BpLevelArrayRawDataStat] [bpDepthType=%s] [outTrackName=%s] '% (depthType, outTn) +\
                      '[username=%s] [withOverlaps=%s] [valDataType=%s] [useFloatValues=%s]-> CreateFunctionTrackStat' \
                       % (username, withOverlaps, valDataType, useFloatValues)
        trackNames = [tn]
        regSpec = '*'
        binSpec = '*'

        from gold.application.LogSetup import setupDebugModeAndLogging
        setupDebugModeAndLogging()

        from quick.application.GalaxyInterface import GalaxyInterface
        GalaxyInterface.runManual(trackNames, analysisDef, regSpec, binSpec, genome, galaxyFn=galaxyFn, username=username)

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        return None


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class ChrNamesTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Get list/regions of chromosomes, chromosome arms etc"

    @staticmethod
    def getInputBoxNames():
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).
        '''
        return ['Names/Coordinates', 'Which regions', 'Select genome'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()
        return ['Get names']

    @staticmethod
    def getOptionsBox2(prevChoices): # Alternatively: getOptionsBoxKey2()
        '''
        See getOptionsBox1().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return ['Chromosomes', 'Chromosome arms']

    @staticmethod
    def getOptionsBox3(prevChoices):
        return '__genome__'

    #@staticmethod
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        from quick.util.GenomeInfo import GenomeInfo
        genome = choices[2]

        if choices[0] == 'Get names':
            if choices[1] == 'Chromosomes':
                l = GenomeInfo.getChrList(genome)
            elif choices[1] == 'Chromosome arms':
                regs = GenomeInfo.getChrArmRegs(genome)
                l = [r.val for r in regs]
            print ','.join(l)

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        return None

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
    #def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
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
    #@staticmethod
    #def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    #@staticmethod
    #def getFullExampleURL():
    #    return None
    #
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
    #@staticmethod
    #def getOutputFormat(choices):
    #    '''
    #    The format of the history element with the output of the tool. Note
    #    that html output shows print statements, but that text-based output
    #    (e.g. bed) only shows text written to the galaxyFn file.In the latter
    #    case, all all print statements are redirected to the info field of the
    #    history item box.
    #    '''
    #    return 'html'


class MapTfTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Map between TF ids"

    @staticmethod
    def getInputBoxNames():
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).
        '''
        return ['Type of input','Type of original TF id','Type of output TF id','ID input'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()

        return ['Direct text input']

    @staticmethod
    def getOptionsBox2(prevChoices): # Alternatively: getOptionsBoxKey2()
        return ['Transfac PWM ID (Mxx)']

    @staticmethod
    def getOptionsBox3(prevChoices): # Alternatively: getOptionsBoxKey2()
        return ['TF Name','TF ID']


    @staticmethod
    def getOptionsBox4(prevChoices):
        return ''

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        assert choices[0] == 'Direct text input'
        assert choices[1] == 'Transfac PWM ID (Mxx)'

        if choices[2] == 'TF ID':
            mappingShelf = cls.openTfbsShelve('pwm2TFids.shelf')
        elif choices[2] == 'TF Name':
            mappingShelf = cls.openTfbsShelve('pwm2TFnamesNew.shelf')

        for inputId in choices[3].split(','):
            print inputId, ': ', mappingShelf[inputId]

    @classmethod
    def openTfbsShelve(cls, fn):
        from third_party import safeshelve
        return safeshelve.open(os.path.join(DATA_FILES_PATH, 'tfbs', fn), 'r')

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        return None



class ScanFastaByPwmTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Scan FASTA by PWM to get max score"

    @staticmethod
    def getInputBoxNames():
        return ['Select PWM','Select FASTA file'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    return None

    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()
        return ('__history__',)

    @staticmethod
    def getOptionsBox2(prevChoices):
        return ('__history__',)

    #@staticmethod
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @staticmethod
    def getToolDescription():
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        return ''

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        motifFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[0].split(':'))
        fastaFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[1].split(':'))

        from quick.webtools.tfbs.TestOverrepresentationOfPwmInDna import parseTransfacMatrixFile
        from third_party.MotifTools import Motif
        from third_party.Fasta import load

        countMats = parseTransfacMatrixFile(motifFn)
        #from gold.application.StatRunner import Progress
        #progress = Progress(len(countMats))
        utfil = open(galaxyFn, 'w')
        for motifId, countMat in countMats.items():
            motif = Motif(backgroundD={'A': 0.25, 'C': .25, 'G': .25, 'T': .25} )
            motif.compute_from_counts(countMat,0.1)
            motif.name = motifId


            seqs = load(fastaFn,lambda x:x)
            #concatSeq = ''.join(seqs.values()).upper()
            #print motif.ll
            #print motif.bestscore(seqs[0]), motif.bestscanseq(seqs[0]), motif._scan(seqs[0])
            bestScores = [motif.bestscore(seq.upper()) for seq in seqs.values()]

            print>>utfil,  '\n'.join(['\t'.join([str(key),str(score)]) for key,score in zip(seqs.keys(), bestScores)])

    @staticmethod
    def getOutputFormat(choices):
        return 'tabular'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None


class PlotFigure1Tool(GeneralGuiTool):
    rCode =\
'''plotFig1 = function(fn) {
  r=read.csv(fn,sep='\t')
  plot(r[,2], r[,4], xlim=c(0,0.2), ylim=c(0,0.2),
       xlab='Preserving only the number of TFBS',
       ylab='Preserving empiric inter-TFBS distances',
       main='Do TFBS fall more than expected inside genes?')
  lines(0:1,0:1,lty='dashed')
}
'''

    @staticmethod
    def getToolName():
        return "Plot figure 1 of manuscript"

    @staticmethod
    def getInputBoxNames():
        return ['Select 4-column tabular data for plot (where column 2 and 4 will be used)'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]


    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()
        return ('__history__','tabular')
    #
    #@staticmethod
    #def getOptionsBox2(prevChoices):
    #    return ('__history__',)


    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
        from proto.RSetup import r
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from proto.hyperbrowser.HtmlCore import HtmlCore
        dataFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[0])
        sf = GalaxyRunSpecificFile(['fig1.png'], galaxyFn)
        sf.openRFigure()
        r(PlotFigure1Tool.rCode)(dataFn)
        sf.closeRFigure()
        core = HtmlCore()
        core.begin()
        core.image(sf.getURL() )
        core.end()
        print str(core)

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'

    @staticmethod
    def validateAndReturnErrors(choices):
        from quick.application.ExternalTrackManager import ExternalTrackManager

        if not choices[0]:
            return 'No tabular history elements selected. Please select a history element with 4-column tabular data.'

        dataFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[0])

        if len( open(dataFn).readline().split('\t') ) != 4:
            return 'Selected history element does not contain 4-column tabular data.'


    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.descriptionLine('R-code', cls._exampleText(cls.rCode))
        return str(core)

    @staticmethod
    def isPublic():
        return True

class PlotFigure2Tool(GeneralGuiTool):
    rCode = \
'''plotFig1 = function(fn) {
  r=read.csv(fn, sep='\t')
  up = r[,1]
  ip = r[,2]
  is = r[,3]
  us = r[,4]
  plot(sort(up), type='l',
       xlab='Tests (bins corresponding to the 50 lowest p-values for each assumption)',
       ylab='P-value', ylim=c(0,0.35))
  lines(sort(ip), col='blue', lty='dashed')
  lines(sort(us), col='darkgreen', lty='dotted')
  lines(sort(is), col='red', lty='dotdash')
  legend('bottomright',
         legend=list('Uniform point location',
                     'Preserving inter-point distances',
                     'Uniform segment location',
                     'Preserving inter-segment location'),
         col=c('black','blue','darkgreen','red'), lty=c(1,2,3,4))
}
'''

    @staticmethod
    def getToolName():
        return "Plot figure 2 of manuscript"

    @staticmethod
    def getInputBoxNames():
        return ['Select 4-column tabular data for plot'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]


    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()
        return ('__history__','tabular')
    #
    #@staticmethod
    #def getOptionsBox2(prevChoices):
    #    return ('__history__',)


    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
        from proto.RSetup import r
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from proto.hyperbrowser.HtmlCore import HtmlCore
        dataFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[0])
        sf = GalaxyRunSpecificFile(['fig2.png'], galaxyFn)
        sf.openRFigure()
        r(PlotFigure2Tool.rCode)(dataFn)
        sf.closeRFigure()
        core = HtmlCore()
        core.begin()
        core.image(sf.getURL() )
        core.end()
        print str(core)

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'

    @staticmethod
    def validateAndReturnErrors(choices):
        from quick.application.ExternalTrackManager import ExternalTrackManager

        if not choices[0]:
            return 'No tabular history elements selected. Please select a history element with 4-column tabular data.'

        dataFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[0])

        if len( open(dataFn).readline().split('\t') ) != 4:
            return 'Selected history element does not contain 4-column tabular data.'

    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.descriptionLine('R-code', cls._exampleText(cls.rCode))
        return str(core)

    @staticmethod
    def isPublic():
        return True

class ExtractLocalFdrsBelowThresholdTool(GeneralGuiTool):
    ConvestRCode = \
'''
convest <- function(p,niter=100,plot=FALSE,report=FALSE,file="",tol=1e-06)
# Estimates pi0 using a convex decreasing density estimate
# Input: p=observed p-values,k=number of iterations,
# plot=TRUE plots and report=TRUE writes results of each iteration.
# Returns: An estimate of pi0
# The methology underlying the function can be found in the
# preprint: "Estimating the proportion of true null hypotheses,
# with application to DNA microarray data." that can be downloaded
# from http://www.math.ntnu.no/~mettela/
#  Written by Egil Ferkingstad.
#  Received from Mette Langaas 26 Jun 2004.
#  Modified for limma by Gordon Smyth, 29 Oct 2004, 28 May 2005.
#  Report modified by Marcus Davy, 24 June 2007. Implemented and edited by Gordon Smyth, 9 Sep 2012.
{
  if(!length(p)) return(NA)
  if(any(is.na(p))) stop("Missing values in p not allowed")
  if(any(p<0 | p>1)) stop("All p-values must be between 0 and 1")
  k <- niter
#  accuracy of the bisectional search for finding a new
#  convex combination of the current iterate and the mixing density
  ny <- tol
  p <- sort(p)
  m <- length(p)
  p.c <- ceiling(100*p)/100
  p.f <- floor(100*p)/100
  t.grid <- (1:100)/100
  x.grid <- (0:100)/100
  t.grid.mat <- matrix(t.grid,ncol=1)
  f.hat <- rep(1,101) #f.hat at the x-grid
  f.hat.p <- rep(1,m) #f.hat at the p-values
  theta.hat <- 0.01*which.max(apply(t.grid.mat,1,function(theta) sum((2*(theta-p)*(p<theta)/theta^2))))
  f.theta.hat <- 2*(theta.hat-x.grid)*(x.grid<theta.hat)/theta.hat^2 # f.theta.hat at the x-grid
  f.theta.hat.p <- 2*(theta.hat-p)*(p<theta.hat)/theta.hat^2 # f.theta.hat at the p-values
  i<-1
  j<-0
  thetas <- numeric()
  if(report) cat("j\tpi0\ttheta.hat\t\tepsilon\tD\n", file=file, append=FALSE)
  for (j in 1:k) {
    f.hat.diff <- (f.hat.p - f.theta.hat.p)
    if (sum(f.hat.diff/f.hat.p) > 0)
      eps <- 0
    else {
      l <- 0
      u <- 1
      while (abs(u-l)>ny) {
        eps <- (l+u)/2
        if(sum((f.hat.diff/((1-eps)*f.hat.p+eps*f.theta.hat.p))[f.hat.p>0])<0)
          l <- eps
        else
          u <- eps
      }
    }
    f.hat <- (1-eps)*f.hat + eps*f.theta.hat
    pi.0.hat <- f.hat[101]
    d <- sum(f.hat.diff/f.hat.p)
    if(report) cat(j, "\t",pi.0.hat, "\t",theta.hat,"\t",eps, "\t",d, "\n", file=file, append=TRUE)
    f.hat.p <- 100*(f.hat[100*p.f+1]-f.hat[100*p.c+1])*(p.c-p)+f.hat[100*p.c+1]
    theta.hat <- 0.01*which.max(apply(t.grid.mat,1,function(theta) sum((2*(theta-p)*(p<theta)/theta^2)/f.hat.p)))
    f.theta.hat <- 2*(theta.hat-x.grid)*(x.grid<theta.hat)/theta.hat^2
    f.theta.hat.p <- 2*(theta.hat-p)*(p<theta.hat)/theta.hat^2
    if (sum(f.theta.hat.p/f.hat.p)<sum(1/f.hat.p)) { # check if the Unif[0,1]-density is the new "f.theta.hat"
      theta.hat <- 0
      f.theta.hat <- rep(1,101)
      f.theta.hat.p <- rep(1,m)
    }
    if (sum(thetas==theta.hat)==0) {
      thetas[i] <- theta.hat
      thetas <- sort(thetas)
      i <- i + 1
    }
#    pi.0.hat <- f.hat[101]
    if (plot) {
      plot(x.grid,f.hat,type="l",main=paste(format(round(pi.0.hat,5),digits=5)),ylim=c(0,1.2))
      points(thetas,f.hat[100*thetas+1],pch=20,col = "blue")
    }
  }
  pi.0.hat
}
'''

    @staticmethod
    def getToolName():
        return "For each column in tabular file, extract number of values that are below a given threshold"

    @staticmethod
    def getInputBoxNames():
        return ['Select tabular data', 'FDR treshold','FDR/pi0 estimation method'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]


    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()
        return ('__history__','tabular')

    @staticmethod
    def getOptionsBox2(prevChoices):
        return '0.2'

    @staticmethod
    def getOptionsBox3(prevChoices):
        return ['Use Benjamini & Hochberg (pi0=1)', 'Estimate pi0 by Pounds & Cheng', 'Estimate pi0 by Langaas et al']


    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from proto.RSetup import r
        r('library(pi0)')

        dataFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[0])
        threshold = float(choices[1])
        pi0Method = choices[2]

        rows = [line.split('\t') for line in open(dataFn)]
        headerRow = rows[0][1:] #first element is only header for the column of row headers
        dataRows = rows[1:]
        cols = zip(*dataRows)
        headerCol = cols[0] #ignored
        dataCols = cols[1:]

        pvalColumns = [[float(x) for x in col] for col in dataCols]
        if pi0Method=='Use Benjamini & Hochberg (pi0=1)':
            fdrColumns = [r('p.adjust')( r.unlist(pvals)) for pvals in pvalColumns]
        elif pi0Method =='Estimate pi0 by Pounds & Cheng':
            pi0s = [min(1.0, mean( pvals )*2.0) for pvals in pvalColumns]
            fdrColumns = [r.fdr( r.unlist(pvals),pi0) for pvals,pi0 in zip(pvalColumns, pi0s)]
        elif pi0Method=='Estimate pi0 by Langaas et al':
            #pi0s = [r.convest(r.unlist(pvals)) for pvals in pvalColumns]
            pi0s = [r(ExtractLocalFdrsBelowThresholdTool.ConvestRCode)( r.unlist(pvals) ) for pvals in pvalColumns]
            fdrColumns = [r.fdr( r.unlist(pvals),pi0) for pvals,pi0 in zip(pvalColumns, pi0s)]

        numDiscoveries = [ str(sum([val<=threshold for val in col])) for col in fdrColumns]
        assert len(headerRow)==len(numDiscoveries), (len(headerRow), len(numDiscoveries), headerRow, numDiscoveries)
        outCols = zip(headerRow, numDiscoveries)
        outRows = zip(*outCols)
        open(galaxyFn,'w').write( '\n'.join(['\t'.join(outRow) for outRow in outRows]) )

    @staticmethod
    def getOutputFormat(choices):
        return 'tabular'

    #@staticmethod
    #def validateAndReturnErrors(choices):
    #    return None

    @staticmethod
    def getToolDescription():
        return  '''
        Assumes first line is header line.
        Outputs the number of values per column being equal to or lower than threshold.
        '''

    @staticmethod
    def isPublic():
        return True


class PrunePubmedPaperSummaries(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Prune away extra information from pubmed summary entries"

    @staticmethod
    def getInputBoxNames():

        return ['Original pubmed summary'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey()

        return '',20




    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        import re
        import codecs
        from proto.hyperbrowser.HtmlCore import HtmlCore
        entries = []
        useLine=True
        outF = codecs.open(galaxyFn,'w', 'utf-8')
        outF.write( str(HtmlCore().begin() ) )
        for line in choices[0].split('\n'):
            if re.match('\d{1,2}:.*', line):
                entries.append( line[ re.search(':', line).start() +2:].replace('\r',' ') )
                useLine=True
            elif line.strip() != '' and useLine:
                if re.search('doi:', line):
                    line = line[:re.search('doi:', line).start()]
                    useLine=False
                entries[-1] += line.replace('\r',' ')


        for entry in entries:
            #print type(entry)
            entryComponents = entry.split('.')
            outF.write(entryComponents[0] + '.<i>' + entryComponents[1] + '</i>.' + \
                       '.'.join(entryComponents[2:]) + '<br><br>\n')
            #print ''
        outF.write( str(HtmlCore().end() ) )
        outF.close()


    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'

class ComputeFdrValues(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Adjust input collection of p-values (one p-value per line as input)"

    @staticmethod
    def getInputBoxNames():

        return ['Pvalues', 'Adjustment scheme'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey()

        return '', 15

    @staticmethod
    def getOptionsBox2(prevChoices): # Alternatively: getOptionsBoxKey()
        return ['Benjamini & Hochberg (FDR)']




    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        from proto.RSetup import r
        pvals = [float(x) for x in choices[0].split('\n')]
        assert len(pvals)>1, "Must have more than one p-value to do adjustment."
        if choices[1]== 'Benjamini & Hochberg (FDR)':
            #print 'False discovery rate values:'
            adjPvals = r("p.adjust")(pvals, method='BH')
        else:
            raise

        outF = open(galaxyFn, 'w')
        for adjP in adjPvals:
             outF.write(str(adjP)+'\n')


    @staticmethod
    def getOutputFormat(choices):
        return 'text'


class AliaksanderDemo(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Give me a uniform number between X and Z"

    @staticmethod
    def getInputBoxNames():
        return ["low number", "high number", 'dummy']

    def getOptionsBox1(self):
        return ['0','1']


    def getOptionsBox2(self, prevChoices):
        return ""

    def getOptionsBox3(self, prevChoices):
        return ("__history__",)

    def execute(self, choices, galaxyFn, username=''):
        low = int(choices[0])
        high = int(choices[1])
        from proto.RSetup import r
        rCode='''

        '''
        print r.runif(1, low,high)
        from quick.application.ExternalTrackManager import ExternalTrackManager
        fn = ExternalTrackManager.extractFnFromGalaxyTN(choices[2])
        print open(fn).readlines()
        #print choices[2], repr(choices[2])


from gold.application.HBAPI import doAnalysis, GlobalBinSource, \
    AnalysisSpec, PlainTrack


class NewRunApiDemo(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Demo that new run is working"

    @staticmethod
    def getInputBoxNames():
        return []

    def execute(self, choices, galaxyFn, username=''):
        from quick.statistic.AvgSegLenStat import AvgSegLenStat
        analysisSpec = AnalysisSpec(AvgSegLenStat)
        analysisSpec.addParameter("withOverlaps","no")

        #from gold.track.GenomeRegion import GenomeRegion
        #analysisBins = RegionIter([ GenomeRegion('hg18','chr1',1000,9000000) ])
        analysisBins = GlobalBinSource('hg18')

        tracks = [ PlainTrack(['Genes and gene subsets','Genes','Refseq']) ]

        result = doAnalysis(analysisSpec, analysisBins, tracks)
        resultDict = result.getGlobalResult()
        print "Avg gene length: ", resultDict['Result']

class CubeDemo(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Suggested GUI for selecting how to treat dimensions"

    @staticmethod
    def getInputBoxNames():
        return 'How to treat folder-value 1 of first GSuite, Selected value,How to treat folder-value 1 of second GSuite, Selected value,How to treat folder-value 2 of second GSuite, Selected value'.split(',')

    def getOptionsBox1(self):
        return "Select one value,Show results for each value,Sum across this dimension".split(',')

    def getOptionsBox2(self, prevChoices):
        if prevChoices[-2] == "Select one value":
            return 'tandem,interspersed,low complexity,...'.split(',')

    def getOptionsBox3(self, prevChoices):
        return "Select one value,Show results for each value,Sum across this dimension".split(',')

    def getOptionsBox4(self, prevChoices):
        if prevChoices[-2] == "Select one value":
            return 'abyss,celera,...'.split(',')

    def getOptionsBox5(self, prevChoices):
        return "Select one value,Show results for each value,Sum across this dimension".split(',')

    def getOptionsBox6(self, prevChoices):
        if prevChoices[-2] == "Select one value":
            return 'misjoin,lacking coverage,...'.split(',')

    def execute(self, choices, galaxyFn, username=''):
        pass

class HotSpotDemo(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Tool for generating hotspot regions in temporary form"

    @staticmethod
    def getInputBoxNames():
        return []

    def execute(self, choices, galaxyFn, username=''):
        #tn = 'Genes and gene subsets:Genes:CCDS'.split(',')
        from quick.statistic.HotSpotRegionsStat import HotSpotRegionsStat
        analysisSpec = AnalysisSpec(HotSpotRegionsStat)
        analysisSpec.addParameter("numberOfTopHotSpots",5)

        #from gold.track.GenomeRegion import GenomeRegion
        #analysisBins = RegionIter([ GenomeRegion('hg18','chr1',1000,9000000) ])
        analysisBins = GlobalBinSource('hg18')

        #for loopNum, track in enumerate(GSuiteFile):
        #    ...

        tracks = [ PlainTrack(['Genes and gene subsets','Genes','Refseq']) ]

        result = doAnalysis(analysisSpec, analysisBins, tracks)
        resultDict = result.getGlobalResult()
        regs = resultDict['Result']
        outF = open(galaxyFn, 'w')
        #staticF = GalaxyRunSpecificFile([str(loopNum)], galaxyFn)
        #outF = GalaxyRunSpecificFile.getFile()
        for reg in regs:
            outF.write( '\t'.join([str(reg.chr), str(reg.start), str(reg.end)]) + '\n' )

    @staticmethod
    def getOutputFormat(choices):
        return 'bed'

class MultiplyTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Multiply two numbers'

    @staticmethod
    def getInputBoxNames():
        return [('Number 1', 'num1'),
                ('Number 2', 'num2')]

    @staticmethod
    def getOptionsBoxNum1():
        return '2'

    @staticmethod
    def getOptionsBoxNum2(prevChoices):
        return ['1', '2', '3', '4', prevChoices.num1]

    @staticmethod
    def execute(choices, galaxyFn, username):
        print int(choices.num1) * \
              int(choices.num2)

class CheckProfileAndDebugStatus(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Get settings of profiling and debugging'

    @staticmethod
    def getInputBoxNames():
        return []

    @staticmethod
    def execute(choices, galaxyFn, username):
        from config.Config import DebugConfig
        print 'Debugging: %s' % (DebugConfig)

class SetGTrackValueColumn(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Set name of GTrack column to use as value'

    @staticmethod
    def getInputBoxNames():
        return ['GTrack file', 'Name of value column', 'Value type']

    def getOptionsBox1(self):
        return ('__history__',)

    def getOptionsBox2(self, prevChoices):
        return ''

    def getOptionsBox3(self, prevChoices):
        return 'number,binary,character,category'.split(',')

    
    @staticmethod
    def execute(choices, galaxyFn, username):
        inF = open(ExternalTrackManager.extractFnFromGalaxyTN(choices[0].split(':')) )
        outF = open(galaxyFn,'w')
        outF.write('##value column: %s\n' % choices[1])
        writtenValueType=False
        for line in inF:
            if "track type" in line:
                line = '##track type: valued segments\n'
            if "value type" in line:
                line = '##value type: %s\n' % choices[2]
                writtenValueType=True
            if line.startswith('###') and not writtenValueType:
                outF.write('##value type: %s\n' % choices[2])
            outF.write(line)
        
        
        
    @staticmethod
    def getOutputFormat(choices):
        return 'gtrack'
        
        
class TestRTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Test R interaction'

    @staticmethod
    def getInputBoxNames():
        return []
    
    @staticmethod
    def execute(choices, galaxyFn, username):
        from proto.RSetup import r, robjects
        from numpy import arange
        nums = arange(10)
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
        sf = GalaxyRunSpecificFile(['test.png'],galaxyFn)
        sf.openRFigure()
        r.hist(robjects.FloatVector(nums))
        sf.closeRFigure()
        print sf.getLink('Mitt plott')
        print 'WORKED!'
        
class TestGEWriterTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Test GE writing'

    @staticmethod
    def getInputBoxNames():
        return []
    
    @staticmethod
    def execute(choices, galaxyFn, username):
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
        sf = GalaxyRunSpecificFile(['test'],galaxyFn)
        
        from gold.application.HBAPI import doAnalysis
        from quick.application.UserBinSource import GlobalBinSource
        from quick.statistic.GenericGenomeElementWriterStat import GenericGenomeElementWriterStat
        from gold.track.Track import Track
        from urllib import quote
        
        analysisSpec = AnalysisSpec(GenericGenomeElementWriterStat)
        analysisSpec.addParameter("quotedOutTrackFn", quote(sf.getDiskPath(True),safe="") )
        analysisSpec.addParameter("generatorStatistic","TemporaryGETestStat")
        bins = GlobalBinSource('hg18')
        tracks = [ Track(['Genes and gene subsets','Genes','Refseq']) ]
        setupDebugModeAndLogging()
        res = doAnalysis(analysisSpec, bins, tracks)
        print sf.getLink("TRACK HERE")
        print "Written elements: ", res.getGlobalResult()

class PlainScatterPlot(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Make a simple scatter plot of a two column file'

    @staticmethod
    def getInputBoxNames():
        return ['2-column data']

    @staticmethod
    def getOptionsBox1():
        return ('__history__',)

    @staticmethod
    def execute(choices, galaxyFn, username):
        from quick.application.ExternalTrackManager import ExternalTrackManager
        fn = ExternalTrackManager.extractFnFromGalaxyTN(choices[0])
        col1, col2 = zip(*[ [float(x) for x in line.strip().split('\t')] for line in open(fn)])
        from proto.RSetup import r, robjects
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile

        sf = GalaxyRunSpecificFile(['plot.png'], galaxyFn)
        sf.openRFigure()
        rCol1 = robjects.FloatVector(col1)
        rCol2 = robjects.FloatVector(col2)
        r.plot(rCol1, rCol2, xlab='col1', ylab='col2')
        r.lines(r.lowess(rCol1, rCol2),col="red")
        sf.closeRFigure()
        print sf.getLink('See scatterplot')

class RevCompMergeTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Add counts for reverse complement mutations'

    @staticmethod
    def getInputBoxNames():
        return ['Hierarchical GSuite']

    @staticmethod
    def getOptionsBox1():
        return ('__history__',)

    @staticmethod
    def execute(choices, galaxyFn, username):
        from quick.application.ExternalTrackManager import ExternalTrackManager
        fn = ExternalTrackManager.extractFnFromGalaxyTN(choices[0].split(':'))
        revcomp = dict(zip('ACGT','TGCA'))
        from collections import defaultdict
        mergedCounts = defaultdict(int)
        for line in open(fn):
            parts = line.strip().split()
            if parts[3] in 'GT':
                keyParts = [revcomp[parts[i]] for i in [2,1,0,3,4]]
            else:
                keyParts = parts[:-1]
            mergedCounts[tuple(keyParts)] += int(parts[-1])
        outF = open(galaxyFn,'w')
        for key in sorted(mergedCounts.keys()):
            outF.write( '\t'.join( key[0:3]+ (key[3]+'->'+key[4], str(mergedCounts[key]))) +'\n')

    @staticmethod
    def getOutputFormat(choices):
        return 'gsuite'

class MultiplyTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'multiply'

    @staticmethod
    def getInputBoxNames():
        return ['Number1', 'Number2']

    @staticmethod
    def getOptionsBox1():
        return ['1','5']

    @staticmethod
    def getOptionsBox2(prevChoices):
        return ''

    @staticmethod
    def execute(choices, galaxyFn, username):
        print 'Result is: ', int(choices[0]) * int(choices[1])

class DemoCatGSuiteTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Demo cat gsuite'


    @staticmethod
    def getInputBoxNames():
        return [('Input GSuite', 'gsuite'), ("Input query track", 'queryTrack')]

    @staticmethod
    def getOptionsBoxGsuite():
        return ('__history__',)

    @staticmethod
    def getOptionsBoxQueryTrack(prevChoices):
        return ('__history__',)


    @staticmethod
    def execute(choices, galaxyFn, username):
        genome = 'hg19'
        from quick.statistic.GSuiteSimilarityToQueryTrackRankingsWrapperStat import \
            GSuiteSimilarityToQueryTrackRankingsWrapperStat
        analysisSpec = AnalysisSpec(GSuiteSimilarityToQueryTrackRankingsWrapperStat)
        from quick.gsuite import GSuiteStatUtils
        from quick.statistic.StatFacades import ObservedVsExpectedStat
        analysisSpec.addParameter('pairwiseStatistic',ObservedVsExpectedStat.__name__)
        #             analysisSpec.addParameter('summaryFunc', GSuiteStatUtils.SUMMARY_FUNCTIONS_MAPPER[summaryFunc])
        queryTrackNameAsList = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, choices.queryTrack)
        from gold.track.Track import Track
        queryTrack = Track(queryTrackNameAsList)
        queryTrackTitle = prettyPrintTrackName(queryTrack.trackName).replace('/', '_')

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)

        tracks = [queryTrack] + [Track(x.trackName, trackTitle=x.title) for x in gsuite.allTracks()]

        from gold.util import CommonConstants
        from urllib import quote
        trackTitles = CommonConstants.TRACK_TITLES_SEPARATOR.join(
            [quote(queryTrackTitle)] + [quote(x.title, safe='') for x in gsuite.allTracks()])

        analysisSpec.addParameter('trackTitles', trackTitles)
        analysisSpec.addParameter('queryTracksNum', str(1))

        from quick.application.GalaxyInterface import GalaxyInterface
        analysisBins = GalaxyInterface._getUserBinSource('chr1:1-10m', '*', genome=genome)

        resultsObj = doAnalysis(analysisSpec, analysisBins, tracks)
        results = resultsObj.getGlobalResult()
        allTracks = list(gsuite.allTracks())
        categoryPerTrack = [t.getAttribute('antibody') for t in allTracks]
        print 'Output:'
        print categoryPerTrack
        categorySet = set(categoryPerTrack)
        for cat in categorySet:
            catResults = [list(results.values())[i] for i in range(len(results)) if allTracks[i].getAttribute('antibody')==cat]
            print cat, ': ', min(catResults), '-', max(catResults)



class AssignGradesTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Ad hoc tool for assigning grades to exam evaluation sheets'


    @staticmethod
    def getInputBoxNames():
        return ['Input file (csv)', 'Grade thresholds (five values, comma-separated)']

    @staticmethod
    def getOptionsBox1():
        return ('__history__',)

    @staticmethod
    def getOptionsBox2(prevChoices):
        return ''

    @staticmethod
    def getOutputFormat(choices):
        return 'txt'


    @staticmethod
    def execute(choices, galaxyFn, username):
        fn = ExternalTrackManager.extractFnFromGalaxyTN(choices[0].split(':'))
        allLines = open(fn).readlines()
        header = allLines[0].strip().split(',')
        assert header[0]=='Student nr'
        if not 'Grade' in header:
            header.append('Grade')
            appendGrade = True
        else:
            appendGrade = False
        gradeIndex = header.index('Grade')

        thresholds = [int(x) for x in choices[1].strip().split(',')]
        assert thresholds == sorted(thresholds)

        maxLine = allLines[1].strip().split(',')
        assert maxLine[0] == 'Max'
        if appendGrade:
            maxLine.append('A-F')
        stopTaskColIndex = None if appendGrade else -1
        lineSums = dict([ [line.split(',')[0], sum([float(x) for x in line.split(',')[1:stopTaskColIndex]])] for line in allLines[1:]])
        assert lineSums['Max']==100

        outF = open(galaxyFn,'w')
        for line in [header,maxLine]:
            outF.write(','.join([str(x) for x in line]) + '\n')
        for line in allLines[2:]:
            cols = line.strip().split(',')
            studNr = cols[0]
            scoreSum = lineSums[studNr]
            gradeNum = sum(scoreSum>=x for x in thresholds)
            grade = 'FEDCBA'[gradeNum]
            if appendGrade:
                cols.append(grade)
            else:
                cols[gradeIndex]=grade
            outF.write(','.join(cols)+'\n')
        outF.close()

class CheckPoissonDistributionTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Ad hoc tool for checking poisson distribution of bin counts'


    @staticmethod
    def getInputBoxNames():
        return ['Input file (ad hoc format)', 'saturation value (truncate/remove higher bin counts)']

    @staticmethod
    def getOptionsBox1():
        return ('__history__',)

    @staticmethod
    def getOptionsBox2(prevChoices):
        return ''

    @staticmethod
    def execute(choices, galaxyFn, username):
        from proto.RSetup import robjects, r
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
        fn = ExternalTrackManager.extractFnFromGalaxyTN(choices[0].split(':'))
        maxVal = int(choices[1]) if choices[1]!='' else None
        # for i,line in enumerate(open(fn)):
        #     if '.' in line.strip().split()[2]:
        #         print i, line
        counts = [int(line.strip().split()[2]) for line in open(fn) if not line.startswith('#')]
        if maxVal != None:
            #counts = [min(x,maxVal) for x in counts]
            counts = [x for x in counts if x<=maxVal]

        avg = 1.0*sum(counts)/len(counts)
        print 'min, avg, max: ', min(counts), avg, max(counts)
        print 'plots: '

        rCounts = robjects.IntVector(counts)
        sf = GalaxyRunSpecificFile(['hist.png'],galaxyFn)
        sf.openRFigure()
        r.hist(rCounts,main='Hist all',xlab='Count per bin',ylab='Freq')
        sf.closeRFigure()
        print sf.getLink('Hist')

        subCounts = [x for x in counts if x<=10]
        rSubCounts = robjects.IntVector(subCounts)
        sf2 = GalaxyRunSpecificFile(['hist2.png'],galaxyFn)
        sf2.openRFigure()
        r.hist(rSubCounts,main='Hist 0-10',xlab='Count per bin',ylab='Freq')
        sf2.closeRFigure()
        print sf2.getLink('Histogram between 0 and 10..')

        rCounts = r.rpois(len(rCounts), avg)
        sf3 = GalaxyRunSpecificFile(['hist3.png'],galaxyFn)
        sf3.openRFigure()
        r.hist(rCounts,main='Hist poisson',xlab='Count per bin',ylab='Freq')
        sf3.closeRFigure()
        print sf3.getLink('Histogram for poisson simulated values')


class AdhocReceptorRepertoirTool(GeneralGuiTool):
    MODELS_DICT = {'S: Same frequencies':1,'O: Same order of frequency':2, 'C: Correlation of the order of frequency':3}
    CURVE_FIT_DICT = {'Fractional': 1, 'Exponential':2}
    @staticmethod
    def getToolName():
        return 'Ad hoc tool for assessing receptor repertoirs'


    @staticmethod
    def getInputBoxNames():
        return ['GSuite of receptor repertoires (ad hoc format)', 'Num MC samples', 'Model type', 'Curve fitting function', 'Random seed (empty for no seed)']


    @staticmethod
    def getOptionsBox1():
        return ('__history__',)

    @staticmethod
    def getOptionsBox2(prevChoices):
        return ''

    @staticmethod
    def getOptionsBox3(prevChoices):
        return AdhocReceptorRepertoirTool.MODELS_DICT.keys()

    @staticmethod
    def getOptionsBox4(prevChoices):
        return AdhocReceptorRepertoirTool.CURVE_FIT_DICT.keys()

    @staticmethod
    def getOptionsBox5(prevChoices):
        return ""

    @staticmethod
    def execute(choices, galaxyFn, username):
        ModelText = choices[2]
        clonoFunc = AdhocReceptorRepertoirTool.CURVE_FIT_DICT[choices[3]]
        #Set random seed if needed
        randomSeed = choices[4]
        from gold.util.RandomUtil import getManualSeed, setManualSeed
        if randomSeed and randomSeed != 'Random' and getManualSeed() is None:
            setManualSeed(int(randomSeed))

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        #print choices[0]
        gsuite = getGSuiteFromGalaxyTN(choices[0])
        from gold.gsuite.GSuiteTrack import GSuiteTrack
        fns = [GSuiteTrack(x.uri).path for x in gsuite.allTracks()]
        titles = [x.title for x in gsuite.allTracks()]
        numGSuiteTracks = len(titles)
        numMcSamples = int(choices[1])
        Model = AdhocReceptorRepertoirTool.MODELS_DICT[ModelText ]
        from proto.RSetup import r
        #print r.getwd()
        #r.setwd("/hyperbrowser/src/hb_core_dev3/quick/extra/receptors")
        #print r.getwd()
        #r.source("coeliaki-to-HB.R")
        r.source("/hyperbrowser/src/hb_core_dev3/quick/extra/receptors/coeliaki-to-HB.R")
        #table = r('read.table')(fns[0], header=True, sep="\t")
        param = [0]*7
        header = ['Patient ID', 'Model type', 'Test statistic', 'P-value (mc)', 'N', 'a']
        if Model == 3:
            header.append('c')

        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.tableHeader(header)
        for gSuiteIndex in range(numGSuiteTracks):
            fn = fns[gSuiteIndex]
            numPatientSamples = len(open(fn).readline().split('\t'))-1

            LL = r.list(sim=numMcSamples)
            #print [str(x) for x in [fn,numMcSamples,param,Model,clonoFunc,LL]]
            print r.list(fn,numMcSamples,param,Model,clonoFunc,LL)
            res = r.EstimateClonotypesParameters(fn,numMcSamples,param,Model,clonoFunc,LL)
            #print res
            #res = dict(rawRes.items())
            result = {}
            result['Patient ID'] = titles[gSuiteIndex]
            result['Model type'] = ModelText
            result['P-value (mc)'] = res.rx2('pvalH')#res['pvalH']
            result['Test statistic'] = res.rx2('pvalH')#res['value']
            result['N'] = res.rx2('par')[0] # res['par'][0]

            numParamsForModel = {1:2, 2:1+numPatientSamples, 3:1+2*numPatientSamples}
            assert len(res.rx2('par')) == numParamsForModel[Model]
            if Model == 1:
                result['a'] = res.rx2('pvalH')#res['par'][1]
            if Model >= 2:
                result['a'] = ','.join([str(x) for x in res.rx2('par')[2:2+numPatientSamples]])
            if Model == 3:
                result['c'] = ','.join([str(x) for x in res.rx2('par')[2+numPatientSamples:2+2*numPatientSamples]])
            assert set(header) == set(result.keys()), [set(header), set(result.keys())]
            core.tableLine([str(result[x]) for x in header])

        core.tableFooter()
        print core

class ComputeMeanScoresTool2(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Ad hoc tool for computing mean scores of an exam evaluation sheet having scores from two examiners per student'

    @staticmethod
    def getInputBoxNames():
        return ['Input file (csv)']

    @staticmethod
    def getOptionsBox1():
        return ('__history__',)

    @staticmethod
    def getOutputFormat(choices):
        return 'txt'


    @staticmethod
    def execute(choices, galaxyFn, username):
        # fn = choices[0]
        # from collections import defaultdict
        # scoreLines = defaultdict(list)
        # for line in open(fn).readlines()[2:]:
        #     studnr = line.split(',')[0]
        #     scoreLinesp[studnr].append(line.split(',')[1:])
        # for studnr in scoreLines:
        #     assert len(scoreLines[studnr])==2
        print 'yes'
