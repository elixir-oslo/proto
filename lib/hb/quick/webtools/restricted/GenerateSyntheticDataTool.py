from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.util.CommonFunctions import ensurePathExists
from quick.webtools.GeneralGuiTool import GeneralGuiTool, HistElement
from quick.extra.SimulationTools import PointIter, SimulationPointIter

# author: DD
# date: 07.11.2016

class GenerateSyntheticDataTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Generate synthetics dataset with Poisson distribution"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select genome:', 'genome'),
            ('Select a file with parameters:', 'parameters')
        ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxParameters(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gtrack')

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('synthetic GSuite', 'gsuite')]

    @staticmethod
    def validateAndReturnErrors(choices):
        if not choices.genome:
            return "Please select a genome"
        if not choices.parameters:
            return "Please select a file with parameters"
        return None

    @staticmethod
    def getToolDescription():
        htmlCore = HtmlCore()

        htmlCore.paragraph('This tool provides the possibility to generate synthetic dataset with Poisson distribution.')

        htmlCore.divider()

        htmlCore.paragraph('The input for tool is following:')
        htmlCore.line('- genome, which you can select from the given options')
        htmlCore.line('- file with parameters (gtrack format), which should be given by user')


        htmlCore.paragraph('File with parameters should include information about:')
        htmlCore.line('- chromosome')
        htmlCore.line('- start position')
        htmlCore.line('- end position')
        htmlCore.line('- inter-events distance')
        htmlCore.line('- intra-events distance')
        htmlCore.line('- probability value')

        htmlCore.paragraph('The example of file with parameters:')

        htmlCore.paragraph('''
                ##Track type: points <br \>
                ###seqid        start   end     inter   intra   prob <br \>
                ####genome=hg19 <br \>
                chr1	0	100000	0.0001	0	1
        ''')
        htmlCore.line(', where first three lines are a header, the fourth line contains the information about'
                      'region (chromosome, start, end position) and values ' \
                      '(inter-, intra-mutations, probability) for which will be calculated synthetic dataset.')

        htmlCore.divider()

        htmlCore.line('IMPORTANT INFORMATION')
        htmlCore.line('The file can contains more than one line with parameters, but the calculated simulated datasets ' \
                      'for every regions are merged together at the end.')

        htmlCore.divider()

        htmlCore.paragraph('The output for tool is a GSuite containing one simulated dataset.')

        htmlCore.divider()

        htmlCore.line('IMPORTANT OTHER TOOLS')
        htmlCore.line('To upload your own file with parameters (available later as an element in the history) use the tool called:' \
                      ' Upload file ')

        return str(htmlCore)

    @staticmethod
    def isPublic():
        return True

    # @staticmethod
    # def getFullExampleURL():
    #     return None


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        genome = choices.genome
        parameters = choices.parameters

        dataOut = cls.readGTrack(parameters)
        cls.generateSynGSuite(dataOut, galaxyFn, genome)

        print 'Gsuite with synthetic dataset is in the history.'

    @classmethod
    def readGTrack(cls, parameters):
        # change for gtrack
        dataOut = []
        with open(ExternalTrackManager.extractFnFromGalaxyTN(parameters.split(':')), 'r') as f:
            for x in f.readlines():
                xx = x.strip('\n')
                if not '#' in xx:
                    data = xx.split('\t')
                    if len(data) == 6:
                        dataOut.append(data)

        f.closed

        return dataOut

    @classmethod
    def generateSynGSuite(cls, dataOut, galaxyFn, genome):
        outGSuite = GSuite()
        g = SimulationPointIter()
        newData = ''
        chrNum = 0
        for chr in dataOut:

            # fileName = 'syn-chr' + 'iInterR-' + str(chr[0]) + 'st-' + str(chr[1]) + 'end-' + str(
            #     chr[2]) + 'iInterR-' + str(chr[3]) + 'iIntraR-' + str(chr[4]) + 'prob-' + str(chr[5]) + '--' + str(
            #     chrNum)

            fileName = 'syn-' + str(chr[0]) + ',' + str(chr[1]) + ',' + str(chr[2]) + ',' + str(chr[3]) +',' + str(chr[4]) +',' + str(chr[5])

            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=fileName,
                                                suffix='bed')

            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)

            g.createChrTrack(genome, chr[0], PointIter, outFn, chr[3], chr[4], chr[5], chr[1], chr[2])

            with open(outFn, 'r') as outputFile:
                newData += ''.join(outputFile.readlines())

            chrNum += 1

            if chrNum == len(dataOut):
                with open(outFn, 'w') as outputFile:
                    outputFile.write(newData)
                outGSuite.addTrack(GSuiteTrack(uri, title=''.join(fileName), genome=genome))
        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['synthetic GSuite'])





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
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by AutoConfig.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #

    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether the debug mode is turned on.
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
