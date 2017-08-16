from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.application.ExternalTrackManager import ExternalTrackManager

# This is a template prototyping GUI that comes together with a corresponding
# web page.

class FilterOutSeqsFromFasta(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return 'Get reverse complements of sequences from fasta file'
    
    @staticmethod
    def getInputBoxNames():
        return [
                ('Select fasta file from history', 'file'),
#                 ('Get reverse complements',  'revComp')
                ]

    @staticmethod
    def getOptionsBoxFile():
        return GeneralGuiTool.getHistorySelectionElement('fasta')
    
#     @staticmethod
#     def getOptionsBoxRevComp(prevChoices):
#         return False
    
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        seqs = []
        with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.file), 'r') as f:
            for line in f:
                strpd = line.upper().strip()
                if strpd and strpd[0] in 'ACTG':
                    if strpd not in seqs:
                        seqs.append(strpd)
                        
#         for seq in seqs:
#             print seq
            
        from Bio.Seq import Seq
        for seq in seqs:
            seqObj = Seq(seq)
            print seqObj.reverse_complement()
                
        
    @staticmethod
    def validateAndReturnErrors(choices):
        if not choices.file:
            return "Please select a fasta file"
        
        
