# Copied and modified from gops_subtract.py from Galaxy codebase

import fileinput
import sys
import tempfile

from bx.intervals.io import NiceReaderWrapper, ParseError
from bx.intervals.operations.subtract import subtract

from galaxy.tools.util.galaxyops import fail, skipped
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class CreateCaseControlTrack(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Combine two BED files into single case-control track"

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
        return [('Select genome build: ', 'genome'), \
                ('Select track to be used as case: ', 'case'), \
                ('Select track to be used as control: ', 'control'), \
                ('Shared regions should be: ', 'shared')] #Alternatively: [ ('box1','key1'), ('box2','key2') ]

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
    def getOptionsBoxCase(prevChoices): # Alternatively: getOptionsBoxKey2()
        '''
        See getOptionsBox1().
        
        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return '__history__', 'bed', 'point.bed', 'category.bed', 'valued.bed'
    
    @staticmethod    
    def getOptionsBoxControl(prevChoices): # Alternatively: getOptionsBoxKey2()
        '''
        See getOptionsBox1().
        
        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return '__history__', 'bed', 'point.bed', 'category.bed', 'valued.bed'
        
    @staticmethod    
    def getOptionsBoxShared(prevChoices):
        return ['removed', 'returned as case regions', 'returned as control regions', 'returned as they are (possibly overlapping)']

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
    
    @classmethod
    def subtract_files(cls, fn1, fn2, out_fn):
        g1 = NiceReaderWrapper( fileinput.FileInput( fn1 ),fix_strand=True )    
        g2 = NiceReaderWrapper( fileinput.FileInput( fn2 ), fix_strand=True )
    
        out_file = open( out_fn, "w" )
        try:
            for feature in subtract( [g1,g2], pieces=True, mincols=1 ):
                out_file.write( "%s\n" % feature )
        except ParseError, exc:
            out_file.close()
            fail( "Invalid file format: %s" % str( exc ) )

        out_file.close()

        if g1.skipped > 0:
            print skipped( g1, filedesc=" of 2nd dataset" )
        if g2.skipped > 0:
            print skipped( g2, filedesc=" of 1st dataset" )

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
        
        orig_case = ExternalTrackManager.extractFnFromGalaxyTN(choices.case.split(':'))
        orig_control = ExternalTrackManager.extractFnFromGalaxyTN(choices.control.split(':'))
        out_case = orig_case
        out_control = orig_control
        output = galaxyFn
    
        if choices.shared in ['removed', 'returned as control regions']:
            case_minus_control = tempfile.NamedTemporaryFile()
            cls.subtract_files(orig_case, orig_control, case_minus_control.name)
            out_case = case_minus_control.name
        
        if choices.shared in ['removed', 'returned as case regions']:
            control_minus_case = tempfile.NamedTemporaryFile()
            cls.subtract_files(orig_control, orig_case, control_minus_case.name)
            out_control = control_minus_case.name

        sys.stdout = open(output, "w", 0)
        GalaxyInterface.combineToTargetControl(out_case, out_control, output)    

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        for choiceIndex in [1,2]:
            errorStr = CreateCaseControlTrack._checkTrack(choices, trackChoiceIndex=choiceIndex)
            if errorStr:
                return errorStr
                
        if choices[1] == choices[2] and choices[1] not in [None, '']:
            return 'Please select two different tracks'
        
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
    @staticmethod
    def getToolDescription():
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.paragraph('''
This tool combines elements from two separate data sets into a single track where
the elements are denoted as case (target) or control, depending on their source.
This allows analyses of how other tracks preferentially interact with case
elements as opposed to control elements.''')
        core.divider()
        core.smallHeader('Shared regions')
        core.paragraph('''
This tool supports four ways of handling regions that are found in both case and
control tracks. These regions do not need to be full segments, as defined in the
input tracks; the tool also correctly handles shared parts of segments.''')
        core.descriptionLine('Shared regions should be removed', \
            'the shared regions are not returned, neither as case nor as control segments')
        core.descriptionLine('Shared regions should be returned as case regions', \
            'the shared regions are all denoted as case regions and returned')
        core.descriptionLine('Shared regions should be returned as control regions', \
            'the shared regions are all denoted as control regions and returned')
        core.descriptionLine('Shared regions should be returned as they are', \
            '''
the shared regions are not handled in any way, but denoted according to whether
they were found in the case or the control input track. Note that this may
result in case and control regions that overlap. The subsequent analysis may not
handle this correctly.''')
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
    @staticmethod
    def getFullExampleURL():
        return 'u/hb-superuser/p/combining-bed-files-into-case-control-track'

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
        return 'targetcontrol.bedgraph'
