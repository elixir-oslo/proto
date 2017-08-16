from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.extra.RenameTrack import renameTrack
from quick.application.GalaxyInterface import GalaxyInterface
from os.path import isdir
from gold.util.CommonFunctions import createDirPath

#This is a template prototyping GUI that comes together with a corresponding web page.
#

class RenameTrackTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Rename track"

    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Genome','Current track name','New track name', 'Select extra genomes for renaming']

    @staticmethod    
    def getOptionsBox1():
        "Returns a list of options to be displayed in the first options box"
        return '__genome__'
    
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return '__track__'

    @staticmethod    
    def getOptionsBox3(prevChoices): 
        return prevChoices[1]
    
    @staticmethod    
    def getOptionsBox4(prevChoices):
        
        return '__genomes__' #dict([(v[0],False) for v in GalaxyInterface.getAllGenomes()])


    #@staticmethod
    #def getDemoSelections():
    #    return ['hg18','Trashcan:SICER islands:H3K27me3','Trashcan:SICER islands:H3K27me3']
    #
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
        genomesList = []
        for v in GalaxyInterface.getAllGenomes(username):
            if choices[3].get(v[0]):
                if choices[3][v[0]] and isdir(createDirPath(choices[1].split(':'),v[1])):
                    genomesList.append(v[1])
        #genomesList = [v[1] for v in GalaxyInterface.getAllGenomes(username) if choices[3][v[0]] and isdir(createDirPath(choices[1].split(':'),v[1]))]

        #print 'Executing...'
        genomes = [choices[0]] + genomesList
        oldTn = choices[1]
        newTn = choices[2]
        for genome in genomes:
            renameTrack(genome, oldTn.split(':'), newTn.split(':'))
            print '%s renamed to %s in genome %s.' % (oldTn, newTn, genome)
    
    
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        if choices[1] == '':
            return ''
        
    @staticmethod
    def isPublic():
        return False
    
    @staticmethod
    def getToolDescription():
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.paragraph('This tool is used to rename or move a track.')
        core.divider()
        core.highlight('Current track name')
        core.paragraph('Select the track to rename. It is allowed to select a parent track or category.')
        core.divider()
        core.highlight('New track name')
        core.paragraph("Type in the new track name. Track names are separated by ':', e.g. 'Trashcan:SICER islands:H3K27me3'.")
        return str(core)
        
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
    
    @staticmethod
    def getResetBoxes():
        return [1,2]
