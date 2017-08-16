from quick.util.CommonFunctions import createHyperBrowserURL
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool


#This is a template prototyping GUI that comes together with a corresponding web page.
#

class NmerAnalyzeTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Analyze k-mer occurrences"

    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Genome build: ','K-mer (any length): ']

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
    
    #@staticmethod    
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']
    
    @staticmethod
    def isRedirectTool():
        return True
    
    @staticmethod
    def getRedirectURL(choices):
        genome = choices[0]
        return createHyperBrowserURL(genome, GenomeInfo.getNmerTrackName(genome) + [choices[1].lower()], [''])
    
    @staticmethod
    def getDemoSelections():
        return ['sacCer1','tacg']
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
        print 'Executing...'

    @staticmethod
    def isPublic():
        return True
    #
    @staticmethod
    def getToolDescription():
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.paragraph('Analyze occurrences of a given k-mer along the genome, either in itself or in relation to other genomic tracks.')
        core.divider()
        core.paragraph('First, select a genome and k-mer of interest. Then a full analysis specification page appears, where one can directly start a basic analysis or specify further details on the analysis of interest.')
        core.divider()
        core.highlight('K-mer')
        core.paragraph('A string based on only the following characters: a, c, g, t, A, C, G, T. Eventual use of case has no effect.')
        return str(core)
        
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        
        if choices[0] in [None, '']:
            return 'Please select a genome build'
        
        nmer = choices[1]
        if nmer.strip() == '':
            return 'Please type in a k-mer'
        from gold.extra.nmers.NmerTools import NmerTools
        if not NmerTools.isNmerString(nmer):
            return NmerTools.getNotNmerErrorString(nmer)
    #    
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
