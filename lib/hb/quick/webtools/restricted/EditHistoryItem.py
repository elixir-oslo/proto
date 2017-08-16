from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.application.ExternalTrackManager import ExternalTrackManager
#This is a template prototyping GUI that comes together with a corresponding web page.
#

class EditHistoryItem(GeneralGuiTool):

    @staticmethod
    def getToolName():
        return "Edit history item"
    
    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Select History item', 'select line to edit', 'Line Info', 'replace line with..']
                
    @staticmethod    
    def getOptionsBox1():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return ('__history__','bed','wig','bedgraph','gtrack')
    
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return ''
    
    @staticmethod    
    def getOptionsBox3(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        if prevChoices[-2]!=None and prevChoices[0]:
            try:
                fnSource = ExternalTrackManager.extractFnFromGalaxyTN(prevChoices[0].split(':'))
                return (open(fnSource,'r').readlines()[int(prevChoices[-2])], 2, True)
            except:
                pass
            
    
    @staticmethod    
    def getOptionsBox4(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return ''
    
    
    
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
        #print ''''The genome %s has %i base pairs. As there is 10 bps per turn, it has %i turns.
        #    This means that your wireframe model will need to be %.1f kilometers long 
        #    '''
        
        if choices[-1]!=None and choices[0]:
            if True:
                index = int(choices[1])
                fnSource = ExternalTrackManager.extractFnFromGalaxyTN(choices[0].split(':'))
                contentTab =  open(fnSource,'r').read().split('\n')
                contentTab[index] = choices[3]
                open(galaxyFn,'w').write('\n'.join(contentTab))
            else:
                pass
                
                
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        pass
        
    
    
    
    #@staticmethod
    #def isPublic():
    #    return False
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    #@staticmethod
    #def isHistoryTool():
    #    return False
    
    #@staticmethod
    #def isDynamic():
    #    return True
    #
    @staticmethod
    def getResetBoxes():
        return [2]
    
    @staticmethod
    def getToolDescription():
        return 'Tool for editing one line at a time. Type the index of line number you want to edit.<br/>Negative indexes start form the end of the file, eg. index = -1 is the last line in file'
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
       '''The format of the history element with the output of the tool.
       Note that html output shows print statements, but that text-based output
       (e.g. bed) only shows text written to the galaxyFn file.
       '''
       return choices[0].split(':')[1]
       # return 'txt'
    
