from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.extra.tfbs.TfInfo import TfInfo
from quick.application.ProcTrackOptions import ProcTrackOptions
from gold.application.LogSetup import logException, logMessage

#This is a template prototyping GUI that comes together with a corresponding web page.
#

class GeneRegulatorsTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Find which TFs regulate your gene of interest"

    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Type of analysis: ','Genome: ','TF source: ', 'Gene source', 'Flank size: ','Gene of interest (ID): ']

    @staticmethod    
    def getOptionsBox1():
        "Returns a list of options to be displayed in the first options box"
        return ['Get list of TFs binding near specified gene']
        #return ['Get list of TFs binding near (any of the) specified genes']
     
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return ['hg18','mm9']
    
    @staticmethod    
    def getOptionsBox3(prevChoices):
        return TfInfo.getTfTrackNameMappings(prevChoices[1]).keys()

    @staticmethod    
    def getOptionsBox4(prevChoices):
        return ['Ensemble genes']

    @staticmethod    
    def getOptionsBox5(prevChoices):
        return ['0','500','2000','10000']

    @staticmethod
    #@logException
    def getOptionsBox6(prevChoices):
        return ''
        #return 'ENSG00000208234,ENSG00000199674'

    @staticmethod
    def getDemoSelections():
        return ['Get list of TFs binding near specified gene', 'hg18', 'UCSC tfbs conserved', 'Ensembl genes', '10000', 'ENSG00000199674']
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
        #print 'Executing...'
        genome = choices[1]
        tfSource = choices[2]
        geneSource = choices[3]
        flankSize = int(choices[4])
        from quick.extra.tfbs.TFsFromGenes import TFsFromGenes
        TFsFromGenes.findTFsTargetingGenes(genome, tfSource, choices[5].split(','),flankSize, flankSize, geneSource, galaxyFn)

    @staticmethod
    def isPublic():
        return False

    @staticmethod
    def getToolDescription():
        return 'Returns a list of TFs assumed to target your gene of interest.\
                The analysis is based on binding sites (predicted or experimentally determined) of different TFs\
                that falls in the vicinity of the input gene\
                (determined by flanking).'
        
    @staticmethod
    def getToolIllustration():        
        return ['illustrations','tools','GeneRegulators.png']

    @staticmethod
    def isDebugMode():
        return False