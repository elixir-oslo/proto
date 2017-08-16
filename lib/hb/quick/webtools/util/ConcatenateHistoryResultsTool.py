from cPickle import load
from collections import OrderedDict

from gold.result.Results import Results
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.SignatureDevianceLogging import returns
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class ResultCollection(OrderedDict):
    def __init__(self, chosenResDictKey, imputeNAs=False, naChar='.', firstColLabel=''):
        OrderedDict.__init__(self)
        self._chosenResDictKey = chosenResDictKey
        self._imputeNAs = imputeNAs
        self._naChar = naChar
        self._firstColLabel = firstColLabel

    #OrderedDefaultDict?
    def __setitem__(self, entryLabel, resultValue):
        if not entryLabel in self:
            OrderedDict.__setitem__(self, entryLabel, [])
        self[entryLabel].append(resultValue)

    #def getNumEntries(self):
    #   return len(self.keys())

    def _assertRows(self, allRows):
        pass

    def _addColumnLabels(self, allRows, columnLabels):
        return [[self._firstColLabel] + columnLabels] + allRows

    @returns(str)
    def getTabularStrRepresentation(self, columnLabels):
        allRows = [[entryLabel] + self[entryLabel] for entryLabel in self.keys()]

        if columnLabels not in [None, '']:
            allRows = self._addColumnLabels(allRows, columnLabels)

        return '\n'.join(['\t'.join(['%s'%x for x in row]) for row in allRows])


class LocalResultCollection(ResultCollection):
    def __init__(self, chosenResDictKey, allLocalKeys, imputeNAs=False, naChar='.', firstColLabel=''):
        ResultCollection.__init__(self, chosenResDictKey, imputeNAs, naChar, firstColLabel)
        self._allLocalKeys = allLocalKeys

    def __setitem__(self, entryLabel, resultObject):
        assert type(entryLabel) in [str, type(None)] #anyway ignored..
        assert type(resultObject)==Results, (type(resultObject), resultObject)

        if self._chosenResDictKey == 'fdr':
            resultObject.inferAdjustedPvalues()

        for localResultKey in self._allLocalKeys:
            if self._imputeNAs:
                localResult = resultObject.get(localResultKey)
                if localResult:
                    resultValue = resultObject[localResultKey].get(self._chosenResDictKey)
                else:
                    resultValue = None

                if resultValue is None:
                    resultValue = self._naChar
            else:
                resultValue = resultObject[localResultKey][self._chosenResDictKey]

            ResultCollection.__setitem__(self, localResultKey, resultValue)

    def _assertRows(self, allRows):
        assert len(set([len(row) for row in allRows])) == 1, \
            'All rows must have same number of columns: ' + str([len(row) for row in allRows])


class GlobalResultCollection(ResultCollection):
    def __setitem__(self, entryLabel, resultObject):
        'Sets item, not directly to the passed value (which is resultDict), but to a subResult given by self._chosenResDictKey'
        assert isinstance(entryLabel, basestring)
        assert type(resultObject)==Results, (type(resultObject), resultObject)

        try:
            resultValue = resultObject.getGlobalResult()[self._chosenResDictKey]
        except:
            if self._imputeNAs:
                resultValue = self._naChar
            else:
                raise

        ResultCollection.__setitem__(self, entryLabel, resultValue)

    def _addColumnLabels(self, allRows, columnLabels):
        newAllRows = []
        i = 0

        for j, row in enumerate(allRows):
            curColLabels = columnLabels[i:i+len(row)-1]
            if any(x != '' for x in curColLabels):
                if j > 0:
                    newAllRows += ['']
                newAllRows += [[self._firstColLabel] + curColLabels]
            newAllRows += [row]
            i += len(row)-1

        assert i == len(columnLabels)

        return newAllRows


class ConcatenateHistoryResultsTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Concatenate results of multiple history items"

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
        return [('Select histories: ', 'history'), \
                ('Select result statistic (numbers of results per stat in brackets): ', 'stat'), \
                ('Use local or global results? ', 'localOrGlobal'), \
                ('Allow missing values? ', 'allowMissing'), \
                ('Denote missing values with: ', 'denoteMissing'), \
                ('Print concatenation info as comment? ', 'printInfo'), \
                ('Separate global results by track names? ', 'sepByTrack'), \
                ('Separate global results by: ', 'rowLabels'), \
                ('Print column labels? ', 'printColLabels'), \
                ('Specify column labels: ', 'colLabelType'), \
                ('Custom column labels, separated by pipe character (i.e. "|"): ', 'colLabels')]

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
        return ('__multihistory__', 'html', 'customhtml')

    @classmethod
    def getOptionsBoxStat(cls, prevChoices):
        '''
        See getOptionsBox1().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        if len(prevChoices.history) == 0:
            return []

        rsl = cls._getResultsLists(prevChoices.history)[0]
        if rsl == []:
            return []

        resDictKeysWithCounts = cls._getResDictAndLocalKeys(rsl)[0]
        return ['%s [%s]' % (key,count) for key,count in resDictKeysWithCounts.iteritems()]

    @staticmethod
    def getOptionsBoxLocalOrGlobal(prevChoices):
        return ['Global results', 'Local results']

    @staticmethod
    def getOptionsBoxAllowMissing(prevChoices):
        return ['No', 'Yes']

    @staticmethod
    def getOptionsBoxDenoteMissing(prevChoices):
        if prevChoices.allowMissing == 'Yes':
            return ['.', 'nan', 'None']

    @staticmethod
    def getOptionsBoxPrintInfo(prevChoices):
        return ['Yes', 'No']

    @staticmethod
    def getOptionsBoxSepByTrack(prevChoices):
        if prevChoices.localOrGlobal == 'Global results':
            return ['No', 'Yes']

    @staticmethod
    def getOptionsBoxRowLabels(prevChoices):
        if prevChoices.sepByTrack == 'Yes':
            return ['First track', 'Second track', 'All tracks']

    @staticmethod
    def getOptionsBoxPrintColLabels(prevChoices):
        return ['No','Yes']

    @staticmethod
    def getOptionsBoxColLabelType(prevChoices):
        if prevChoices.printColLabels == 'Yes':
            return ['Short (History - event. batch number)', \
                    'Long (History name - event. batch number)', \
                    'Custom labels']

    @staticmethod
    def getInfoForOptionsBoxColLabelType(prevChoices):
        if prevChoices.colLabelType in [None, '', 'Short (History - event. batch number)']:
            return 'Example column labels: "1", "2-0", "2-1"'
        elif prevChoices.colLabelType == 'Long (History name - event. batch number)':
            return 'Example column labels: "1: History name", "2: Batch run - 0", "2: Batch run - 1"'
        else:
            return 'Any column labels allowed (separated by the pipe character (e.g. "|").'

    @classmethod
    def getOptionsBoxColLabels(cls, prevChoices):
        if prevChoices.colLabelType == 'Custom labels':
            columnLabels = cls._getColumnLabels(prevChoices, labelType='long')
            return '|'.join(columnLabels)

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

        HtmlCore().begin()
        core = HtmlCore()
        histChoices = choices.history
        chosenResDictKey = choices.stat[:choices.stat.find(' [')]

        useGlobal = True if choices.localOrGlobal == 'Global results' else False
        imputeNAs = True if choices.allowMissing == 'Yes' else False

        resultsLists, historyNames = cls._getResultsLists(histChoices)
        allLocalKeys = cls._getResDictAndLocalKeys(resultsLists)[1]

        if useGlobal:
            if choices.sepByTrack == 'Yes':
                if choices.rowLabels == 'First track':
                    firstColLabel = 'Track_1'
                elif choices.rowLabels == 'Second track':
                    firstColLabel = 'Track_2'
                elif choices.rowLabels == 'All tracks':
                    firstColLabel = 'Tracks'
            else: #No
                firstColLabel = 'Statistic'
        else:
            firstColLabel = 'Local region'

        if choices.printColLabels == 'No':
            columnLabels = None
        else: #Yes
            if choices.colLabelType.startswith('Short'):
                columnLabels = cls._getColumnLabels(choices, 'short')
            elif choices.colLabelType.startswith('Long'):
                columnLabels = cls._getColumnLabels(choices, 'long')
            else: #Custom columns
                columnLabels = choices.colLabels.split('|')

        if useGlobal:
            resColl = GlobalResultCollection(chosenResDictKey, imputeNAs, \
                                             naChar=choices.denoteMissing, \
                                             firstColLabel=firstColLabel)
        else:
            resColl = LocalResultCollection(chosenResDictKey, allLocalKeys, imputeNAs, \
                                            naChar=choices.denoteMissing, \
                                            firstColLabel=firstColLabel)

        outFile = open(galaxyFn, 'w')
        if choices.printInfo == 'Yes':
            print>>outFile, '# Concatenated %s results for statistic: ' \
                            % ('global' if choices.localOrGlobal == 'Global results' else 'local') \
                            + chosenResDictKey

        from urllib import unquote
        for i,resultList in enumerate(resultsLists):
            for j,oneResult in enumerate(resultList):
                trackNames = oneResult.getTrackNames()

                tracks = [unquote(trackNames[i][-1]) if trackNames[1] else '' \
                          for i in range(len(trackNames))]

                if choices.sepByTrack in [None, '', 'No']:
                    label = chosenResDictKey
                else:
                    if choices.rowLabels == 'First track':
                        label = tracks[0]
                    elif choices.rowLabels == 'Second track':
                        label = tracks[1]
                    elif choices.rowLabels == 'All tracks':
                        label = ' & '.join(tracks)

                resColl[label] = oneResult

        outFile.write(resColl.getTabularStrRepresentation(columnLabels))
        outFile.close()

    @staticmethod
    def _getResultsLists(histChoices):
        if len([x for x in histChoices.values() if x is not None]) == 0:
            return [],[]

        galaxyTNs = [x.split(':') for x in histChoices.values() if x is not None]

        galaxyFns = [ExternalTrackManager.extractFnFromGalaxyTN(tn) for tn in galaxyTNs]
        historyNames= [ExternalTrackManager.extractNameFromHistoryTN(tn) for tn in galaxyTNs]
        staticFiles = [GalaxyRunSpecificFile(['results.pickle'], gfn) for gfn in galaxyFns]
        #fileSpecificFile = [GalaxyRunSpecificFile([], gfn) for gfn in galaxyFns]

        #paths = [x.getDiskPath()+'/0' for x in fileSpecificFile]
        #pngList = [[v for v in x[2] if v.find('.png')>0] for x in os.walk(paths[0])]

        try:
            resultsLists = [load(sf.getFile('r')) for sf in staticFiles]
        except:
            resultsLists = []

        return resultsLists, historyNames

    @classmethod
    def _getColumnLabels(cls, prevChoices, labelType):
        assert labelType in ['short', 'long']
        resultsLists, historyNames = cls._getResultsLists(prevChoices.history)
        columnLabels = []

        for histName, resultList in zip(historyNames, resultsLists):
            numBatchRuns = len(resultList)
            batchDigits = len(str(numBatchRuns))
            for i in range(len(resultList)):
                batchStr = "{num:0{width}d}".format(num=i, width=batchDigits)
                if labelType == 'short':
                    histNum = histName.split(' - ')[0]
                    columnLabels.append(histNum + ('-' + batchStr if numBatchRuns>1 else ''))
                else: #labelType == 'long'
                    columnLabels.append(histName + (' - ' + batchStr if numBatchRuns>1 else ''))

        return columnLabels

    @staticmethod
    def _getResDictAndLocalKeys(resultsLists):
        from collections import defaultdict
        from copy import copy

        if len(resultsLists)==0:
            return [], []

        allResDictKeysWithCount = defaultdict(int)
        allLocalKeys = set()
        firstLocalKeys = None

        for resultsList in resultsLists:
            for result in resultsList:
                resDictKeys = result.getResDictKeys()
                if len(resDictKeys) != 0:
                    for key in resDictKeys:
                        allResDictKeysWithCount[key] += 1
                allLocalKeys.update(result.keys())
                if not firstLocalKeys:
                    firstLocalKeys = copy(allLocalKeys)

        diffInLocalKeys = firstLocalKeys != allLocalKeys
        allLocalKeys = sorted(allLocalKeys)
        allResDictKeysWithCount = OrderedDict(sorted(allResDictKeysWithCount.iteritems(), \
                                                     key=lambda x: x[0].lower()))

        return allResDictKeysWithCount, allLocalKeys, diffInLocalKeys

    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        if len([x for x in choices.history.values() if x!=None])==0:
            return 'Please select one or more history elements.'

        for galaxyId in choices.history.keys():
            if choices.history[galaxyId]:
                oneHistory = {galaxyId: choices.history[galaxyId]}
                rsl, histNames = cls._getResultsLists(oneHistory)
                if rsl == []:
                    return 'History "%s" does not contain properly stored results.' % histNames[0]

        if choices.stat in [None, '']:
            rsl = cls._getResultsLists(choices.history)[0]
            if rsl == []:
                return 'Please select a result statistic.'

        numResults = sum( len(x) for x in cls._getResultsLists(choices.history)[0] )
        if choices.stat:
            numStatResults = int( choices.stat[choices.stat.find('[')+1:choices.stat.find(']')] )
            if numStatResults != numResults and choices.allowMissing == 'No':
                return 'The selected result statistic is not present in all selected history results ' +\
                       '(only present in %s out of %s results). ' % (numStatResults, numResults) + \
                       'To be able to concatenate the results, the choice "Allow missing values" ' +\
                       'needs to be set to "Yes".'

        if choices.localOrGlobal == 'Local results':
            resultsLists = cls._getResultsLists(choices.history)[0]
            diffInLocalKeys = cls._getResDictAndLocalKeys(resultsLists)[2]
            if diffInLocalKeys and choices.allowMissing == 'No':
                return 'The selected history results differ in the analysis regions for local results. ' +\
                       'To be able to concatenate the results, the choice "Allow missing values" ' +\
                       'needs to be set to "Yes".'

        if choices.printColLabels == 'Yes' and choices.colLabelType == 'Custom labels':
            numLabels = len(choices.colLabels.split('|'))
            if numResults != numLabels:
                return 'The number of custom column labels (%s) is not equal to the number of results (%s). ' % (numLabels, numResults) +\
                       'Please edit the custom column labels.'

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

    @staticmethod
    def getToolDescription():
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        core = HtmlCore()
        core.paragraph('This tool can be used to concatenate HyperBrowser analysis results '
                       'from several different history elements into a single tabular file, '
                       'providing a simple overview of many runs at once. The tool only works on '
                       'history elements created by the tools "Analyze genomic tracks" and '
                       '"Execute batch commands".')
        core.divider()
        core.paragraph('In order to concatenate, you will need to select a single result statistic. '
                       'The tool will then fetch the resulting values of this statistic '
                       'from the different runs in the selected '
                       'history elements. The tool supports concatenation of either global '
                       'or local results. Several formatting options are also provided.')
        core.divider()
        core.paragraph('The resulting table can easily be pasted into spreadsheet programs '
                       'such as Microsoft Excel for further analysis. To look at the data in Excel '
                       'you need to:')
        core.orderedList(['Click the eye icon of the new history element to look at the table',
                          'Click somewhere in the table',
                          'Select "Select All" from the "Edit" menu (or type cmd-A (Mac) or cltr-A (Windows))',
                          'Copy the table (cmd/ctrl-C)', 'Switch to Excel', 'Select "Paste special..." '
                          'from the "Edit" menu.', 'In the dialog box that opens, choose "Text"'])
        return str(core)

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
        return 'tabular'
