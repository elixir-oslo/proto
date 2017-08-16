from collections import OrderedDict

from quick.webtools.GeneralGuiTool import GeneralGuiTool


class GSuiteSelectColumns(GeneralGuiTool):
    exception = None

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Select subset of meta-data columns in a GSuite"

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

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('Select GSuite file from history', 'history'), \
                ('Select columns','selectColumns')
                ]

    @staticmethod
    def getOptionsBoxHistory(): # Must have this name ('getOptionsBoxFirst' +

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
        - The contents is the default value shown inside the text area
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
        return '__history__', 'gsuite'


    @classmethod
    def getOptionsBoxSelectColumns(cls, prevChoices):
        from gold.gsuite.GSuiteConstants import TITLE_COL
        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN

        if prevChoices.history == None:
            return
        try:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
        except:
            return

        cols = []
        if gSuite.hasCustomTitles():
            cols.append(TITLE_COL)
        cols += gSuite.attributes

        return OrderedDict([(x,True) for x in cols])
    
#     @classmethod
#     def getOptionsBoxShowVisualization(cls, prevChoices):
#           
#         if prevChoices.history == None:
#             return
#         else:
#             try:
#                 from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs, dataTransformer
#                 
#                 colList = [col for col,selected in prevChoices.selectColumns.iteritems()]
#                 selectedAttributes = [col for col, selected in prevChoices.selectColumns.iteritems() if selected]
#                 
#                 res=OrderedDict()
#                 for w in colList:
#                     if w in selectedAttributes:
#                         res[w]=1
#                     else:
#                         res[w]=0
#                 
#                 dT = dataTransformer(res)
#                 seriesName, categories, data = dT.changeDictIntoList()
#                  
#                 vg = visualizationGraphs()
#                 res = vg.drawColumnChart(data, categories=categories, seriesName=['Tracks'], allowDecimals=False, maxY=1)
#                 
#                 return '__rawstr__', str(vg.visualizeResults(res))
#             
#             except:
#                 pass
        
    
    
    @classmethod
    def execute(cls,choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        from gold.gsuite.GSuiteEditor import selectColumnsFromGSuite
        from gold.gsuite.GSuiteConstants import TITLE_COL
        from gold.gsuite.GSuiteComposer import composeToFile

        gSuite = getGSuiteFromGalaxyTN(choices.history)

        colList = [col for col,selected in choices.selectColumns.iteritems() if selected]
        selectedAttributes = [col for col in colList if col != TITLE_COL]
        selectTitle = TITLE_COL in colList

        filteredGSuite = selectColumnsFromGSuite(gSuite, selectedAttributes,
                                                 selectTitle=selectTitle)

        composeToFile(filteredGSuite, galaxyFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.

        '''

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.history)
        if errorStr:
            return errorStr

        if not choices.selectColumns is None and len(choices.selectColumns) == 0:
            return 'GSuite file contains only standard columns'

    @classmethod
    def getOutputName(cls, choices):
        if choices.history:
            from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
            return getGSuiteHistoryOutputName('same', ', subset of columns', choices.history)

    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None

    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True
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

    @staticmethod
    def getResetBoxes():
        '''
        Specifies a list of input boxes which resets the subsequent stored
        choices previously made. The input boxes are specified by index
        (starting with 1) or by key.
        '''
        return ['history']

    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore
        from gold.gsuite.GSuiteConstants import URI_COL, FILE_FORMAT_COL, \
                                                TRACK_TYPE_COL, TITLE_COL

        core = HtmlCore()
        core.paragraph('This tool provides the option of filtering metadata columns '
                       'in a GSuite file, generating as output a GSuite file with the '
                       'same tracks (rows), but with only a subset of '
                       'metadata columns as selected by the user. ')
        core.divider()
        core.paragraph('To filter a GSuite file, please follow these steps: ')
        core.orderedList(['Select the input GSuite file from history',
                          'Select the metadata columns that should be kept',
                          'Click the "Execute" button'])

        core.divider()
        core.smallHeader('Note')
        core.paragraph('The standard metadata columns of a GSuite file cannot be '
                       'removed by this tool: ')
        core.unorderedList([URI_COL, FILE_FORMAT_COL, TRACK_TYPE_COL])
        core.paragraph('The exception to this rule is the "%s" column.' % TITLE_COL)

        cls._addGSuiteFileDescription(core,
                                      alwaysShowRequirements=True,
                                      alwaysShowOutputFile=True)

        return str(core)
        string = 'This tool provides the option of filtering track attributes in a GSuite file and generates a GSuite with the user selected attributes. It takes a GSuite file as an input, and displays all the included attributes in mutiple selections box. Upon the user selection, only the selected attributes will appear in the resulted GSuite.'
        return string
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
    # @staticmethod
    # def getFullExampleURL():
    #     return 'https://hyperbrowser.uio.no/nar/u/hb-superuser/p/select-subsets-of-metadata-columns-in-gsuite---user-guide'
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

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'gsuite'
