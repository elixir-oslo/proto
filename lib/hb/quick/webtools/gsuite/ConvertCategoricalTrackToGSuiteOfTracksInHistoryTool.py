from quick.webtools.GeneralGuiTool import GeneralGuiTool
from _collections import defaultdict
from quick.application.ExternalTrackManager import ExternalTrackManager
from gold.origdata.GESourceWrapper import ListGESourceWrapper
from gold.gsuite.GSuite import GSuite
from collections import OrderedDict
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from gold.gsuite import GSuiteComposer
from gold.origdata.BedComposer import BedComposer
from gold.origdata.GtrackComposer import StdGtrackComposer
from gold.origdata.FastaComposer import FastaComposer
from gold.origdata.GffComposer import GffComposer
from gold.track.TrackFormat import TrackFormat

# This is a template prototyping GUI that comes together with a corresponding
# web page.

class ConvertCategoricalTrackToGSuiteOfTracksInHistoryTool(GeneralGuiTool):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Convert categorical track to GSuite of tracks in history"

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
        return [('Select genome','genome'),
                ('Select categorical track from history', 'catTrack'),
                ('Select ouput type', 'outputType')]

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
    def getOptionsBoxGenome(): # Alternatively: getOptionsBox1()
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
        return '__genome__'

    @staticmethod
    def getOptionsBoxCatTrack(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return GeneralGuiTool.getHistorySelectionElement('bed', 'gtrack', 'gff', 'fasta', 'category.bed')

    @staticmethod
    def getOptionsBoxOutputType(prevChoices):
        return ['bed', 'gtrack', 'gff', 'fasta']

    #@staticmethod
    #def getOptionsBox4(prevChoices):
    #    return ['']

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
        categoryToGenomeElementListDict = defaultdict(list)
        genome = choices.genome
        outputType = choices.outputType 
        catTrack = choices.catTrack.split(':')
        geSource = ExternalTrackManager.getGESourceFromGalaxyOrVirtualTN(catTrack, genome)
        for ge in geSource:
            categoryToGenomeElementListDict[ge.val].append(ge)
            
        for category, genomeElementList in categoryToGenomeElementListDict.iteritems():
            geSourceWrapper = ListGESourceWrapper(geSource, genomeElementList)
            composer = cls.getComposer(geSourceWrapper, outputType)
#             staticFile = GalaxyRunSpecificFile(catTrack + [category, outputType], galaxyFn)
            composer.composeToFile(cls.extraGalaxyFn[category])
            
        outGSuite = GSuite()
        for category, galaxyFileName in OrderedDict([(x, cls.extraGalaxyFn[x]) for x in categoryToGenomeElementListDict.keys()]).iteritems():
            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFileName, suffix=outputType)
            outGSuite.addTrack(GSuiteTrack(uri, title=category, genome=genome))
        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['GSuite from categorical'])     
        
        print 'Execution done!'
        

    @classmethod
    def getComposer(cls, geSource, outputType):
        if outputType == 'bed':
            return BedComposer(geSource)
        if outputType == 'gtrack':
            return StdGtrackComposer(geSource)
        if outputType == 'fasta':
            return FastaComposer(geSource)
        if outputType == 'gff':
            return GffComposer(geSource)
        
    @classmethod
    def getExtraHistElements(cls, choices):
        if choices.genome and choices.catTrack:
            from quick.webtools.GeneralGuiTool import HistElement
            genome = choices.genome
            outputType = choices.outputType 
            catTrack = choices.catTrack.split(':')
            geSource = ExternalTrackManager.getGESourceFromGalaxyOrVirtualTN(catTrack, genome)
            return [HistElement(ge.val, outputType) for ge in geSource] + [HistElement('GSuite from categorical', 'gsuite')]

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        if not choices.genome:
            return 'Please select genome'
        
        if not choices.catTrack:
            return 'Please select categorical track from history'
        
        
        geSource = ExternalTrackManager.getGESourceFromGalaxyOrVirtualTN(choices.catTrack.split(':'), choices.genome)
        
        trackFormat = TrackFormat.createInstanceFromGeSource(geSource)

        if trackFormat.getValTypeName() != 'Category':
            return 'Please select <b>categorical</b> track from history, current is of type ' + trackFormat.getValTypeName()
