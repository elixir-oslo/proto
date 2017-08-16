from quick.webtools.GeneralGuiTool import GeneralGuiTool, HistElement
from quick.application.GalaxyInterface import GalaxyInterface
from gold.gsuite.GSuite import GSuite
from gold.description.TrackInfo import TrackInfo
from gold.gsuite.GSuiteTrack import HbGSuiteTrack, GSuiteTrack
from gold.gsuite import GSuiteComposer

# This is a template prototyping GUI that comes together with a corresponding
# web page.


class CreateKmersTool(GeneralGuiTool):

    @staticmethod
    def getToolName():
        return 'Create k-mer tracks'
    
    @staticmethod
    def getInputBoxNames():
        return [
                ('Select genome', 'genome'),
                ('Input sequences (one per line)', 'seqs')
                ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxSeqs(prevChoices):
        return ('',20) 

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        seqs = [s.strip() for s in choices.seqs.splitlines()]
        trackNameList = []
        for nmer in seqs: 
            GalaxyInterface.createNmerTrack(choices.genome, nmer)
            trackNameList.append(['Sequence', 'K-mers', str(len(nmer)) + '-mers', nmer])
        #example trackName = ['Sequence', 'K-mers', '7-mers', 'agagaga']
        outGSuite = GSuite()
        for trackName in trackNameList:
            trackType = TrackInfo(choices.genome, trackName).trackFormatName.lower()
            hbUri = HbGSuiteTrack.generateURI(trackName=trackName)
            outGSuite.addTrack(GSuiteTrack(hbUri, title=' '.join(['Nmer track'] + trackName[-1:]), trackType=trackType, genome=choices.genome))
            
        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['Kmers GSuite'])
        
    @staticmethod
    def validateAndReturnErrors(choices):
        errorStr = GeneralGuiTool._checkGenome(choices.genome)
        if errorStr:
            return errorStr
        
        if not choices.seqs:
            return 'Please enter at least one sequence'
        
#     @staticmethod
#     def getOutputFormat(choices=None):
#         return 'gsuite'
         
    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('Kmers GSuite', 'gsuite')]
    
    
