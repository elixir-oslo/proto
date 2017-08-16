from gold.util.CustomExceptions import ShouldNotOccurError
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool


#This is a template prototyping GUI that comes together with a corresponding web page.
#

class CreateFunctionTrackAsDistanceToNearestSegments(GeneralGuiTool):
    
    @staticmethod
    def getToolName():
        return "Generate bp-level track of distance to nearest segment"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        #can have two syntaxes: either a list of stings or a list of tuples where each tuple has two items(Name of box on webPage, name of getOptionsBox)
        return [('Genome build: ', 'genome'), \
                ('Fetch track from: ', 'source'), \
                ('Select track: ', 'track'), \
                ('Select track: ', 'history'), \
                ('Select transformation of distances: ', 'transform')]
    
    @staticmethod    
    def getOptionsBoxGenome():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return '__genome__'
    
    @staticmethod    
    def getOptionsBoxSource(prevChoices):
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return ['history', 'HyperBrowser repository']
    
    @staticmethod    
    def getOptionsBoxHistory(prevChoices):
        if prevChoices.source == 'history':
            return '__history__','bed','category.bed','valued.bed','bedgraph','gtrack'
    
    @staticmethod    
    def getOptionsBoxTrack(prevChoices):
        if prevChoices.source == 'HyperBrowser repository':
            return '__track__'
    
    @staticmethod    
    def getOptionsBoxTransform(prevChoices):
        return ['no transformation','logarithmic (log10(x))', 'fifth square root (x**0.2)']

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']

    @staticmethod
    def getDemoSelections():
        return ['sacCer1', 'HyperBrowser repository', 'Genes and gene subsets:Exons', 'None', 'logarithmic (log10(x))']
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
        genome = choices.genome
        
        trackChoice = choices.history if choices.source == 'history' else choices.track
        trackName = trackChoice.split(':')
        
        galaxyOutTrackName = 'galaxy:hbfunction:%s:Create function track of distance to nearest segment' % galaxyFn
        outTrackName = ExternalTrackManager.getStdTrackNameFromGalaxyTN(galaxyOutTrackName.split(':'))
        
        if choices.transform == 'no transformation':
            valTransformation = 'None'
        elif choices.transform =='logarithmic (log10(x))':
            valTransformation = 'log10'
        elif choices.transform == 'fifth square root (x**0.2)':
            valTransformation = 'power0.2'
        else:
            raise ShouldNotOccurError
        
        analysisDef ='[dataStat=MakeDistanceToNearestSegmentStat] [valTransformation=%s][outTrackName=' % valTransformation \
                     + '^'.join(outTrackName) + '] -> CreateFunctionTrackStat'
        #userBinSource, fullRunArgs = GalaxyInterface._prepareRun(trackName, None, analysisDef, '*', '*', genome)
        #
        #for el in userBinSource:
        #    print el.chr, el.start, el.end
            
        from quick.application.GalaxyInterface import GalaxyInterface

        print GalaxyInterface.getHbFunctionOutputBegin(galaxyFn, withDebug=False)
        
        GalaxyInterface.runManual([trackName], analysisDef, '*', '*', genome, username=username, printResults=False, printHtmlWarningMsgs=False)
        #job = AnalysisDefJob(analysisDef, trackName, None, userBinSource).run()
        
        print GalaxyInterface.getHbFunctionOutputEnd('A custom track has been created by finding the bp-distance to the nearest segment', withDebug=False)
        

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        trackChoiceIndex = 'history' if choices.source == 'history' else 'track'
        errorStr = CreateFunctionTrackAsDistanceToNearestSegments._checkTrack(choices, trackChoiceIndex=trackChoiceIndex)
        if errorStr:
            return errorStr
            
        trackType = CreateFunctionTrackAsDistanceToNearestSegments._getBasicTrackFormat(choices, trackChoiceIndex)[-1]
            
        if trackType not in ['segments', 'valued segments']:
            return 'Please select a track of segments. You selected a track with basic type: %s' % trackType

    
    @staticmethod
    def isPublic():
        return True
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    #@staticmethod
    #def isHistoryTool():
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    return []
    #
    @staticmethod
    def getToolDescription():
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        
        core.paragraph('''
This tool generates a function track covering the whole genome, where each base
pair gets a value denoting the distance (in bps) to the nearest element in the
selected track.''')
        core.divider()
        core.paragraph('''
The distance measure may be transformed to other bps-derived values (e.g. the
logarithm or fifth square root of the bps distance), if desired.''')
        
        return str(core)
    #
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    @staticmethod
    def getFullExampleURL():
        return 'u/hb-superuser/p/generate-bp-level-track-of-distance-to-nearest-segment'
    
    #@staticmethod
    #def isDebugMode():
    #    return True
    #
    @staticmethod    
    def getOutputFormat(choices):
        '''The format of the history element with the output of the tool.
        Note that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.
        '''
        return 'hbfunction'
