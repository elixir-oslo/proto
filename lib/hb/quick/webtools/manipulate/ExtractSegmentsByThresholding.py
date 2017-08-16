from collections import OrderedDict

from gold.origdata.FileFormatComposer import findMatchingFileFormatComposers, \
                                             getComposerClsFromFileFormatName
from gold.origdata.GEOverlapClusterer import GEOverlapClusterer_Segment
from gold.origdata.GESourceWrapper import ElementModifierGESourceWrapper
from gold.origdata.GenomeElementSorter import GenomeElementSorter
from gold.origdata.TrackGenomeElementSource import FullTrackGenomeElementSource
from gold.track.TrackFormat import TrackFormat
from gold.util.CustomExceptions import ShouldNotOccurError
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool

RULE_DICT = OrderedDict([('Greater than threshold value', lambda x,y: x > y), \
                         ('Greater than or equal to threshold value', lambda x,y: x >= y), \
                         ('Equal to threshold value', lambda x,y: x == y), \
                         ('Less than or equal to threshold value', lambda x,y: x <= y), \
                         ('Less than threshold value', lambda x,y: x < y)])

class GEValueThresholder(ElementModifierGESourceWrapper):
    def __init__(self, geSource, genome, threshold, rule):
        ElementModifierGESourceWrapper.__init__(self, geSource, genome)
        self._threshold = threshold
        self._rule = rule

    def _iter(self):
        self._prevElement = None
        
    def _next(self, brt, ge, i):
        if ge.start is None:
            if i == 0:
                if brt is not None:
                    ge.start = brt.region.start
                else:
                    raise ShouldNotOccurError
            else:
                ge.start = self._prevElement.end
                
        if ge.end is None:
            ge.end = ge.start + 1
            
        self._prevElement = ge
        
        if self._rule(ge.val, self._threshold):
            ge.val = None
            return ge
        
class GEAdjacencyClusterer_Segment(GEOverlapClusterer_Segment):
    def _overlapsPrev(self, el):
        return el.start <= self._prevEl.end

class ExtractSegmentsByThresholding(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Extract segments where value is greater/less than threshold"

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
        return [('Genome build:', 'genome'),\
                ('Fetch track from:', 'source'), \
                ('Select track:', 'history'), \
                ('Select track:', 'track'), \
                ('Enter treshold value:', 'threshold'), \
                ('Extract segments that are:', 'rule'), \
                ('Merge adjacent segments:', 'merge'), \
                ('Select output file format:', 'format')]

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
        
        Text area:              'textbox' ,  ('textbox',1) ,  ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - Returns: string
        
        Password field:         '__password__'
        - Returns: string
        
        Genome selection box:   '__genome__'
        - Returns: string
        
        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name
        
        History selection box:  ('__history__',) ,  ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.
        
        History check box list: ('__multihistory__', ) ,  ('__multihistory__', 'bed', 'wig')
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
    def getOptionsBoxSource(prevChoices):
        return ['history', 'HyperBrowser repository']
    
    @staticmethod    
    def getOptionsBoxHistory(prevChoices):
        if prevChoices.source == 'history':
            return '__history__', 'wig', 'bedgraph', 'gtrack', 'gff', 'gff3', 'valued.bed', 'hbfunction'
        
    @staticmethod    
    def getOptionsBoxTrack(prevChoices):
        if prevChoices.source == 'HyperBrowser repository':
            return '__track__'
        
    @staticmethod    
    def getOptionsBoxThreshold(prevChoices):
        return '0', 1

    @staticmethod    
    def getOptionsBoxRule(prevChoices):
        return RULE_DICT.keys()

    @staticmethod    
    def getOptionsBoxMerge(prevChoices):
        return ['Yes', 'No']
        
    @staticmethod    
    def getOptionsBoxFormat(prevChoices):
        tf = TrackFormat.createInstanceFromPrefixList(['start', 'end'])
        return [composer.fileFormatName for composer in findMatchingFileFormatComposers(tf)]

    @staticmethod
    def getDemoSelections():
        return ['hg19', 'HyperBrowser repository', 'None', 'Sample data:5hmC, Szulwach et. al.', '80', 'Less than or equal to threshold value', 'No', 'BED']
        
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
        
        genome = choices.genome
        
        trackChoice = choices.history if choices.source == 'history' else choices.track
        trackName = trackChoice.split(':')
        
        if ExternalTrackManager.isGalaxyTrack(trackName):
            geSource = ExternalTrackManager.getGESourceFromGalaxyOrVirtualTN(trackName, genome)
            if not geSource.hasOrigFile(): #hbfunction
                stdTrackName = ExternalTrackManager.getStdTrackNameFromGalaxyTN(trackName)
                ExternalTrackManager.renameExistingStdTrackIfNeeded(genome, stdTrackName)
                geSource = FullTrackGenomeElementSource(genome, stdTrackName, allowOverlaps=False)
        else:
            try:
                geSource = FullTrackGenomeElementSource(genome, trackName, allowOverlaps=True)
                for ge in geSource:
                    break
            except:
                geSource = FullTrackGenomeElementSource(genome, trackName, allowOverlaps=False)
        
        threshold = float(choices.threshold)
        rule = RULE_DICT[choices.rule]
        
        composerCls = getComposerClsFromFileFormatName(choices.format)
        geModifier = GEValueThresholder(geSource, genome, threshold, rule)
        if choices.merge == 'Yes':
            if not geModifier.isSorted():
                geModifier = GenomeElementSorter( geModifier )
            geModifier = GEAdjacencyClusterer_Segment(geModifier)
        
        composerCls( geModifier ).composeToFile(galaxyFn, ignoreEmpty=True)

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        trackChoiceIndex = 'history' if choices.source == 'history' else 'track'
        errorStr = ExtractSegmentsByThresholding._checkTrack(choices, \
                                                             genomeChoiceIndex='genome', \
                                                             trackChoiceIndex=trackChoiceIndex, \
                                                             validateFirstLine=True)
        
        if errorStr:
            return errorStr
            
        #tn = getattr(choices, trackChoiceIndex).split(':')
        #if not ExternalTrackManager.isGalaxyTrack(tn):
        #    for allowOverlaps in [True, False]:
        #        newTypeTrack = BoundingRegionShelve(choices.genome, tn, allowOverlaps).fileExists()
        #        if newTypeTrack:
        #            break
        #    if not newTypeTrack:
        #        return 'Error: this tool only works on tracks that have been preprocessed with ' +\
        #                      'version 1.5 or later of the Genomic HyperBrower. Please, do not ' +\
        #                      'hesitate to contact our group if you would like to use this tool ' +\
        #                      'on the selected track.'
            
        if choices.source == 'HyperBrowser repository':
            valType = ExtractSegmentsByThresholding._getValueTypeName(choices, \
                                                                      tnChoiceIndex=trackChoiceIndex, \
                                                                      genomeChoiceIndex='genome')
            if valType != 'number':
                return 'The selected track does not have single floating point values.'
            
        try:
            float(choices.threshold)
        except:
            return 'Please type a floating point value as threshold. Current value: ' + repr(choices.threshold)
        
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
    @staticmethod
    def getToolDescription():
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        core = HtmlCore()
        core.paragraph('''
This tool extracts segments from an existing track that has floating point
values associated with the genome coordinates. The segments are extracted
according to a threshold value.''')
        core.divider()
        core.smallHeader('Input track')
        core.paragraph('''
The input track can be fetched either from the history or from the HyperBrowser
repository. The only requirement is that each track elements has an associated
floating point value. The track type thus has to be one of "Valued Points",
"Valued Segments", "Step Function", "Function", or one of the linked variants of
these. Note that tracks of type "Function" will work, but will be very slow.''')
        
        core.divider()
        core.smallHeader('Threshold and rule')
        core.paragraph('''
Type in a floating point value as the threshold and select an associated rule.
When the rule is true, the corresponding segment will be written to the output
file.''')
        
        core.divider()
        core.smallHeader('Merge adjacent segments')
        core.paragraph('''
If "Merge adjacent segments" is set to "Yes", any resulting segments that are
adjacent (''' + str(HtmlCore().emphasize('i.e.')) + ''' that have no gaps between
them), are merged into the same segment.''')
        
        core.divider()    
        core.smallHeader('Output format')
        core.paragraph('''
Several output file formats are available. These are all file formats that can
represent segment tracks.''')
        
        core.divider()
        core.smallHeader('Example')
        core.paragraph('Input file:')
        core.styleInfoBegin(styleClass='debug')
        core.append(
'''track type=bedGraph
chr21	10042712	10080194	-0.3655
chr21	10042712	10080194	0.2621
chr21	10079666	10080197	-1.047
chr21	13664826	13665788	-0.1566
chr21	13904368	13935777	1.396
chr21	13973462	13975927	0.007720
chr21	14403007	14439210	-1.021
chr21	14406599	14407013	2.022
chr21	14438228	14438658	-0.2405
chr21	14510257	14522024	-0.1010''')
        core.styleInfoEnd()
        
        core.paragraph('Output file:')
        core.styleInfoBegin(styleClass='debug')
        core.append(
'''chr21	10042712	10080194
chr21	13904368	13935777
chr21	13973462	13975927
chr21	14406599	14407013''')
        core.styleInfoEnd()
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
        return getComposerClsFromFileFormatName(choices.format).getDefaultFileNameSuffix()
