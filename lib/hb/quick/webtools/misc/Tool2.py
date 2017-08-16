from collections import OrderedDict
from functools import partial

from quick.webtools.GeneralGuiTool import GeneralGuiTool


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class Tool2(GeneralGuiTool):
    INPUT_BOXES = ['a','b','c','d','e']

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Sveinungs Tool"

    @classmethod
    def getInputBoxNames(cls):
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
        return [('Table', 'table'),
                ('HTML', 'html'),
                ('Select key', 'selectKey'),
                ('Hidden', 'hidden'),
                ('Visible', 'visible')] +\
                [('Select value', 'value%s' % i) for i in xrange(len(cls.INPUT_BOXES))]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @classmethod
    def getOptionsBoxTable(cls):
        header = 'File name, Experiment type, Type of data, Cell/tissue type, Target, Genome build, File suffix'.split(', ')
        row = 'wgEncodeUwHistoneK562H3k36me3StdPkRep1.narrowPeak.gz, ChIP-Seq, Peaks (narrow), K562, H3K36me3, hg19, narrowPeak'.split(', ')
        #return [header, row]
        from proto.hyperbrowser.HtmlCore import HtmlCore
        from collections import OrderedDict
        rowDict = OrderedDict()
        for i in range(10):
            rowDict[row[0] + str(i)] = row[1:]
        
        return '__rawstr__', str(HtmlCore().tableFromDictionary(rowDict, header, tableId='mytable', expandable=True))

    @classmethod
    def getOptionsBoxHtml(cls, prevChoices):
        return '__rawStr__', '<p><img src="http://www.mn.uio.no/ifi/personer/adm/sveinugu/sveinugu.jpg"></p>'

    @classmethod
    def getOptionsBoxSelectKey(cls, prevChoices): # Alternatively: getOptionsBox1()
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
        return OrderedDict([(x, False) for x in cls.INPUT_BOXES] + [('f', True)])

    @staticmethod
    def getOptionsBoxHidden(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        if prevChoices.hidden is None:
            prevHidden = []
        else:
            prevHidden = prevChoices.hidden.split('|') if prevChoices.hidden != '|' else []
        
        prevSelectedSet = set(prevHidden)
        nowSelectedSet = set(key for key,val in prevChoices.selectKey.iteritems() if val)

        newDeselectedList = list(prevSelectedSet - nowSelectedSet)
        if len(newDeselectedList) > 0:
            prevHidden.remove(newDeselectedList[0])

        newSelectedList = list(nowSelectedSet - prevSelectedSet)
        prevHidden += newSelectedList

        return '__hidden__', '|'.join(prevHidden) if len(prevHidden) > 0 else '|'

    @staticmethod
    def getOptionsBoxVisible(prevChoices):
        return repr(prevChoices.hidden), 1, True

    @classmethod
    def setupVariableBoxFunctions(cls):
        for i in xrange(len(cls.INPUT_BOXES)):
            setattr(cls, 'getOptionsBoxValue%s' % i,
                    partial(cls._getVariableBox, index=i))

    @classmethod
    def _getVariableBox(cls, prevChoices, index):
        if prevChoices.hidden != '|':
            prevHidden = prevChoices.hidden.split('|')
            if len(prevHidden) > index:
                key = prevHidden[index]
                return [key, key.capitalize()]

    #
    #@staticmethod
    #def getOptionsBoxSelected(prevChoices):
    #    return repr(prevChoices.multiply), 1, True

    #@staticmethod
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        import sys
        print>>sys.stderr, "An error occurred!!!"
        print 'Nothing happened...'

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

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

Tool2.setupVariableBoxFunctions()
