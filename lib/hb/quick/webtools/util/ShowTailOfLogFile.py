from quick.webtools.GeneralGuiTool import GeneralGuiTool
from config.Config import LOG_PATH
import glob
import os
from subprocess import check_output

#This is a template prototyping GUI that comes together with a corresponding web page.
#

class ShowTailOfLogFile(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Show tail of log file"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Select log file','Select number of lines to show', 'Content of log file']

    @staticmethod    
    def getOptionsBox1():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        logList = sorted([v for v in os.listdir(LOG_PATH) if v[0]!='#'])
        if 'detailed.log' in logList:
            logList.remove('detailed.log')
            logList.insert(0, 'detailed.log')
            
        return logList
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return '20'
    
        

    @staticmethod    
    def getOptionsBox3(prevChoices):
        if prevChoices[0] and prevChoices[1]:
            if prevChoices[1].strip().isdigit():
                fileObj = open(os.sep.join([LOG_PATH, prevChoices[0]]),'r')
                numLines = int(prevChoices[1].strip())
                return (check_output('tail -n %i %s' % (numLines, os.sep.join([LOG_PATH, prevChoices[0]])), shell=True), numLines, True)
                #return (ShowTailOfLogFile.tail(fileObj,numLines), numLines, True)

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
    #
    #@staticmethod
    #def tail( f, window=20 ):
    #    BUFSIZ = 1024
    #    f.seek(0, 2)
    #    bytes = f.tell()
    #    size = window
    #    block = -1
    #    data = []
    #    while size > 0 and bytes > 0:
    #        if (bytes - BUFSIZ > 0):
    #            # Seek back one whole BUFSIZ
    #            f.seek(block*BUFSIZ, 2)
    #            # read BUFFER
    #            data.append(f.read(BUFSIZ))
    #        else:
    #            # file too small, start from begining
    #            f.seek(0,0)
    #            # only read what was not read
    #            data.append(f.read(bytes))
    #        linesFound = data[-1].count('\n')
    #        size -= linesFound
    #        bytes -= BUFSIZ
    #        block -= 1
    #    f.close()
    #    return '\n'.join(''.join(data).splitlines()[-window:])
    #
    #@staticmethod
    #def isPublic():
    #    return False
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    
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
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
    #
    #@staticmethod    
    #def getOutputFormat():
    #   '''The format of the history element with the output of the tool.
    #   Note that html output shows print statements, but that text-based output
    #   (e.g. bed) only shows text written to the galaxyFn file.
    #   '''
    #    return 'html'
    #
