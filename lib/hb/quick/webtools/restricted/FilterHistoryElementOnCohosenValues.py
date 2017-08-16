from quick.webtools.GeneralGuiTool import GeneralGuiTool
#from gold.application.LogSetup import logMessage
from quick.application.ExternalTrackManager import ExternalTrackManager
from gold.util.CustomExceptions import InvalidFormatError
from third_party.asteval_raise_errors import Interpreter


class FilterHistoryElementOnCohosenValues(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Filter history element on chosen values"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['History Element','File content','choose filter mechanism','Choose column to filter on', 'Select values to filter on', 'Write Expression to filter on']
    
    #@staticmethod
    #def getOpttionsAvailable(prevChoices, )
    
    @staticmethod    
    def getOptionsBox1():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','...')
        '''
        return ('__history__','bed','...')
    
    
    
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        
        if prevChoices[0]:
            fnSource = ExternalTrackManager.extractFnFromGalaxyTN(prevChoices[0].split(':'))
            inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices[0].split(':')), 'r')
            firstLineStr = inputFile.readline()
            count = 0
            resultStrList = []
            while count< 4 and firstLineStr:
                if firstLineStr[0]!='#' and firstLineStr.strip()!='':
                    resultStrList.append(firstLineStr)
                    count+=1
                firstLineStr = inputFile.readline()
            firstLineStr = ''.join(resultStrList)
        else:
            return None
        return (firstLineStr, 4, True)
    
    
    @staticmethod  
    def getOptionsBox3(prevChoices):
        if prevChoices[0]:
            return ['Filter on exact values', 'filter on expression']
        
    @staticmethod  
    def getOptionsBox4(prevChoices):
        
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        if prevChoices[2] == 'Filter on exact values':
            return ['Select column..']+['column-%d' % v for v in range(len(prevChoices[1].split('\n')[0].split('\t')))]
        else:
            return None
        
    @staticmethod  
    def getOptionsBox5(prevChoices):
        
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        if prevChoices[2] == 'Filter on exact values' and prevChoices[3] and prevChoices[3]!='Select column..':
            resultDict = {}
            column = int(prevChoices[3][7:])
            fnSource = ExternalTrackManager.extractFnFromGalaxyTN(prevChoices[0].split(':'))
            inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices[0].split(':')), 'r')
            for i in inputFile:
                tempVal = i.split('\t')[column]
                if not resultDict.has_key(tempVal):
                    resultDict[tempVal] = None
            if len(resultDict.keys())<2000:   
                return dict([(v,False) for v in sorted(resultDict.keys())])
            else:
                return ('Too many values too choose from: %d' % len(resultDict), 1, True)
        else:
            return None
    
    
    @staticmethod  
    def getOptionsBox6(prevChoices):
        if prevChoices[2] == 'Filter on exact values':
            return None
        return ''
    
    

    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history. If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.gtr
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
        outputFile=open(galaxyFn,"w")
        fnSource = ExternalTrackManager.extractFnFromGalaxyTN(choices[0].split(':'))
        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(choices[0].split(':')), 'r')
        
        if choices[2] == 'Filter on exact values':    
            if choices[3]!='Select column..':
                column = int(choices[3][7:])
                filterSet = set([key for key,val in choices[4].items() if val])
                for i in inputFile:
                    if i.split('\t')[column] in filterSet:
                        print>>outputFile, i
                
        else:
            for i in inputFile:
                temptab = i.split('\t')
                aeval = Interpreter()
                for index in range(len(temptab)):
                    aeval.symtable['c'+str(index)] = temptab[index]
                if aeval(choices[5]):
                    print>>outputFile, i
                    
        inputFile.close()
        outputFile.close()    
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        if choices[0] is None:
            return 'Please select a file from history.'
            
        return None
    
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
    #@staticmethod    
    #def getOutputFormat(choices=None):
        '''The format of the history element with the output of the tool.
        Note that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.
        '''
        return 'bed'
    
