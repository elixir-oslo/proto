from quick.util.CommonFunctions import createHyperBrowserURL
from quick.webtools.GeneralGuiTool import GeneralGuiTool


#This is a template prototyping GUI that comes together with a corresponding web page.
#

class BinScaledPlotTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Aggregation plot of track elements relative to anchor regions"

    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Genome build: ', \
                'Fetch track from: ', \
                'Select track to visualize: ', \
                'Select track to visualize: ', \
                'Summary statistic: ']

    @staticmethod    
    def getOptionsBox1():
        "Returns a list of options to be displayed in the first options box"
        return '__genome__'
    
    
    @staticmethod    
    def getOptionsBox2(prevChoices): # Alternatively: getOptionsBoxKey2()
        '''
        See getOptionsBox1().
        
        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return ['history', 'HyperBrowser repository']
    
    
    @staticmethod    
    def getOptionsBox3(prevChoices): # Alternatively: getOptionsBoxKey2()
        '''
        See getOptionsBox1().
        
        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        if prevChoices[-2] == 'HyperBrowser repository':
            return '__track__'
    
    @staticmethod    
    def getOptionsBox4(prevChoices): # Alternatively: getOptionsBoxKey2()
        
        if prevChoices[-3] == 'history':
            return '__history__','bed','point.bed','category.bed','valued.bed','bedgraph','gtrack'
    
    
    @staticmethod    
    def getOptionsBox5(prevChoices):
        if prevChoices[-2] not in [None, ''] or prevChoices[-3] not in [None, '']:
            chIndx = 3 if prevChoices[-4] == 'history' else 2
            genome, trackName, tf = BinScaledPlotTool._getBasicTrackFormat(prevChoices, chIndx)
            
            if tf != '' and tf.split()[-1] == 'points':
                return ['Count']
            elif tf != '' and tf.split()[-1] == 'segments':
                return ['Count', 'Base pair coverage']
            elif tf == 'function':
                return ['Average of function values']
            else:
                return None

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']
    @staticmethod
    def isRedirectTool():
        return True
    
    @staticmethod
    def getRedirectURL(choices):
        #genome = choices[0]
        #trackName1 = choices[1].split(':')
        chIndx = 3 if choices[1] == 'history' else 2
        genome, trackName1, tf1 = BinScaledPlotTool._getBasicTrackFormat(choices, chIndx) 
        plot = choices[4]
        if plot == 'Count':
            analysis = 'Aggregation plot of counts'
        elif plot == 'Base pair coverage':
            analysis = 'Aggregation plot of coverage'
        elif plot == 'Average of function values':
            analysis = 'Aggregation plot of values'

        return createHyperBrowserURL(genome, trackName1, [''], analcat='Descriptive statistics', \
                                     analysis=analysis, configDict={'Resolution': '100'})
    
    @staticmethod
    def getDemoSelections():
        return ['sacCer1', 'HyperBrowser repository', 'Genes and gene subsets:Exons', 'None', 'Count']
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
        print 'Executing...'

    @staticmethod
    def isPublic():
        return True
    #
    @staticmethod
    def getToolDescription():
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.paragraph('''
Used to reveal trends of how track elements are distributed relative to a set of
anchor regions (bins). All anchor regions are divided into the same number of
sub-bins, and a summary statistic is calculated for each sub-bin and averaged
across all anchor regions. The tool returns a plot of the average values with
95% confidence intervals.''')
        core.paragraph('''
First, select a genome and a track of interest. Secondly, select a summary
statistic, and click "Execute". Then a full analysis specification page appears,
where one can directly start a basic analysis or specify further details on the
analysis of interest. Here, you can select the bins across which the aggregation
plot is created.''')
        return str(core)
    
    @classmethod    
    def validateAndReturnErrors(cls, choices):
        chIndx = 3 if choices[1] == 'history' else 2
        errorStr = cls._checkTrack(choices, chIndx)
        if errorStr:
            return errorStr
        
        trackType = cls._getBasicTrackFormat(choices, chIndx)[-1]
            
        if trackType not in ['segments','points', 'valued segments', 'valued points', 'function']:
        
            return 'Basic track format must be one of (valued) points, (valued) segments or function. ' +\
                   'Current: %s' % trackType
        
    #    
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    
    @staticmethod
    def getFullExampleURL():
        return 'u/hb-superuser/p/aggregation-and-relative-localization-plots'

    #@staticmethod
    #def isDebugMode():
    #    return True
