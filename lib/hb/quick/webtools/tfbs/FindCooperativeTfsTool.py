from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.extra.tfbs.TfInfo import TfInfo
from quick.application.ProcTrackOptions import ProcTrackOptions
from gold.application.LogSetup import logException, logMessage
from quick.extra.tfbs.TFsFromGenes import TFsFromGenes
from quick.application.ExternalTrackManager import ExternalTrackManager
from gold.util.CommonFunctions import getOrigFns
from quick.extra.tfbs.TFsFromGenes import TFsFromRegions


class FindCooperativeTfsTool(GeneralGuiTool):

    @staticmethod
    def getToolName():
        return "Find cooperative TFs"

    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Genome:','Source of seed TF:','Seed TF: ','Flank size: ', 'Source of potentially cooperative TFs:']

    @staticmethod    
    def getOptionsBox1(): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return '__genome__'

    @staticmethod    
    def getOptionsBox2(prevChoices):
        installedSources = TfInfo.getTfTrackNameMappings(prevChoices[0]).keys()
        return installedSources + ['TFBS from history'] 

    @staticmethod
    def getOptionsBox3(prevChoices):
        seedSource = prevChoices[1]
        if seedSource == 'TFBS from history':
            return ('__history__','bed')
        else:
            genome = prevChoices[0]
            tfSourceTN = TfInfo.getTfTrackNameMappings(genome)[ prevChoices[1] ]
            subtypes = ProcTrackOptions.getSubtypes(genome, tfSourceTN, True)
            return subtypes
     

    @staticmethod    
    def getOptionsBox4(prevChoices):
        return ''

    @staticmethod    
    def getOptionsBox5(prevChoices):
        return TfInfo.getTfTrackNameMappings(prevChoices[0]).keys()

    #@staticmethod
    #def getDemoSelections():
    #    return ['Get list of TFs binding near specified gene', 'hg18', 'UCSC tfbs conserved', 'Ensembl genes', '10000', 'ENSG00000208234,ENSG00000199674']
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        #'Genome:','Source of seed TF:','Seed TF: ','Flank size: ', 'Source of potentially cooperative TFs:'
        #genome
        
        genome = choices[0]
        seedSource = choices[1]
        seedTfTnInput = choices[2]
        if seedSource == 'TFBS from history':
            seedFn = ExternalTrackManager.extractFnFromGalaxyTN(seedTfTnInput.split(':'))
        else:
            tfTrackNameMappings = TfInfo.getTfTrackNameMappings(genome)
            seedTfTn = tfTrackNameMappings[seedSource] + [seedTfTnInput]
            #tfTrackName = tfTrackNameMappings[tfSource] + [selectedTF]
            seedFns = getOrigFns(genome, seedTfTn, '')
            assert len(seedFns) == 1
            seedFn = seedFns[0]
            
        flankSize = choices[3]
        flankSize = int(flankSize) if flankSize != '' else 0
        cooperativeTfSource = choices[4]
        #flankSize = int(choices[4])
        #TFsFromGenes.findOverrepresentedTFsFromGeneSet('hg18', 'UCSC tfbs conserved', ['ENSGflankSizeflankSizeflankSizeflankSizeflankSize2flankSize8234','ENSGflankSizeflankSizeflankSizeflankSizeflankSize199674'],flankSize, flankSize, galaxyFn)
        #TFsFromGenes.findOverrepresentedTFsFromGeneSet('hg18', tfSource, choices[5].split(','),flankSize, flankSize, 'Ensembl', galaxyFn)
        
        #TFsFromRegions.findOverrepresentedTFsFromGeneSet(genome, tfSource, ensembleGeneIdList,upFlankSize, downFlankSize, geneSource, galaxyFn)
        
        #TFsFromGenes.findTFsTargetingGenes('hg18', tfSource, choices[5].split(','),flankSize, flankSize, 'Ensembl', galaxyFn)

        TFsFromRegions.findTFsOccurringInRegions(genome, cooperativeTfSource, seedFn, flankSize, flankSize, galaxyFn)
    
    @staticmethod
    def isPublic():
        return True

    @staticmethod
    def getToolDescription():
        return 'Based on a seed TF, returns a list of other TFs that binds in the vicinity of the seed TF'
        
    #@staticmethod
    #def getToolIllustration():
        #return ['illustrations','tools','GeneSetRegulators.png']
        #si = StaticImage(['illustrations','Tools','TfTargets'])

    
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        genome = choices[0]
        seedSource = choices[1]
        seedTfTnInput = choices[2]

        if seedSource != 'TFBS from history':
            tfTrackNameMappings = TfInfo.getTfTrackNameMappings(genome)
            seedTfTn = tfTrackNameMappings[seedSource] + [seedTfTnInput]
            #tfTrackName = tfTrackNameMappings[tfSource] + [selectedTF]
            if len(getOrigFns(genome, seedTfTn,'')) != 1:
                return 'Sorry. Only seed TFs that are internally represented as single files are currently supported. Please contact the HB team for assistance if needed. Track name that was not supported: ' + ':'.join(seedTfTn)
            
