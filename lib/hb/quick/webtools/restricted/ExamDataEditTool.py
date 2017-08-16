from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.extra.exam.ExamResultsAnalysis import ExamResultsReader,\
    ExamResultsAnalysis

# This is a template prototyping GUI that comes together with a corresponding
# web page.

class ExamDataEditTool(GeneralGuiTool):
    
    OP_MORE_THEN = '>='
    OP_EQUAL_TO = '='
    OP_LESS_THEN = '<='
    OP_IN = 'between'
    FILTER_OP_LIST = [
                      OP_MORE_THEN,
                      OP_EQUAL_TO,
                      OP_LESS_THEN,
                      OP_IN
                      ]
    
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

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('Select results file from history (.csv)','resultsFile'),
                ('Select filtering column', 'columnName'),
                ('Select filtering operation', 'filter'),
                ('Specify filtering value/interval', 'value')
                ]

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
    def getOptionsBoxResultsFile(): # Alternatively: getOptionsBox1()
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
        return GeneralGuiTool.getHistorySelectionElement('csv', 'txt')

    @staticmethod
    def getOptionsBoxColumnName(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        
        if prevChoices.resultsFile:
            resultsFN = ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.resultsFile)
            return ExamResultsReader.readColumnNames(resultsFN)
        
        return []

    @staticmethod
    def getOptionsBoxFilter(prevChoices):
        return ExamDataEditTool.FILTER_OP_LIST
  
    @staticmethod
    def getOptionsBoxValue(prevChoices):
        return ''

    #@staticmethod
    #def getInfoForOptionsBoxKey(prevChoices):
    #    '''
    #    If not None, defines the string content of an clickable info box beside
    #    the corresponding input box. HTML is allowed.
    #    '''
    #    return None

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @staticmethod
    def filterDataRow(filteringOperator, filteringValue, filteringInterval, dataVal, isNumberType):
        addRow = False
        if isNumberType:
            if filteringOperator == ExamDataEditTool.OP_EQUAL_TO:
                addRow = float(filteringValue) == float(dataVal)
            elif filteringOperator == ExamDataEditTool.OP_MORE_THEN:
                addRow = float(dataVal) >= float(filteringValue)
            elif filteringOperator == ExamDataEditTool.OP_LESS_THEN:
                addRow = float(dataVal) <= float(filteringValue)
            else:
                intervalStart = filteringInterval[0].strip()
                intervalEnd = filteringInterval[1].strip()
                addRow = float(dataVal) >= float(intervalStart) and float(dataVal) <= float(intervalEnd) #IN
        elif filteringOperator == ExamDataEditTool.OP_EQUAL_TO:
            addRow = filteringValue == dataVal
        elif filteringOperator == ExamDataEditTool.OP_MORE_THEN:
            addRow = dataVal >= filteringValue
        elif filteringOperator == ExamDataEditTool.OP_LESS_THEN:
            addRow = dataVal <= filteringValue
        else:
            intervalStart = filteringInterval[0]
            intervalEnd = filteringInterval[1]
            addRow = dataVal >= intervalStart and dataVal <= intervalEnd #IN
        return addRow

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
        resultsFN = ExternalTrackManager.extractFnFromGalaxyTN(choices.resultsFile)
        filteringColumnName = choices.columnName
        filteringOperator = choices.filter
        
        #filtering value is always uppercase for easier comparison
        val = choices.value.strip().upper()
        filteringValue = None
        filteringInterval = None
        if filteringOperator == ExamDataEditTool.OP_IN:
            filteringInterval = [x.strip().upper() for x in val.strip('[]()').split(',')]
        else: 
            filteringValue = val
        filteredContent = []
        
        with open(resultsFN) as origFile:
            
            import csv
            reader = csv.reader(origFile)
            attributes = reader.next()
            filteredContent.append(','.join(attributes))
            maxScores = reader.next()
            filteredContent.append(','.join(maxScores))
            
            filterColumnIndex = attributes.index(filteringColumnName)
            
            dataRow = reader.next()
            dataVal = dataRow[filterColumnIndex].upper().strip()
            isNumberType = False
            try:
                float(dataVal)
                isNumberType = True
            except:
                pass
            
            if ExamDataEditTool.filterDataRow(filteringOperator, filteringValue, filteringInterval, dataVal, isNumberType):
                filteredContent.append(','.join(dataRow))
            
            for dataRow in reader:
                dataVal = dataRow[filterColumnIndex].upper()
                if ExamDataEditTool.filterDataRow(filteringOperator, filteringValue, filteringInterval, dataVal, isNumberType):
                    filteredContent.append(','.join(dataRow))
#                 if filteringColumnName == ExamResultsAnalysis.COL_GRADE:
#                     if filteringOperator == ExamDataEditTool.OP_EQUAL_TO:
#                         if filteringValue == dataVal:
#                             filteredContent.append(dataRow)
#                     elif filteringOperator == ExamDataEditTool.OP_MORE_THEN:
#                         if dataVal <= filteringValue.upper():
#                             filteredContent.append(dataRow)
#                     elif filteringOperator == ExamDataEditTool.OP_LESS_THEN:
#                         if dataVal >= filteringValue:
#                             filteredContent.append(dataRow)
#                     else: #IN
#                         intervalStart = filteringInterval[0]
#                         intervalEnd = filteringInterval[1]
#                         if dataVal <= intervalStart \
#                         and dataVal >= intervalEnd:
#                             filteredContent.append(dataRow)
#                 else:

#                 if filteringOperator == ExamDataEditTool.OP_EQUAL_TO:
#                     if filteringValue == dataVal:
#                         filteredContent.append(','.join(dataRow))
#                 elif filteringOperator == ExamDataEditTool.OP_MORE_THEN:
#                     if dataVal >= filteringValue:
#                         filteredContent.append(','.join(dataRow))
#                 elif filteringOperator == ExamDataEditTool.OP_LESS_THEN:
#                     if dataVal <= filteringValue:
#                         filteredContent.append(','.join(dataRow))
#                 else: #IN
#                     intervalStart = filteringInterval[0]
#                     intervalEnd = filteringInterval[1]
#                     if dataVal >= intervalStart \
#                     and dataVal <= intervalEnd:
#                         filteredContent.append(','.join(dataRow))
                            
            origFile.close()
            
#         print 'Printing filtered content...'
#         print filteredContent
#         print 'Done...'
#         for fc in filteredContent:
#             print fc
        with open(galaxyFn, 'wb') as outFile:
            outFile.write('\n'.join(filteredContent))
            outFile.close()
         
#         examResults = ExamResultsReader.run(resultsFN, 
#                                             ExamResultsAnalysis.REQUIRED_COLUMNS, 
#                                             ExamResultsAnalysis.OPTIONAL_COLUMNS)
        

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        if not choices.resultsFile:
            return 'Please select a results file from history'
        
        if not choices.value:
            return 'Please specify the filtering value'
        
        filteringColumnName = choices.columnName
        filteringOperator = choices.filter
        val = choices.value.strip().upper()
        filteringInterval = None
        if filteringOperator == ExamDataEditTool.OP_IN:
            filteringInterval = [x.strip().upper() for x in val.strip('[]()').split(',')]
            #TODO: if ColumnName is Grade, validate that value is in [A,B,C,D,E,F]
            if filteringColumnName == ExamResultsAnalysis.COL_GRADE:
                if filteringOperator == ExamDataEditTool.OP_IN:
                    if len(filteringInterval) != 2:
                        return 'Please specify a valid interval for the filtering value, e.g. "A,C"'
                    elif filteringInterval[0] not in ExamResultsAnalysis.GRADES or \
                    filteringInterval[1] not in ExamResultsAnalysis.GRADES:
                        return 'Interval values must be valid grades, one of ' + str(ExamResultsAnalysis.GRADES)
            if filteringInterval[0] > filteringInterval[1]:
                return 'Invalid interval. Start value is larger then end value.'
        else:
            if filteringColumnName == ExamResultsAnalysis.COL_GRADE:
                if val not in ExamResultsAnalysis.GRADES:
                    return "Please specify a valid grade, one of %r" % str(ExamResultsAnalysis.GRADES)

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
        return True

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
        return 'csv'
