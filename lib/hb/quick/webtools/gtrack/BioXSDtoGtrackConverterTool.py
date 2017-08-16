from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.application.ExternalTrackManager import ExternalTrackManager

class BioXSDtoGtrackConverterTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "BioXSD 1.1 to GTrack converter (under development)"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Choose BioXSD file from history','Track type','Value column','Additional columns']

    @staticmethod    
    def getOptionsBox1():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return '__history__', 'bioxsd'
    
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        #fixme: should be replaced with general code:
        return ['Points', 'Valued Points', 'Segments', 'Valued Segments', 'Genome Partition', 'Step Function', 'Function',\
                'Linked Points', 'Linked Valued Points', 'Linked Segments', 'Linked Valued Segments', 'Linked Genome Partition', 'Linked Step Function', 'Linked Function', 'Linked Base Pairs']
    
    @staticmethod
    def _getBioXSDFileName(prevChoices):
        return ExternalTrackManager.extractFnFromGalaxyTN(prevChoices[0].split(':'))
    
    @staticmethod    
    def getOptionsBox3(prevChoices):
        if any(x in prevChoices[1] for x in ['Marked', 'Function']):
            if not prevChoices[0]:
                return ['Test']
            
            valColumnList = []
            inFn = BioXSDtoGtrackConverterTool._getBioXSDFileName(prevChoices)
            ###
            ### Code here
            ###
            return valColumnList
    
    @staticmethod    
    def getOptionsBox4(prevChoices):
        if not prevChoices[0]:
            return {'Test': False}

        extraColumnList = []
        inFn = BioXSDtoGtrackConverterTool._getBioXSDFileName(prevChoices)
        
        ###
        ### Code here
        ###
        
        return dict((x, False) for x in extraColumnList)

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
        
        if choices[0]:
            inFn = cls._getBioXSDFileName(choices)
            outFn = galaxyFn
            trackType = choices[1]
            valCol = choices[2]
            extraCols = [col for col, selected in choices[3] if selected]
            
            ###
            ### Code here
            ###

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        
        if not choices[0]:
            return ''
        
        inFn = BioXSDtoGtrackConverterTool._getBioXSDFileName(choices)
        isValidBioXSDFile = False
        errorMsg = ''
        
        ###
        ### Code here
        ###
        
        if not isValidBioXSDFile:
            return 'Input file is not a valid BioXSD 1.1 file. Error message: %s' % errorMsg
    
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
    #
    @staticmethod    
    def getOutputFormat(choices=None):
        '''The format of the history element with the output of the tool.
        Note that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.
        '''
        return 'gtrack'
    
