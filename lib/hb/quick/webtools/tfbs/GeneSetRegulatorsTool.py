from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.extra.tfbs.TfInfo import TfInfo
from quick.application.ProcTrackOptions import ProcTrackOptions
from gold.application.LogSetup import logException, logMessage
from quick.extra.tfbs.TFsFromGenes import TFsFromGenes
import re
#This is a template prototyping GUI that comes together with a corresponding web page.
#

class GeneSetRegulatorsTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Find which TFs regulate your genes of interest"

    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Type of analysis: ','Genome: ','TF source: ', 'Gene source', 'Flank size: ','Genes of interest (comma-separated IDs): ']

    @staticmethod    
    def getOptionsBox1():
        "Returns a list of options to be displayed in the first options box"
        #return ['Get list of TFs overrepresented in regions near genes of the specified gene set']
        #return ['Get list of TFs binding near specified gene']
        return ['Get list of TFs binding near (any of the) specified genes']
     
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return ['hg18','mm9']#,'hg19']
    
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
        #return 'ENSG00000124097'
        #return 'ENSG00000208234,ENSG00000199674'
        return ''
    @staticmethod
    def getDemoSelections():
        return ['Get list of TFs binding near specified gene', 'hg18', 'UCSC tfbs conserved', 'Ensembl genes', '10000', 'ENSG00000208234,ENSG00000199674']
        
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
        flankSize = int(choices[4])
        genes = [v for v in re.split('[, \n\t]', choices[5]) if v.strip()!='']
        #TFsFromGenes.findOverrepresentedTFsFromGeneSet('hg18', 'UCSC tfbs conserved', ['ENSGflankSizeflankSizeflankSizeflankSizeflankSize2flankSize8234','ENSGflankSizeflankSizeflankSizeflankSizeflankSize199674'],flankSize, flankSize, galaxyFn)
        #TFsFromGenes.findOverrepresentedTFsFromGeneSet('hg18', tfSource, choices[5].split(','),flankSize, flankSize, 'Ensembl', galaxyFn)
        from quick.extra.tfbs.TFsFromGenes import TFsFromGenes
        #TFsFromGenes.findOverrepresentedTFsFromGeneSet('hg18', tfSource, choices[5].split(','),flankSize, flankSize, 'Ensembl', galaxyFn)
        TFsFromGenes.findTFsTargetingGenes(genome, tfSource, genes,flankSize, flankSize, 'Ensembl', galaxyFn)
    
    @staticmethod
    def isPublic():
        return True

    @staticmethod
    def getToolDescription():
        return 'Returns a list of TFs assumed to target your genes of interest.\
                The analysis is based on binding sites (predicted or experimentally determined) of different TFs\
                that falls in the vicinity (determined by flanking) of the input gene set.'
        
    @staticmethod
    def getToolIllustration():
        return ['illustrations','tools','GeneSetRegulators.png']
        #si = StaticImage(['illustrations','Tools','TfTargets'])

    
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        if choices[5].strip() == '':
            return ''