from quick.util.CommonFunctions import createHyperBrowserURL
from quick.webtools.GeneralGuiTool import GeneralGuiTool


#This is a template prototyping GUI that comes together with a corresponding web page.
#

class ScatterPlotTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Visualize relation between two tracks across genomic regions"

    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Genome build: ', \
                'Fetch first track from: ', \
                'Select first track: ', \
                'Select first track: ', \
                'Fetch second track from: ', \
                'Select second track: ', \
                'Select second track: ']
                
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
    def getOptionsBox3(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        if prevChoices[1] == 'HyperBrowser repository':
            return '__track__'
        
    
    @staticmethod    
    def getOptionsBox4(prevChoices): # Alternatively: getOptionsBoxKey2()
        '''
        See getOptionsBox1().
        
        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        if prevChoices[1] == 'history':
            return '__history__','bed','point.bed','category.bed','valued.bed','bedgraph','gtrack'
    
    @staticmethod    
    def getOptionsBox5(prevChoices): # Alternatively: getOptionsBoxKey2()
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
    def getOptionsBox6(prevChoices):
        if prevChoices[4] == 'HyperBrowser repository':
            return '__track__'
    
    @staticmethod    
    def getOptionsBox7(prevChoices): # Alternatively: getOptionsBoxKey2()
        '''
        See getOptionsBox1().
        
        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        if prevChoices[4] == 'history':
            return '__history__','bed','point.bed','category.bed','valued.bed','bedgraph','gtrack'

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']
    
    @staticmethod
    def isRedirectTool():
        return True
    
    @staticmethod
    def getRedirectURL(choices):
        chIndex = 2 if choices[1] == 'HyperBrowser repository' else 3   
        genome, trackName1, tf1 = ScatterPlotTool._getBasicTrackFormat(choices, chIndex)
        chIndex = 5 if choices[4] == 'HyperBrowser repository' else 6 
        trackName2, tf2 = ScatterPlotTool._getBasicTrackFormat(choices, chIndex)[1:] 
        if tf1 == 'function' and tf2 == 'function':
            analysis = 'Scatter plot (F, F)'
        elif tf1.split()[-1] in ['points', 'segments'] and tf2 == 'function':
            analysis = 'Scatter plot (P, F)'
        elif tf1 == 'function' and tf2.split()[-1] in ['points', 'segments']:
            analysis = 'Scatter plot (F, P)'
        elif tf1.split()[-1] in ['points', 'segments'] and tf2.split()[-1] in ['points', 'segments']:
            analysis = 'Scatter plot (P, P)'
        else:
            analysis = ''
        
        return createHyperBrowserURL(genome, trackName1, trackName2, analcat='Descriptive statistics', analysis=analysis)
        
    @staticmethod
    def getDemoSelections():
        return ['sacCer1', 'HyperBrowser repository', 'DNA structure:Melting:Melting map','None', 'HyperBrowser repository', 'Genes and gene subsets:Exons','None']
        
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
        core.paragraph('Creates a scatter plot of the relation between two tracks across local bins along the genome.')
        core.divider()
        core.paragraph('Each point in the scatter plot is a summarized value of the two tracks (as x and y-values) in a given bin. Thus, a point corresponds to a bin, the x-axis corresponds to first track, and the y-axis corresponds to second track.')
        core.divider()
        core.paragraph('First, select a genome and two track of interest. Then a full analysis specification page appears, where one can directly start a basic analysis or specify further details on the analysis of interest.')
        return str(core)

    @classmethod    
    def validateAndReturnErrors(cls, choices):
        tnList = []
        for indx in [1,4]:
            chIndx = indx+1 if choices[indx] == 'HyperBrowser repository' else indx+2
            errorStr = cls._checkTrack(choices, chIndx)
            if errorStr:
                return errorStr
            tnList.append(cls._getBasicTrackFormat(choices, chIndx)[-1])
        
        if choices[1] == choices[4]:
            trackIndxs = (2,5) if choices[1] == 'HyperBrowser repository' else (3,6)
            if choices[trackIndxs[0]] not in [None, ''] and choices[trackIndxs[0]] == choices[trackIndxs[1]]:
                return 'Please select two different tracks'
        
        if not all(x in ['points', 'valued points', 'segments', 'valued segments', 'function'] for x in tnList):
            return 'Basic track format must be one of (valued) points, (valued) segments or function. ' +\
                   'Current: %s (track 1), %s (track 2)' % (tnList[0], tnList[1])
            

    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
        
    @staticmethod
    def getFullExampleURL():
        return 'u/hb-superuser/p/scatter-plots'

    #@staticmethod
    #def isDebugMode():
    #    return True
