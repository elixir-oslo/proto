from collections import OrderedDict

from gold.gsuite.GSuiteComposer import composeToFile
from gold.gsuite.GSuiteEditor import selectRowsFromGSuiteByTitle
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.util import CommonFunctionsForTools


class GSuiteSelectRows(GeneralGuiTool):
    exception = None

    INDEX_TITLE_DELIMITER = '_'

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Select subsets of tracks in a GSuite"

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

        return [('Select a GSuite file from history', 'history'), \
                ('Row indices (e.g. 1-20 or 1,3,5,19-29. NB: Intervals are end exclusive.)', 'rowIndices'), \
                ('Select rows','selectRows'), \
                ('', 'showVisualization')]

    @staticmethod
    def getOptionsBoxHistory():

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

        return '__history__','gsuite'




    @classmethod
    def getOptionsBoxRowIndices(cls, prevChoices):
        if prevChoices.history == None:
            return
        
        gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
        
        return '1-%i' % (gSuite.numTracks() + 1)
        
        
    
    @classmethod
    def getOptionsBoxSelectRows(cls, prevChoices):
        
        if prevChoices.history == None:
            return
        try:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
            rowIndicesStr = prevChoices.rowIndices
            if rowIndicesStr:
                selectedIndices = CommonFunctionsForTools.processIndicesString(rowIndicesStr)
                resDict = OrderedDict()
                for i, trackTitle in enumerate(gSuite.allTrackTitles()):
                    if (i + 1) in selectedIndices:
                        resDict[cls.addIndexToTitle((i+1), trackTitle)] = True
                    else:
                        resDict[cls.addIndexToTitle((i+1), trackTitle)] = False
                return resDict
#                 if selectedIndices:
#                     return
            return OrderedDict([(cls.addIndexToTitle((i+1), x), True) for i, x in enumerate(gSuite.allTrackTitles())])
        except:
            pass
    
    @classmethod
    def getOptionsBoxShowVisualization(cls, prevChoices):
        return
#         if prevChoices.history == None:
#             return
#         else:
#             try:
#                 gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
#                 rowIndicesStr = prevChoices.rowIndices
#                 if rowIndicesStr:
#                     selectedIndices = CommonFunctionsForTools.processIndicesString(rowIndicesStr)
#                     if selectedIndices:
#                         maxIndex = max(selectedIndices)
#                         if maxIndex > (gSuite.numTracks()-1):
#                             return 
#                         else:
#                             from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs, dataTransformer
#                             
#                             titleList = [tt for i, tt in enumerate(gSuite.allTrackTitles()) if i in selectedIndices]
#                             wholeList = gSuite.allTrackTitles()
#                             
#                             res=OrderedDict()
#                             for w in wholeList:
#                                 if w in titleList:
#                                     res[w]=1
#                                 else:
#                                     res[w]=0
#                             
#                             dT = dataTransformer(res)
#                             seriesName, categories, data = dT.changeDictIntoList()
#                              
#                             vg = visualizationGraphs()
#                             res = vg.drawBarChart(data, categories=categories, seriesName=['Tracks'], allowDecimals=False, maxY=1)
#                             
#                             return '__rawstr__', str(vg.visualizeResults(res))
#             except:
#                 pass
           


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

        gSuite = getGSuiteFromGalaxyTN(choices.history)
        
#         titleList = []
#         if choices.rowIndices:
#             selectedIndices = CommonFunctionsForTools.processIndicesString(choices.rowIndices)
#             titleList = [tt for i, tt in enumerate(gSuite.allTrackTitles()) if i in selectedIndices]
#         else:
        titleList = [cls.removeIndexFromTitleName(title) for title, selected in choices.selectRows.iteritems() if selected]
        filteredGSuite = selectRowsFromGSuiteByTitle(gSuite, titleList)

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
        
        gSuite = getGSuiteFromGalaxyTN(choices.history)
        if choices.rowIndices:
            try:
                selectedIndices = CommonFunctionsForTools.processIndicesString(choices.rowIndices)
                maxIndex = max(selectedIndices)
                if maxIndex > (gSuite.numTracks()):
                    return 'Selected row index %i is too high. GSuite contains %i tracks.' % (maxIndex, gSuite.numTracks())
            except:
                return 'Please enter valid indices string (e.g. 1-10, 12, 14)'
         
 
        if gSuite.numTracks() == 0:
            return 'GSuite file contains no tracks'

    @classmethod
    def getOutputName(cls, choices):
        if choices.history:
            from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
            return getGSuiteHistoryOutputName('same', ', subset of tracks', choices.history)

    @classmethod
    def addIndexToTitle(cls, indx, title):
        return cls.INDEX_TITLE_DELIMITER.join([str(indx), title])

    @classmethod
    def removeIndexFromTitleName(cls, titleWithIndex):
        delimiterIndex = titleWithIndex.find(cls.INDEX_TITLE_DELIMITER)
        if delimiterIndex > -1:
            return titleWithIndex[(delimiterIndex+1):]
        else:
            return titleWithIndex


    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    @staticmethod
    def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
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
    #
    @staticmethod
    def getResetBoxes():
        '''
        Specifies a list of input boxes which resets the subsequent stored
        choices previously made. The input boxes are specified by index
        (starting with 1) or by key.
        '''
        return ['history', 'rowIndices']
    
    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()
        core.paragraph('This tool provides the option of filtering tracks in a GSuite file '
                       'generating as output a GSuite file with the same columns, but '
                       'with only a subset of tracks (rows) as selected by the user.')
        core.divider()
        core.paragraph('To filter a GSuite file, please follow these steps: ')
        core.orderedList(['Select the input GSuite file from history',
                          'Select the tracks that should be kept (described in the list '
                          'by its title, or by the whole uri if the title is not defined)',
                          'Click the "Execute" button'])

        cls._addGSuiteFileDescription(core,
                                      alwaysShowRequirements=True,
                                      alwaysShowOutputFile=True)

        return str(core)
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
    #     return 'https://hyperbrowser.uio.no/nar/u/hb-superuser/p/select-subset-of-tracks-in-gsuite---user-guide'
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
    @classmethod
    def getOutputFormat(cls,choices):
        return 'gsuite'
