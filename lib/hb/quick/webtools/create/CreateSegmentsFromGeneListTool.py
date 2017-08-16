from gold.application.GalaxyInterface import GalaxyInterface
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ProcTrackOptions import ProcTrackOptions
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool


#This is a template prototyping GUI that comes together with a corresponding web page.
#

class CreateSegmentsFromGeneListTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Generate segment track from gene IDs"

    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Genome: ', 'Enter gene lists (Ensembl IDs): ']

    @staticmethod    
    def getOptionsBox1():
        "Returns a list of options to be displayed in the first options box"
        return '__genome__'
    
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return '', 7
    
    #@staticmethod    
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']
    @staticmethod
    def getDemoSelections():
        return ['hg18','ENSG00000208234,ENSG00000199674']
       
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
        genome = choices[0]
        genes = choices[1]
    
        genelist = []
        for geneLine in genes.split('\n'):
            for gene in geneLine.split(','):
                gene = gene.strip()
                if gene != '':
                    genelist.append(gene)
                    
        GalaxyInterface.getEnsemblGenes(genome, genelist, galaxyFn)
        
    @staticmethod
    def getToolDescription():
        return str(HtmlCore().paragraph('''
        This tool creates a BED file with the segments corresponding to particular genes.    
        Just paste a list of ENSEMBL IDs in the box, and click Execute.</p>
        '''))
    
    @staticmethod
    def isPublic():
        return True

    @staticmethod    
    def getOutputFormat(choices=None):
        return 'bed'

    @staticmethod
    def validateAndReturnErrors(choices):
        genome, errorStr = CreateSegmentsFromGeneListTool._getGenomeChoice(choices, 0)
        if errorStr:
            return errorStr
            
        ensemblTn = GenomeInfo.getEnsemblTrackName(genome)
        if not ProcTrackOptions.isValidTrack(genome, ensemblTn):
            return 'The selected genome have not been set up with a Ensembl gene track. If you require this functionality for the selected genome, please contact the HyperBrowser team.'
        
        if choices[1].strip() == '':
            return 'Please enter a list of genes (using Ensembl IDs)'
    
    #@staticmethod
    #def getToolDescription():
    #    return ''
    #    
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
