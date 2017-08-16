from quick.webtools.GeneralGuiTool import GeneralGuiTool
import zipfile
import os

#This is a template prototyping GUI that comes together with a corresponding web page.
#

class ExtractPwms(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Extract PWMs"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        #can have two syntaxes: either a list of stings or a list of tuples where each tuple has two items(Name of box on webPage, name of getOptionsBox)
        return ['PWM source','Selection method','Number of PWMs to select']

    @staticmethod    
    def getOptionsBox1():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return ['Transfac PWMs']
    
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return ['All PWMs', 'Random subset']
    
        
    @staticmethod    
    def getOptionsBox3(prevChoices):
        return ''

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
        #print os.getcwd()
        from config.Config import HB_SOURCE_CODE_BASE_DIR
        
        pwms = parseTransfacMatrixFile(HB_SOURCE_CODE_BASE_DIR+'/data/all_PWMs.txt')
        if choices[1]=='All PWMs':
            selectedPwms = pwms
        elif choices[1] == 'Random subset':
            numRandomPwms = int(choices[2])
            from gold.util.RandomUtil import random            
            selectedPwmKeys = random.sample(pwms.keys(),numRandomPwms)
            selectedPwms = dict([(x,pwms[x]) for x in selectedPwmKeys])

        writeTransfacMatrixFile(selectedPwms, galaxyFn)
        
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
    def getOutputFormat(choices):
        '''The format of the history element with the output of the tool.
        Note that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.
        '''
        return 'txt'
    #

def parseTransfacMatrixFile(fn):
    'Parses a transfac file into a dict of ID->CountMatrix. CountMatrix is in the form of a list of columns, where each column is a dict from acgt to corresponding count values for that column.'
    countMats = []
    for line in open(fn):
        if line.startswith('>'):
            countMats.append([line[1:].strip(), []])
        else:
            countMats[-1][1].append( dict(zip('ACGT',[float(x) for x in line.split()]) ) )
            assert len(countMats[-1][1][-1])==4
    
    return dict(countMats)

def writeTransfacMatrixFile(pwms, fn):
    outF = open(fn, 'w')
    for pwmId,matrix in sorted(pwms.items()):
        outF.write('>'+pwmId+os.linesep)
        for col in matrix:
            outF.write('\t'.join([str(val) for letter,val in sorted(col.items())]) +os.linesep)
    outF.close()
                
