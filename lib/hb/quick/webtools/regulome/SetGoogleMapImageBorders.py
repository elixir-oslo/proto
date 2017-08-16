from quick.webtools.GeneralGuiTool import GeneralGuiTool
from config.Config import *

# This is a template prototyping GUI that comes together with a corresponding
# web page.

class SetGoogleMapImageBorders(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Tool not yet in use"

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
        return [('select google map regulome', 'history'), ('Set northern pixel border for image','north'), ('Set  western pixel border for image','west'), ('Set southern  pixel border for image','south'), ('Set  eastern pixel border for image','east')] #Alternatively: [ ('box1','key1'), ('box2','key2') ]

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
    def getOptionsBoxHistory(): # Alternatively: getOptionsBoxKey1()
        '''
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to other
        methods. These are lists of results, one for each input box (in the
        order specified by getInputBoxOrder()).
        
        The input box is defined according to the following syntax:
        
        Selection box:          ['choice1','choice2']
        - Returns: string
        
        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - Returns: string
        
        Password field:         '__password__'
        - Returns: string
        
        Genome selection box:   '__genome__'
        - Returns: string
        
        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name
        
        History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.
        
        History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.
        
        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string
        
        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None
        
        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return '__history__', 'customhtml'
    
    
    @staticmethod    
    def getOptionsBoxNorth(prevChoices):
        return ''
    
    
    @staticmethod    
    def getOptionsBoxEast(prevChoices):
        return ''
    
    @staticmethod    
    def getOptionsBoxSouth(prevChoices):
        return ''
    
    @staticmethod    
    def getOptionsBoxWest(prevChoices):
        return ''
    
    
    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        from quick.application.ExternalTrackManager import ExternalTrackManager
        import urllib2
        
        north = choices.north
        west = choices.west
        east = choices.east
        south = choices.south
        
        histFn = ExternalTrackManager.extractFnFromGalaxyTN(choices.history.split(':'))
        htmlText = open(histFn).read()
        mapId = htmlText.split('<tr><td><a')[1].split('"')[1].split('/')[-1]
        
        relLink = htmlText.split('">Counts<')[0].split('"')[-1].strip()
        rowColsHtml = urllib2.urlopen('https://hyperbrowser.uio.no'+relLink).read()
        rows = rowColsHtml[rowColsHtml.rfind('title=""'):].split('>')[1].split('.')[0]
        cols = rowColsHtml.split('</a></th></tr>')[0].split('>')[-1].split('.')[0]
        
        #print north, east, west, south
        #print mapId, rows, cols
        
        import re
        mapHtmlFn = STATIC_PATH +'/maps/'+mapId+'/index.html'
        
        mapHtmlText = open(mapHtmlFn).read()
        mapHtmlText = mapHtmlText.replace('debug: true', 'debug: false')
        mapHtmlText = re.sub('westPixel: [0-9]+,', 'westPixel: %s,' % west,  mapHtmlText)#mapHtmlText.replace('westPixel: 0,', )
        mapHtmlText = re.sub('northPixel: [0-9]+,', 'northPixel: %s,' % north,  mapHtmlText)#mapHtmlText.replace('northPixel: 0,', 'northPixel: %s,' % north)
        mapHtmlText = re.sub('eastPixel: [0-9]+,', 'eastPixel: %s,' % east,  mapHtmlText)#mapHtmlText.replace('eastPixel: 0,', 'eastPixel: %s,' % east)
        mapHtmlText = re.sub('southPixel: [0-9]+,', 'southPixel: %s,' % south,  mapHtmlText)#mapHtmlText.replace('southPixel: 0,', 'southPixel: %s,' % south)
        mapHtmlText = re.sub('numRows: [0-9]+,', 'numRows: %s,' % rows, mapHtmlText)
        mapHtmlText = re.sub('numCols: [0-9]+,', 'numCols: %s,' % cols, mapHtmlText)
        open(mapHtmlFn, 'w').write(mapHtmlText)
        open(galaxyFn,'w').write(htmlText)
        

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
    @staticmethod    
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'
