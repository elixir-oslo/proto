from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.application.GalaxyInterface import GalaxyInterface
import re
from quick.application.ExternalTrackManager import ExternalTrackManager
import gold.application.StatRunner
# This is a template prototyping GUI that comes together with a corresponding
# web page.

class FilterTrackBasedOnOverlap(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Filter track based on overlap with other track"

    @staticmethod
    def getInputBoxNames():
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:
        
            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.
        
        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).
        '''
        return ['select genome', 'Select source for operation', 'select track', 'Select source for region ', 'select region track', 'specify percent of overlap treshold'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None
    
    @staticmethod    
    def getOptionsBox1():
        return '__genome__'
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        return ['from history', 'from tracks']
        
    @staticmethod    
    def getOptionsBox3(prevChoices):
        #return ''
        if prevChoices[-2] == 'from history':
            return ('__history__', 'bed', 'gtrack', 'bedgraph')
        else:
            return '__track__'
    
        
    @staticmethod
    def getOptionsBox4(prevChoices):
        return ['from history', 'from tracks']
    
    @staticmethod    
    def getOptionsBox5(prevChoices):
        if prevChoices[-2] == 'from history':
            return ('__history__', 'bed', 'gtrack', 'bedgraph')
        elif prevChoices[-2] == 'from tracks':
            return '__track__'
    
    @staticmethod    
    def getOptionsBox6(prevChoices):
        if prevChoices[-2]:
            return ''  
        
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
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        
        analysisDef = 'dummy -> ProportionCountStat'
        genome = choices[0]
        tn1 = choices[2].split(':')
        binSpec = choices[4]
        regSpec = 'track'
        if choices[3] == 'from history':
            regSpec = ExternalTrackManager.extractFileSuffixFromGalaxyTN(choices[4].split(':'))
            binSpec = ExternalTrackManager.extractFnFromGalaxyTN(choices[4].split(':'))
        numBins = open(binSpec).read().count('\n')
        if numBins>330000:
            gold.application.StatRunner.MAX_NUM_USER_BINS = numBins
            

        percent = float(choices[5]) if float(choices[5])<=1.0 else float(choices[5])/100.0
        GalaxyInterface.ALLOW_OVERLAPPING_USER_BINS = True
        resultDict = GalaxyInterface.runManual([tn1], analysisDef, regSpec, binSpec, genome, galaxyFn, printResults=False, printProgress=True)
        overlapRegions = [k for k, v in resultDict.items() if v['Result']>=percent]
        with open(galaxyFn,'w') as utfil:
            for i in overlapRegions:
                print>>utfil, '\t'.join([i.chr, str(i.start), str(i.end)])
        
        
        

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        if choices[5]:
            try:
                var = float(choices[5])
            except:
                return 'Invalid precentage syntax'
        return None
        
    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    #@staticmethod
    #def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
    #
    #@staticmethod
    #def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    @staticmethod
    def getToolDescription():
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        return 'This Tool filteres out any overlap that is below the treshold value for overlap. the percentage treshold can be specified as a number between 0-1 and between 1.01-100.0'
    
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    #@classmethod
    #def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod    
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'bed'
