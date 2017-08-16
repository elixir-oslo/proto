from gold.origdata.GtrackStandardizer import standardizeGtrackFileAndWriteToFile
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class ConvertToLinkedValuedSegments(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Standardize GTrack file"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Select a specific genome?', 'Genome build:', 'Select GTrack file:']

    @staticmethod    
    def getOptionsBox1():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '''
        return ['No', 'Yes']
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '''
        if prevChoices[0] == 'Yes':
            return "__genome__"

    @staticmethod    
    def getOptionsBox3(prevChoices):
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return ('__history__', 'gtrack')

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history. If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.gtr
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
        genome = choices[1] if choices[0] == 'Yes' else None
        suffix = ExternalTrackManager.extractFileSuffixFromGalaxyTN(choices[2].split(':'))
        inFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[2].split(':'))
        
        try:
            standardizeGtrackFileAndWriteToFile(inFn, galaxyFn, genome, suffix=suffix)
        except Exception, e:
            import sys
            print >> sys.stderr, e
            
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        
        genome = choices[1] if choices[0] == 'Yes' else None
        if genome == '':
            return 'Please select a genome build.'
        
        return GeneralGuiTool._checkHistoryTrack(choices, 2, genome, 'GTrack')
    
    @staticmethod
    def isPublic():
        return True
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    #@staticmethod
    #def isHistoryTool():
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    return []
    #
    @staticmethod
    def getToolDescription():
        core = HtmlCore()
        core.paragraph('The GTrack format permits the use of variable column names and order, and '
                       'correspondingly, variable track types. This variation comes at a price, '
                       'increasing the complexity of parsing GTrack files. All GTrack files can, '
                       'however, be represented as the same track type: Linked Valued Segments (LVS). '
                       'This tool converts all GTrack files to the same standardized version of the GTrack format.')
        core.divider()
        
        core.smallHeader('Specification of the standardized GTrack format')
        core.paragraph('The following columns are always present, in the following order:')
        core.orderedList(['seqid ' + str(HtmlCore().emphasize('(sequence ID)')),
                          'start',
                          'end',
                          'value',
                          'strand',
                          'id',
                          'edges'])
        core.paragraph('Any additional columns will then follow, in the order specified in the original GTrack file.')
        core.paragraph('The following header lines are also changed to standardized settings:')
        core.unorderedList(['Track type: linked valued segments', \
                            'Uninterrupted data lines: true ' + \
                                str(HtmlCore().emphasize('(any bounding specification lines are thus removed)')), \
                            '0-indexed: false', \
                            'end inclusive: false'])
        
        core.divider()
        
        core.smallHeader('Genome')
        core.paragraph('Some GTrack files require a specified genome to be valid, e.g. if bounding regions '
                       'are specified without explicit end coordinates.')
        core.divider()
        
        core.smallHeader('Notice')
        core.paragraph('The "value type", "value dimension", "edge weights", "edge weight type" and "edge weight dimension" '
                       'header lines are not standardized. The "value" and "edges" columns may therefore contain all types '
                       'of values supported by the GTrack format. It is, however, simple to assert particular configurations '
                       'of these header lines in specialized parsers.')
        
        core.divider()
        
        core.smallHeader('Example')
        core.paragraph('Input file')
        core.styleInfoBegin(styleClass='debug')
        core.append(
'''##gtrack version: 1.0
##track type: linked genome partition
##edge weights: true
##edge weight type: binary
##1-indexed: true
##end inclusive: true
###end  id      edges
####seqid=chrM; end=500
200     aaa     aab=0;aac=1
500     aab     aaa=0
####seqid=chr21; end=300
200     aac     .
300     aad     aaa=1
####seqid=chr21; start=302; end=400
400     aae     aad=0''')
        core.styleInfoEnd()
        
        core.paragraph('Output file')
        core.styleInfoBegin(styleClass='debug')
        core.append(
'''##gtrack version: 1.0
##track type: linked valued segments
##edge weights: true
##edge weight type: binary
##uninterrupted data lines: true
##no overlapping elements: true
###seqid        start   end     value   strand  id      edges
chrM    0       200     .       .       aaa     aab=0;aac=1
chrM    200     500     .       .       aab     aaa=0
chr21   0       200     .       .       aac     .
chr21   200     300     .       .       aad     aaa=1
chr21   301     400     .       .       aae     aad=0''')
        core.styleInfoEnd()
        
        return str(core)
    #
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
    #
    @staticmethod    
    def getOutputFormat(choices=None):
    #   '''The format of the history element with the output of the tool.
    #   Note that html output shows print statements, but that text-based output
    #   (e.g. bed) only shows text written to the galaxyFn file.
    #   '''
        return 'gtrack'
    #
