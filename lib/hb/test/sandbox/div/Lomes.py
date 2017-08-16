#This is a template prototyping GUI that comes together with a corresponding web page.
#

class HbPrototypeGui(object):
    @staticmethod
    def getToolName():
        return "Lomes"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['box1','box2','3','4','5']
    
    @staticmethod
    def getOptionsBox1():
        "Returns a list of options to be displayed in the first options box"
        return ['Transcriptional regulome','miRNA regulome','Methylome', 'Repeatolome']
    
    @staticmethod
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        if prevChoices[0]=='Transcriptional regulome':
            return ['Disease transcriptional regulome', 'Chromosomal transcriptional regulome', '...']
        else:
            return ['']
    
    @staticmethod
    def getOptionsBox3(prevChoices):
        return ['All diseases', 'Neoplasms']

    @staticmethod
    def getOptionsBox4(prevChoices):
        return ['Normalized against average among (diseases/..)','Normalized by assuming similar proportions..']

    @staticmethod
    def getOptionsBox5(prevChoices):
        return ['Average manhatten distance','Average euklidian distance']
        
    @staticmethod
    def execute(choices):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        print 'Executing...'
    
    
