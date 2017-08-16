from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ProcTrackOptions import ProcTrackOptions
from quick.util.CommonFunctions import createHyperBrowserURL
from quick.webtools.GeneralGuiTool import GeneralGuiTool


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class ColocalizationIn3DTool(GeneralGuiTool):
    PARENT_TRACKNAME = ['DNA structure', 'Hi-C']

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Analyze spatial colocalization of track elements (in 3D)"

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
        return  [('Select genome build', 'genome'), \
                 ('Use inter- or intrachromosomal interactions', 'interactions'), \
                 ('Select cell line', 'cellLine'), \
                 ('Select dataset and resolution', 'dataset'), \
                 ('Fetch query track from', 'source'), \
                 ('Select track to analyze', 'history'), \
                 ('Select track to analyze', 'track')]

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
    def getOptionsBoxGenome(): # Alternatively: getOptionsBoxKey1()
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
        return '__genome__'

    @staticmethod
    def getOptionsBoxInteractions(prevChoices): # Alternatively: getOptionsBoxKey2()
        '''
        See getOptionsBox1().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        #if prevChoices.genome == 'hg19':
        if prevChoices.genome in ['hg19', 'mm9']:
            parentTrack = ColocalizationIn3DTool.PARENT_TRACKNAME
            return ProcTrackOptions.getSubtypes(prevChoices.genome, parentTrack, fullAccess=False)

    @staticmethod
    def getOptionsBoxCellLine(prevChoices):
        #if prevChoices.genome == 'hg19':
        if prevChoices.genome in ['hg19', 'mm9']:
            parentTrack = ColocalizationIn3DTool.PARENT_TRACKNAME + [prevChoices.interactions]
            return ProcTrackOptions.getSubtypes(prevChoices.genome, parentTrack, fullAccess=False)

    @staticmethod
    def getOptionsBoxDataset(prevChoices):
        #if prevChoices.genome == 'hg19':
        if prevChoices.genome in ['hg19', 'mm9']:
            parentTrack = ColocalizationIn3DTool.PARENT_TRACKNAME + [prevChoices.interactions] + [prevChoices.cellLine]
            return ProcTrackOptions.getSubtypes(prevChoices.genome, parentTrack, fullAccess=False)

    @staticmethod
    def getOptionsBoxSource(prevChoices):
        #if prevChoices.genome == 'hg19':
        if prevChoices.genome in ['hg19', 'mm9']:
            return ['history', 'HyperBrowser repository']

    @staticmethod
    def getOptionsBoxHistory(prevChoices):
        if prevChoices.genome in ['hg19', 'mm9'] and prevChoices.source == 'history':
        #if prevChoices.genome == 'hg19' and prevChoices.source == 'History':
            return '__history__', 'gtrack', 'bed', 'point.bed', 'category.bed', 'gff', 'gff3'

    @staticmethod
    def getOptionsBoxTrack(prevChoices):
        if prevChoices.genome in ['hg19', 'mm9'] and prevChoices.source == 'HyperBrowser repository':
        #if prevChoices.genome == 'hg19' and prevChoices.source == 'HyperBrowser repository':
            return '__track__'

    @staticmethod
    def getDemoSelections():
        return ['hg19','Inter- and intrachromosomal','IMR90','1mb','HyperBrowser repository','None','Genes and gene subsets:Gene subsets:Gene ontology:Biological process:lung development']

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

        print 'Executing...'

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        #if choices.genome != 'hg19':
        if choices.genome not in ['hg19', 'mm9']:
            return '3D colocalization analysis is currently only available for the genome builds "Human Feb. 2009 (hg19/GRCh37)" and "Mouse July 2007 (mm9)"'

        trackChoice = 'history' if choices.source == 'history' else 'track'
        errorStr = ColocalizationIn3DTool._checkTrack(choices, trackChoice, 'genome')
        if errorStr:
            return errorStr

        genome, trackName1, tf = ColocalizationIn3DTool._getBasicTrackFormat(choices, trackChoice)

        if tf not in ['points', 'segments', 'valued points', 'valued segments']:
            return 'The selected track is not of suitable track type. Please select a point or segment track.'

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
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True

    @staticmethod
    def isRedirectTool():
        '''
        Specifies whether the tool should redirect to an URL when the Execute
        button is clicked.
        '''
        return True

    @staticmethod
    def getRedirectURL(choices):
        '''
        This method is called to return an URL if the isRedirectTool method
        returns True.
        '''
        genome = choices[0]
        trackName1 = ColocalizationIn3DTool.PARENT_TRACKNAME + [choices[1]] + [choices[2]] + [choices[3]]
        trackName2 = choices[5].split(':') if choices[4] == 'history' else choices[6].split(':')
        return createHyperBrowserURL(genome, trackName1, trackName2, analcat='Hypothesis testing', analysis='Colocalized in 3D?')

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
        core = HtmlCore()
        core.paragraph('Analyze a selected track of genome locations for spatial co-localization with '
                       'respect to the three-dimensional structure of the genome, as defined using '
                       'results from recent Hi-C experiments. The Hi-C data has been corrected for bias '
                       'using a method presented in a recent manuscript (submitted), and further '
                       'normalized by subtracting the expected signal given the sequential distance '
                       'between elements.')

        core.divider()
        core.smallHeader('References')
        core.paragraph('Paulsen, Jonas, Tonje G. Lien, Geir Kjetil Sandve, Lars Holden, &Oslash;rnulf Borgan, ' +\
                       'Ingrid K. Glad, and Eivind Hovig. "' +\
                       str(HtmlCore().link('Handling realistic assumptions in hypothesis testing of 3D co-localization of genomic elements.',
                                           'http://nar.oxfordjournals.org/content/41/10/5164.full')) + \
                       '" Nucleic acids research 41, no. 10 (2013): 5164-5174.')

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

    @staticmethod
    def getFullExampleURL():
        return 'u/hb-superuser/p/3d-co-localization-analysis'

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
