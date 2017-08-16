from collections import OrderedDict

from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.extra.exam.ExamResultsAnalysis import IndividualTaskAnalysis,\
    ExamResultsReader, ExamResultsValidator
from quick.webtools.GeneralGuiTool import GeneralGuiTool


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class IndividualTaskAnalysisTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Individual task scores analysis"

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
                ('Select tasks', 'tasks'),
                ('Select analysis', 'analysis'),
                ('Specify the number of bins', 'bins'),
                ('Specify the smoothing parameter', 'spar'),
                ('Display points in plot', 'displayPoints'),
                ('Specify vertical lines x-values (e.g. 50,60,70,80,90)', 'verticalLines')]

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
    def getOptionsBoxAnalysis(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return IndividualTaskAnalysis.SUBTASK_LIST

    @staticmethod
    def getOptionsBoxTasks(prevChoices):
        if prevChoices.resultsFile:
            taskNames = ExamResultsReader.readTaskNames(
                                                        ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.resultsFile), 
                                                        IndividualTaskAnalysis.REQUIRED_COLUMNS, 
                                                        IndividualTaskAnalysis.OPTIONAL_COLUMNS)
            selected = [True]*len(taskNames)
            return OrderedDict(zip(taskNames,selected))
        return None

    @staticmethod
    def getOptionsBoxBins(prevChoices):
        if prevChoices.analysis == IndividualTaskAnalysis.ANALYSIS_BIN_AVG_SMOOTHED_PLOT:
            return '20'

    @staticmethod
    def getOptionsBoxSpar(prevChoices):
        if prevChoices.analysis in [IndividualTaskAnalysis.ANALYSIS_BIN_AVG_SMOOTHED_PLOT,
                                    IndividualTaskAnalysis.ANALYSIS_MOVING_AVG_SMOOTHED_PLOT]:
            return '0.65'

    @staticmethod
    def getOptionsBoxDisplayPoints(prevChoices):
        if prevChoices.analysis in [IndividualTaskAnalysis.ANALYSIS_BIN_AVG_SMOOTHED_PLOT,
                                    IndividualTaskAnalysis.ANALYSIS_MOVING_AVG_SMOOTHED_PLOT]:
            return OrderedDict([('display', False)])
        
    @staticmethod
    def getOptionsBoxVerticalLines(prevChoices):
        if prevChoices.analysis in [IndividualTaskAnalysis.ANALYSIS_BIN_AVG_SMOOTHED_PLOT,
                                    IndividualTaskAnalysis.ANALYSIS_MOVING_AVG_SMOOTHED_PLOT]:
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
        selectedTasks = [key for key,val in choices.tasks.iteritems() if val]
        bins = int(choices.bins) if choices.bins else 20
        displayPoints = bool(choices.displayPoints['display']) if choices.displayPoints else False
        spar = float(choices.spar) if choices.spar else 1.0
        verticalLines = None
        if choices.verticalLines and \
            choices.analysis in [IndividualTaskAnalysis.ANALYSIS_BIN_AVG_SMOOTHED_PLOT,
                                    IndividualTaskAnalysis.ANALYSIS_MOVING_AVG_SMOOTHED_PLOT]:
            verticalLines = [float(x.strip()) for x in choices.verticalLines.split(',')]
        examAnalysis = IndividualTaskAnalysis(resultsFN, galaxyFn)
        examAnalysis.run(analysis=choices.analysis, selectedTasks=selectedTasks, 
                         bins=bins, displayPoints=displayPoints, spar=spar, verticalLines=verticalLines)  
        
        core = HtmlCore()
        core.begin()
        for plotUrl in examAnalysis.getPlotUrls():
            core.divBegin(divId='plot')
            core.image(plotUrl)
            core.divEnd()
        core.end()
        print core

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
        
        resultsFN = ExternalTrackManager.extractFnFromGalaxyTN(choices.resultsFile)
        errors = ExamResultsValidator.validateExamResultsDataFile(resultsFN, 
                                                                  IndividualTaskAnalysis.REQUIRED_COLUMNS, 
                                                                  IndividualTaskAnalysis.OPTIONAL_COLUMNS)
        if errors:
            if len(errors) > 5:
                errors = errors[0:5]
            return 'First 5 errors reported:<br><br>' + '<br>'.join([str(x) for x in errors]).replace('\n', '<br>')


        
        selectedTasks = [key for key,val in choices.tasks.iteritems() if val]
        if not selectedTasks:
            return 'Please select at least one task'
        
        if choices.analysis == IndividualTaskAnalysis.ANALYSIS_BIN_AVG_SMOOTHED_PLOT:
            if not choices.bins:
                return 'Please specify number of bins'
            try:
                bins = int(choices.bins)
                if bins < 1:
                    return "Number of bins must be 1 or more"
            except:
                return "Bins must be an integer number"
            
        if choices.analysis in [IndividualTaskAnalysis.ANALYSIS_BIN_AVG_SMOOTHED_PLOT,
                                IndividualTaskAnalysis.ANALYSIS_MOVING_AVG_SMOOTHED_PLOT]:
            if not choices.spar:
                return 'Please specify the smoothing parameter'
            else:
                try:
                    spar = float(choices.spar)
                    if spar < 0 or spar > 1:
                        return 'The smoothing parameter must be between 0.0 and 1.0'
                except:
                    return 'The smoothing parameter must be a floating point number between 0.0 and 1.0'
        
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
    @staticmethod
    def isPublic():
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
