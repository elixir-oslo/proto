from quick.webtools.GeneralGuiTool import GeneralGuiTool
import third_party.safeshelve as safeshelve
from config.Config import DATA_FILES_PATH
# This is a template prototyping GUI that comes together with a corresponding
# web page.

class AddToolsToBookmark(GeneralGuiTool):
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Bookmark tools to your collection"

    @staticmethod
    def getInputBoxNames():
        
        return ['Specify tool name', 'Specify tool URL', 'Specify tool name', 'Specify tool URL', 'Specify tool name', 'Specify tool URL',\
		'Specify tool name', 'Specify tool URL', 'Specify tool name', 'Specify tool URL', 'Specify tool name', 'Specify tool URL',\
		'Specify tool name', 'Specify tool URL', 'Specify tool name', 'Specify tool URL'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    @staticmethod    
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey()
        
        return ''
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        return ''
    
    
    @staticmethod    
    def getOptionsBox3(prevChoices):
	if prevChoices[-2]:
	    return ''
    @staticmethod    
    def getOptionsBox4(prevChoices):
	if prevChoices[-3]:
	    return ''
    
    
    @staticmethod    
    def getOptionsBox5(prevChoices):
        if prevChoices[-2]:
	    return ''
    @staticmethod    
    def getOptionsBox6(prevChoices):
        if prevChoices[-3]:
	    return ''
    
    @staticmethod    
    def getOptionsBox7(prevChoices):
	if prevChoices[-2]:
	    return ''
    @staticmethod    
    def getOptionsBox8(prevChoices):
	if prevChoices[-3]:
	    return ''
    
    
    @staticmethod    
    def getOptionsBox9(prevChoices):
        if prevChoices[-2]:
	    return ''
    @staticmethod    
    def getOptionsBox10(prevChoices):
        if prevChoices[-3]:
	    return ''
	
    @staticmethod    
    def getOptionsBox11(prevChoices):
        if prevChoices[-2]:
	    return ''
    @staticmethod    
    def getOptionsBox12(prevChoices):
        if prevChoices[-3]:
	    return ''
    
    @staticmethod    
    def getOptionsBox13(prevChoices):
	if prevChoices[-2]:
	    return ''
    @staticmethod    
    def getOptionsBox14(prevChoices):
	if prevChoices[-3]:
	    return ''
    
    
    @staticmethod    
    def getOptionsBox15(prevChoices):
        if prevChoices[-2]:
	    return ''
    @staticmethod    
    def getOptionsBox16(prevChoices):
        if prevChoices[-3]:
	    return ''
    
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        
	linkTemplate = '<a href="%s"> %s </a><br/><br/>'
	if username:
	    SHELVE_FN = DATA_FILES_PATH +  '/UserToolsCollection.shelve'
	    s = safeshelve.open(SHELVE_FN)
	    valDict = s[username] if s.has_key(username) else {}
	    for i in range(0, len(choices),2):
		if choices[i] and choices[i+1]:
		    valDict[choices[i]] = choices[i+1]
		    print 'Added tool to your bookmarks: ' + linkTemplate % (choices[i+1], choices[i])
		else:
		    break
	    if valDict:
		s[username] = valDict
	    s.close()
	


    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
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
    #@staticmethod
    #def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
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
    #@staticmethod
    #def getFullExampleURL():
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
    #@staticmethod    
    #def getOutputFormat(choices):
    #    '''
    #    The format of the history element with the output of the tool. Note
    #    that html output shows print statements, but that text-based output
    #    (e.g. bed) only shows text written to the galaxyFn file.In the latter
    #    case, all all print statements are redirected to the info field of the
    #    history item box.
    #    '''
    #    return 'html'
