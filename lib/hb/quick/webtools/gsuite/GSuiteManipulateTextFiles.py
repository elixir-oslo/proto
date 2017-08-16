import os
from collections import OrderedDict
from itertools import chain

from config.Config import IS_EXPERIMENTAL_INSTALLATION
from gold.gsuite import GSuiteConstants
from gold.gsuite.GSuiteFunctions import changeSuffixIfPresent
from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class GSuiteManipulateTextFiles(GeneralGuiTool):

    # Constants

    NUM_EXAMPLE_LINES = 12
    NUM_PARAM_BOXES = 10

    ALL_PUBLIC_OPERATIONS = dict([('Output only selected columns', 'CutColumns'),
                                  ('Convert ICGC to GTrack', 'ICGCToGTrack'),
                                  ('Convert Broadpeak to GTrack', 'BroadpeakToGTrack'),
                                  ('Convert Narrowpeak to GTrack', 'NarrowpeakToGTrack'),
                                  ('Remove duplicate lines', 'RemoveDuplicateLines'),
                                  ('Filter GTrack by segment length', 'FilterGTrackByGELength'),
                                  ('Expand all points and segments equally', 'ExpandBedSegments'),
                                  ('Subsample elements of each track', 'SubsampleTracks')
                                  ])

    ALL_PRIVATE_OPERATIONS = dict([('Shuffle and add columns', 'ShuffleAndAddColumns'),
                                   ('Convert vcf to 3-column bed', 'ConvertVcfTo3ColBed'),
                                   ('Convert maf to 3-column bed', 'ConvertMafTo3ColBed')
                                  ])

    ALL_OPERATIONS = OrderedDict(sorted(dict(ALL_PUBLIC_OPERATIONS, **ALL_PRIVATE_OPERATIONS).iteritems())) \
        if IS_EXPERIMENTAL_INSTALLATION else \
            OrderedDict(sorted(ALL_PUBLIC_OPERATIONS.iteritems()))

    NO_OPERATION_TEXT = '-- Select --'
    NO_PARAM_TEXT = '-- Select --'

    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PRIMARY, GSuiteConstants.UNKNOWN]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]

    GSUITE_OUTPUT_LOCATION = GSuiteConstants.LOCAL
    GSUITE_OUTPUT_FILE_FORMAT = 'as input, but may be changed if a new file suffix is selected'
    GSUITE_OUTPUT_TRACK_TYPE = 'as input, but may be changed according to the selected operation'

    OUTPUT_DESCRIPTION = ', tracks manipulated'

    # Methods

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Modify primary tracks referred to in a GSuite"

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

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('Select GSuite file from history: ', 'history'),
                ('Example track (from GSuite): ', 'exampleTrack'),
                ('First %s lines of text file for example track: ' \
                  % cls.NUM_EXAMPLE_LINES, 'firstLinesIn'),
                ('Select operation: ', 'operation')] +\
                [x for x in chain(*((('Select parameter: ', 'param%s' % i), \
                                     ('Type in value for parameter: ', 'paramValue%s' % i)) \
                 for i in xrange(cls.NUM_PARAM_BOXES)))] + \
                [('First %s lines of example track text file after manipulation: ' \
                  % cls.NUM_EXAMPLE_LINES, 'firstLinesOut'),
                ('Change file suffix (e.g. "bed") of output tracks?', 'changeSuffix'),
                ('New file suffix for all output tracks', 'suffix')]

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
    def setupParameterOptionBoxes(cls):
        from functools import partial
        for i in xrange(cls.NUM_PARAM_BOXES):
            setattr(cls, 'getOptionsBoxParam%s' % i, partial(cls.getParamOptionsBox, i))
            setattr(cls, 'getOptionsBoxParamValue%s' % i, partial(cls.getParamValueOptionsBox, i))

    @staticmethod
    def getOptionsBoxHistory(): # Alternatively: getOptionsBox1()
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

    @staticmethod
    def getOptionsBoxExampleTrack(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        if prevChoices.history:
            try:
                gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
                if gSuite.fileFormat in [GSuiteConstants.PRIMARY, GSuiteConstants.UNKNOWN]:
                    return [x for x in gSuite.allTrackTitles()]
            except:
                pass

    @classmethod
    def _getExampleContents(cls, fn):
        with open(fn) as trackFile:
            contents = ''
            for i in xrange(cls.NUM_EXAMPLE_LINES):
                contents += trackFile.readline()
        return contents

    @classmethod
    def _getExampleLines(cls, prevChoices):
        gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
        gSuiteTrack = gSuite.getTrackFromTitle(prevChoices.exampleTrack)
        return cls._getExampleContents(gSuiteTrack.path)

    @classmethod
    def getOptionsBoxFirstLinesIn(cls, prevChoices):
        if prevChoices.exampleTrack:
            try:
                return cls._getExampleLines(prevChoices), cls.NUM_EXAMPLE_LINES, True
            except:
                pass

    @classmethod
    def getOptionsBoxOperation(cls, prevChoices):
        if prevChoices.exampleTrack:
            return [cls.NO_OPERATION_TEXT] + cls.ALL_OPERATIONS.keys()

    @classmethod
    def _getAllParamsWithDefaultValues(cls, prevChoices):
        from quick.extra.StandardizeTrackFiles import getFormattedParamList
        formattedParamList = getFormattedParamList(cls.ALL_OPERATIONS[prevChoices.operation])
        paramDict = OrderedDict()
        for param in formattedParamList:
            if '=' in param:
                key, default = param.split('=')
                if default.startswith('"') and default.endswith('"'):
                    default = default[1:-1]
                paramDict[key] = default
            else:
                paramDict[param] = ''

        return paramDict

    @staticmethod
    def _getParamKeyFromListedParam(prevChoices, index):
        listedParam = getattr(prevChoices, 'param%s' % index)
        if listedParam:
            defaultStart = listedParam.find(' (')
            if defaultStart == -1:
                return listedParam
            else:
                return listedParam[:defaultStart]

    @classmethod
    def getParamOptionsBox(cls, index, prevChoices):
        if prevChoices.operation and prevChoices.operation != cls.NO_OPERATION_TEXT:
            prevParamChoices = set([cls._getParamKeyFromListedParam(prevChoices, i) for i in xrange(index)])
            paramDict = cls._getAllParamsWithDefaultValues(prevChoices)

            if index < len(paramDict):
                unselectedParamList = ['%s (default: %s)' % (key, val) for key,val
                                       in paramDict.iteritems() if key not in prevParamChoices]
                if len(unselectedParamList) > 0:
                    return [cls.NO_PARAM_TEXT] + unselectedParamList

    @classmethod
    def getParamValueOptionsBox(cls, index, prevChoices):
        paramChoice = cls._getParamKeyFromListedParam(prevChoices, index)
        if paramChoice and paramChoice != cls.NO_PARAM_TEXT:
            paramDict = cls._getAllParamsWithDefaultValues(prevChoices)
            return paramDict[paramChoice]

    @classmethod
    def _getAllParamsWithChoices(cls, prevChoices):
        paramDict = cls._getAllParamsWithDefaultValues(prevChoices)

        for i in xrange(cls.NUM_PARAM_BOXES):
            paramChoice = cls._getParamKeyFromListedParam(prevChoices, i)
            if paramChoice is not None and paramChoice != cls.NO_PARAM_TEXT:
                paramValue = getattr(prevChoices, 'paramValue%s' % i)
                paramDict[paramChoice] = paramValue

        return paramDict

    @classmethod
    def _runOperation(cls, prevChoices, inFn, outFn):
        from quick.extra.StandardizeTrackFiles import runParserClassDirectly
        parserClassName = cls.ALL_OPERATIONS[prevChoices.operation]
        paramDict = cls._getAllParamsWithChoices(prevChoices)
        runParserClassDirectly(parserClassName, inFn, outFn, **paramDict)

    @classmethod
    def _runOperationOnExampleDataAndReturnOutput(cls, prevChoices):
        from tempfile import NamedTemporaryFile

        inFile = NamedTemporaryFile()
        inFile.write(cls._getExampleLines(prevChoices))
        inFile.flush()

        outFile = NamedTemporaryFile()
        cls._runOperation(prevChoices, inFile.name, outFile.name)
        outFile.flush()

        return cls._getExampleContents(outFile.name)

    @classmethod
    def getOptionsBoxFirstLinesOut(cls, prevChoices):
        if prevChoices.operation and prevChoices.operation != cls.NO_OPERATION_TEXT:
            try:
                return cls._runOperationOnExampleDataAndReturnOutput(prevChoices), cls.NUM_EXAMPLE_LINES, True
            except:
                pass

    @classmethod
    def getOptionsBoxChangeSuffix(cls, prevChoices):
        if prevChoices.operation and prevChoices.operation != cls.NO_OPERATION_TEXT:
            return ['No', 'Yes']

    @staticmethod
    def _getTrackSuffix(gSuiteTrack):
        if gSuiteTrack.suffix:
            return gSuiteTrack.suffix
        else:
            return 'txt'

    @classmethod
    def _getSuffix(cls, choices, gSuiteTrack):
        if choices.changeSuffix == 'Yes':
            return choices.suffix
        else:
            return cls._getTrackSuffix(gSuiteTrack)

    @classmethod
    def getOptionsBoxSuffix(cls, prevChoices):
        if prevChoices.changeSuffix == 'Yes':
            try:
                gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
                for track in gSuite.allTracks():
                    return cls._getTrackSuffix(track)
            except:
                pass

    @classmethod
    def getInfoForOptionsBoxOperation(cls, prevChoices):
        '''
        If not None, defines the string content of an clickable info box beside
        the corresponding input box. HTML is allowed.
        '''
        if prevChoices.operation and prevChoices.operation != cls.NO_OPERATION_TEXT:
            from quick.extra.StandardizeTrackFiles import getParserClassDocString
            from proto.hyperbrowser.HtmlCore import HtmlCore

            docString = getParserClassDocString(cls.ALL_OPERATIONS[prevChoices.operation])

            core = HtmlCore()
            for line in docString.split(os.linesep):
                core.line(line)

            return str(core)

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @classmethod
    def getExtraHistElements(cls, choices):
        from quick.webtools.GeneralGuiTool import HistElement
        from gold.gsuite.GSuiteConstants import GSUITE_SUFFIX, GSUITE_STORAGE_SUFFIX
        
        fileList = [HistElement(getGSuiteHistoryOutputName(
                        'nomanipulate', datasetInfo=choices.history), GSUITE_SUFFIX)]
        fileList += [HistElement(getGSuiteHistoryOutputName(
                         'primary', cls.OUTPUT_DESCRIPTION, choices.history), GSUITE_SUFFIX)]
        fileList += [HistElement(getGSuiteHistoryOutputName(
                         'storage', cls.OUTPUT_DESCRIPTION, choices.history),
                         GSUITE_STORAGE_SUFFIX, hidden=True)]

        return fileList

        # if choices.history:
        #     try:
        #         #gSuite = getGSuiteFromGalaxyTN(choices.history)
        #
        #         #for track in gSuite.allTracks():
        #         #    suffix = cls._getSuffix(choices, track)
        #         #    title, titleSuffix = os.path.splitext(track.title)
        #         #    title += '.' + suffix
        #         #    histElementsDef += [HistElement(title, suffix, hidden=True)]
        #
        #         fileList.append( HistElement(cls.HISTORY_HIDDEN_TRACK_STORAGE, GSUITE_STORAGE_SUFFIX, hidden=True))
        #         return fileList
        #     except:
        #         pass

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

        from gold.gsuite.GSuite import GSuite
        from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
        from gold.gsuite.GSuiteComposer import composeToFile
        from gold.gsuite.GSuiteFunctions import getTitleWithSuffixReplaced
        from quick.gsuite.GSuiteHbIntegration import \
            writeGSuiteHiddenTrackStorageHtml
        from quick.extra.ProgressViewer import ProgressViewer
        from quick.util.CommonFunctions import ensurePathExists

        gSuite = getGSuiteFromGalaxyTN(choices.history)
        outGSuite = GSuite()
        errorGSuite = GSuite()

        progressViewer = ProgressViewer([('Manipulate tracks', gSuite.numTracks())], galaxyFn)

        hiddenStorageFn = cls.extraGalaxyFn[getGSuiteHistoryOutputName(
                                             'storage', cls.OUTPUT_DESCRIPTION, choices.history)]

        for track in gSuite.allTracks():
            newSuffix = cls._getSuffix(choices, track)

            fileName = os.path.basename(track.path)
            fileName = changeSuffixIfPresent(fileName, oldSuffix=track.suffix, newSuffix=newSuffix)
            title = getTitleWithSuffixReplaced(track.title, newSuffix)

            try:
                if fileName.endswith('.' + newSuffix):
                    uri = GalaxyGSuiteTrack.generateURI(galaxyFn=hiddenStorageFn,
                                                        extraFileName=fileName)
                else:
                    uri = GalaxyGSuiteTrack.generateURI(galaxyFn=hiddenStorageFn,
                                                        extraFileName=fileName,
                                                        suffix=newSuffix)
                
                gSuiteTrack = GSuiteTrack(uri, title=title, genome=track.genome,
                                          attributes=track.attributes)

                trackFn = gSuiteTrack.path
                ensurePathExists(trackFn)
                cls._runOperation(choices, track.path, trackFn)

                outGSuite.addTrack(gSuiteTrack)

            except Exception as e:
                track.comment = 'An error occurred for the following track: ' + str(e)
                errorGSuite.addTrack(track)

            progressViewer.update()

        primaryFn = cls.extraGalaxyFn[getGSuiteHistoryOutputName(
                                       'primary', cls.OUTPUT_DESCRIPTION, choices.history)]

        composeToFile(outGSuite, primaryFn)

        errorFn = cls.extraGalaxyFn[getGSuiteHistoryOutputName(
                                     'nomanipulate', datasetInfo=choices.history)]
        composeToFile(errorGSuite, errorFn)

        writeGSuiteHiddenTrackStorageHtml(hiddenStorageFn)


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
        if gSuite.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        errorStr = cls._checkGSuiteRequirements(
            gSuite,
            allowedFileFormats = cls.GSUITE_ALLOWED_FILE_FORMATS,
            allowedLocations = cls.GSUITE_ALLOWED_LOCATIONS)
        if errorStr:
            return errorStr

        if choices.operation:
            if choices.operation == cls.NO_OPERATION_TEXT:
                return 'Please select an operation to perform on the input tracks'
            else:
                try:
                    cls._runOperationOnExampleDataAndReturnOutput(choices)
                except Exception as e:
                    return 'An error occured testing operation "%s": ' % choices.operation + str(e)

            if choices.changeSuffix == 'Yes' and choices.suffix.strip() == '':
                return 'Please select a file suffix'

    @classmethod
    def getOutputName(cls, choices):
        return getGSuiteHistoryOutputName('progress', cls.OUTPUT_DESCRIPTION, choices.history)

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
    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()
        core.paragraph('This tool contains various operations for manipulating textual '
                       'track files referred to in a GSuite file.')
        core.divider()
        core.smallHeader('Instructions')
        core.orderedList(['Select a GSuite file referring to local textual track files',
                          'The first track referred to in the GSuite is automatically selected '
                          'as an example track, with the beginning of the file shown in a '
                          'text box. The example file is later used to show the results of the '
                          'selected operation. If you want to use another file as the example track '
                          'please select it in the selection box. ',
                          'Select the required operation from the list of operations '
                          '(click the info box if you need further description of each operation '
                          'and its parameters):' +
                          str(HtmlCore().unorderedList([key for key in cls.ALL_OPERATIONS.keys()])),
                          'Each parameter for the selected operation is shown in a selection box, '
                          'with the default value indicated. If another value than the default is '
                          'needed, please select the parameter and change its value. '
                          'the order in which the parameters is selected is unimportant.',
                          'The output of the selected operation with the selected parameter values '
                          'on the beginning of the selected example track is shown in a text box.',
                          'If the file format (e.g. "bed") of the track is changed as a result of '
                          'carrying out the operation, please indicate the new file suffix. '
                          'It is important for the tracks to have the correct file suffix for further '
                          'analysis.'])

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      outputLocation=cls.GSUITE_OUTPUT_LOCATION,
                                      outputFileFormat=cls.GSUITE_OUTPUT_FILE_FORMAT,
                                      outputTrackType=cls.GSUITE_OUTPUT_TRACK_TYPE,
                                      errorFile=True)

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
    #     return 'u/hb-superuser/p/manipulate-textual-track-files-referred-to-in-gsuite---example'
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

GSuiteManipulateTextFiles.setupParameterOptionBoxes()
