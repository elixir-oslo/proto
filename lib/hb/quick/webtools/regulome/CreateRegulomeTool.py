from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.util.CommonFunctions import createHyperBrowserURL
from quick.application.ExternalTrackManager import ExternalTrackManager
from urllib import unquote
#This is a template prototyping GUI that comes together with a corresponding web page.
#

class CreateRegulomeTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Create regulome from history"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Genome build', 'Select row track, e.g. TFs, (Valued Points, categorical)', \
                'Select column track, e.g. diseases, (Valued Segments,  categorical)', \
                'Normalize on']

    @staticmethod    
    def getOptionsBox1():
        return '__genome__'
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        return '__history__', 'category.bed'
    
    @staticmethod    
    def getOptionsBox3(prevChoices):
        return '__history__', 'category.bed'
        
    @staticmethod    
    def getOptionsBox4(prevChoices):
        return ['Both rows and columns (focusing on column differences)', \
                'Rows only (focusing on column similarities)']
    
    #@staticmethod    
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
        
    #@staticmethod    
    #def execute(choices, galaxyFn=None, username=''):
    #    '''Is called when execute-button is pushed by web-user.
    #    Should print output as HTML to standard out, which will be directed to a results page in Galaxy history. If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.gtr
    #    If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
    #    choices is a list of selections made by web-user in each options box.
    #    '''
    #    print 'Executing...'

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        if choices[1] is None:
            return 'Row track has not been selected.'
        if choices[2] is None:
            return 'Column track has not been selected.'
        if choices[1] == choices[2]:
            return 'Please select different tracks as rows and columns.'
        return None
    
    @staticmethod
    def isPublic():
        return True
    
    @staticmethod
    def isRedirectTool():
        return True
        
    @staticmethod
    def getRedirectURL(choices):
        
        genome = choices[0]
        track1file = ExternalTrackManager.createSelectValueFromGalaxyTN(choices[1])
        track2file = ExternalTrackManager.createSelectValueFromGalaxyTN(choices[2])
        return createHyperBrowserURL(genome, trackName1=['galaxy'], trackName2=['galaxy'], \
                                     track1file=track1file, track2file=track2file, \
                                     analysis='Category pairs differentially co-located?', \
                                     configDict={'Method of counting points': 'Only 1 count per bin (binary)',\
                                                 'Normalize counts': 'Differentially in both directions' if \
                                                 choices[3] == 'Both rows and columns (focusing on column differences)'\
                                                 else 'Differentially for points only',\
                                                 'P-value threshold for significance': '0.01'},\
                                     method='__chrs__')
#
    @staticmethod
    def getToolDescription():
        return '''
In order to create a custom regulome, carry out the following steps:
<ol><li>Use the "Select TFs for regulome" tool to select the transcription
factor matrices you are interested in. Click the "Execute" button.
<li>Use the "Select diseases for regulome" tool to select the diseases you are
interested in. Make sure that you select a dataset that fits with the TF
dataset selected under point 1.
<li>Use the "Create regulome from history" tool (this tool). Select the TF
dataset and the disease dataset created. Select normalization strategy and click
"Execute". You will be redirected to the "Analyze genomic tracks" tool, with the
regulome question preselected, along with some standard arguments. If you want
to change the clustering strategy, or other parameters, please do so. Then click
the "Start analysis" button.
</ol>
The regulome creation process will probably take 10-15 minutes, depending on
dataset size. Note that Google maps versions of the regulome is not yet supported
for custom regulomes.
'''
    
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    #@staticmethod    
    #def getOutputFormat():
    #    return 'html'
    #
    #@staticmethod
    #def validateAndReturnErrors(choices):
    #    '''
    #    Should validate the selected input parameters. If the parameters are not valid,
    #    an error text explaining the problem should be returned. The GUI then shows this
    #    to the user and greys out the execute button. If all parameters are valid, the method
    #    whould return None, which enables the execute button.
    #    '''
    #    return None
