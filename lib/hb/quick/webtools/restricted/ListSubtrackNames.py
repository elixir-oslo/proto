from quick.webtools.GeneralGuiTool import GeneralGuiTool
#This is a template prototyping GUI that comes together with a corresponding web page.
#

class ListSubtrackNames(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "List subtrack names"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        #can have two syntaxes: either a list of stings or a list of tuples where each tuple has two items(Name of box on webPage, name of getOptionsBox)
        return ['select genome','select path to tracks', 'Track paths','']

    @staticmethod    
    def getOptionsBox1():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return '__genome__'
    
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return '__track__', 'ucsc'
    
    @staticmethod    
    def getOptionsBox3(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        from quick.application.GalaxyInterface import GalaxyInterface
        from collections import OrderedDict
        try:
            subTrackList = [v[0] for v in GalaxyInterface.getSubTrackNames(prevChoices[0], prevChoices[1].split(':'), deep=False)[0]]
            if len(subTrackList)>0:
                subSubTrackList =  GalaxyInterface.getSubTrackNames(prevChoices[0], prevChoices[1].split(':')+[subTrackList[0]], deep=False)[0]
                if len(subSubTrackList) ==0:
                    return OrderedDict([(v, False)for v in subTrackList])
            #return ('\n'.join(subTrackList), len(subTrackList), True)
        except:
            pass
    
    
    @staticmethod    
    def getOptionsBox4(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        content=[]
        varList = []
        if prevChoices[0] != '----- Select -----':
            prefix = '@T%i= ' if prevChoices[1] == '----- Select -----' else '@T%i= '+ prevChoices[1]+':'
            if isinstance(prevChoices[2], basestring):
                prefix = '@T'
                for i, v in enumerate(prevChoices[2].split('\n')):
                    tmp = prefix
                    if i+1>9:
                        tmp+='0' if i<99 else ''
                    else:
                        tmp+='00'
                    varList.append(tmp+str(i+1))
                    content.append(tmp+str(i+1)+'= '+prevChoices[1]+(':' if v !='' else '')+v)
                content.append('@TNs = '+'/'.join(varList))
                return ('\n'.join(content), len(content), True)
        
        
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
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
        print 'Executing...'

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        return None
    
    #@staticmethod
    #def isPublic():
    #    return False
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    @staticmethod
    def isHistoryTool():
        return False
    
    #@staticmethod
    #def isDynamic():
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    return []
    #
    #@staticmethod
    #def getToolDescription():
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #@staticmethod
    #def isBatchTool():
    #    return False
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
    #
    #@staticmethod    
    #def getOutputFormat(choices):
    #    '''The format of the history element with the output of the tool.
    #    Note that html output shows print statements, but that text-based output
    #    (e.g. bed) only shows text written to the galaxyFn file.
    #    '''
    #    return 'html'
    #
