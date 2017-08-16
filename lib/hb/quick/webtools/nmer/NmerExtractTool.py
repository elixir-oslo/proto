from quick.application.GalaxyInterface import GalaxyInterface
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool


#This is a template prototyping GUI that comes together with a corresponding web page.
#

class NmerExtractTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Generate k-mer occurrence track"

    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Genome build: ','K-mer (any length): ', 'Region of the genome: ']

    @staticmethod
    def getOptionsBox1():
        "Returns a list of options to be displayed in the first options box"
        return '__genome__'

    @staticmethod
    def getOptionsBox2(prevChoices):
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)
        '''
        return ''

    @staticmethod
    def getOptionsBox3(prevChoices):
        return '*'

    #@staticmethod
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod
    #def getOptionsBox4(prevChoices):
    #    return ['']

    @staticmethod
    def getDemoSelections():
        return ['sacCer1','tacg','chr1:1-100k']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        genome = choices[0]
        nmer = choices[1].lower()
        regSpec = choices[2]
        binSpec = '*'
        trackName = GenomeInfo.getPropertyTrackName(genome, 'nmer') + [str(len(nmer))+'-mers',nmer]
        assert galaxyFn is not None
        GalaxyInterface.extractTrackManyBins(genome, trackName, regSpec, binSpec, True, 'point bed', False, False, galaxyFn)

    @staticmethod
    def isPublic():
        return True
    #
    @staticmethod
    def getToolDescription():
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.paragraph('Extract occurrences of a given k-mer in a specified region along the selected genome. K-mer occurrence track is extracted as a BED file.')
        core.divider()
        core.highlight('K-mer')
        core.paragraph('A string based on only the following characters: a, c, g, t, A, C, G, T. Eventual use of case has no effect.')
        core.divider()
        core.highlight('Region of the genome')
        core.paragraph('Region specification as in UCSC Genome browser. * means whole genome. k and m denotes thousand and million bps, respectively. E.g chr1:1-20m')
        return str(core)

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        genome, errorStr = NmerExtractTool._getGenomeChoice(choices, 0)
        if errorStr:
            return errorStr

        nmer = choices[1]
        if nmer.strip() == '':
            return 'Please type in a k-mer of any length'

        from gold.extra.nmers.NmerTools import NmerTools
        if not NmerTools.isNmerString(nmer):
            return NmerTools.getNotNmerErrorString(nmer)

        from quick.application.UserBinSource import parseRegSpec
        try:
            parseRegSpec(choices[2], choices[0])
        except Exception, e:
            return e

    #
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    return True

    @staticmethod
    def getOutputFormat(choices=None):
        return 'bed'
