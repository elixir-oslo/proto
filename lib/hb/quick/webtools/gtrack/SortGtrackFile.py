from gold.origdata.GtrackSorter import sortGtrackFileAndWriteToFile
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool


#This is a template prototyping GUI that comes together with a corresponding web page.
#

class SortGtrackFile(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Sort GTrack file"

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
        return '__history__', 'gtrack'
    #
    #@staticmethod    
    #def getOptionsBox2(prevChoices): 
    #    '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
    #    prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
    #    '''
    #    return ['']
    
    #@staticmethod    
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']

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
        inFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[2].split(':'))
        
        try:
            sortGtrackFileAndWriteToFile(inFn, galaxyFn, genome)
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
        core.paragraph('Sorts a GTrack file using standard alphabetic sort and '
                       'returns it as a history element. The GTrack file are '
                       'sorted first by the bounding region lines, if any, and then '
                       'by the data lines.')
        core.divider()
        core.smallHeader('Genome')
        core.paragraph('Some GTrack files require a specified genome to be valid, e.g. if bounding regions '
                       'are specified without explicit end coordinates.')
        core.divider()
        core.smallHeader('Notice')
        core.paragraph('If the track type is one of Function (F), Linked Function '
                       '(LF), or Linked Base Pairs (LBP), the data lines are not sorted.')
        
        core.divider()
        core.smallHeader('Example')
        core.paragraph('Input file')
        core.styleInfoBegin(styleClass='debug')
        core.append(
'''##gtrack version: 1.0
##track type: segments
###start  end  strand
####seqid=chr2; start=0; end=300
100       165       +
####seqid=chr1; start=200; end=400
300       349       -
200       299       +
####seqid=chr1; start=0; end=100
0          50       +''')
        core.styleInfoEnd()
        
        core.paragraph('Output file')
        core.styleInfoBegin(styleClass='debug')
        core.append(
'''##gtrack version: 1.0
##track type: segments
##sorted elements: true
###start  end  strand
####seqid=chr1; start=0; end=100
0          50       +
####seqid=chr1; start=200; end=400
200       299       +
300       349       -
####seqid=chr2; start=0; end=300
100       165       +''')
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
        return 'gtrack'
       #'''The format of the history element with the output of the tool.
       #Note that html output shows print statements, but that text-based output
       #(e.g. bed) only shows text written to the galaxyFn file.
       #'''
        
