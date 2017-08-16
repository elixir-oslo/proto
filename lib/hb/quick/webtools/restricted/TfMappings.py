from quick.webtools.GeneralGuiTool import GeneralGuiTool
import os
import third_party.safeshelve as safeshelve
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from config.Config import DATA_FILES_PATH
#This is a template prototyping GUI that comes together with a corresponding web page.
#

class TfMappings(GeneralGuiTool):
    MAPPING_SHELVES_PATH = DATA_FILES_PATH + os.sep + 'tfbs'
    
    @staticmethod
    def getToolName():
        return "Assorted functionality for interal use"

    @staticmethod
    def getSubClass(prevChoices):
        if prevChoices is None or len(prevChoices)==0:
            return TfMappings
        elif prevChoices[0]=='TF id mappings':
            return Tool1TfMappings
        
    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"        
        if prevChoices is None or len(prevChoices)==0:
            return ['Functionality', 'test','test2']
        elif prevChoices[0]=='TF id mappings':
            return ['Functionality','Map from','Map to','Mappings to include','Output format of mapping']
        elif prevChoices[0]=='Rename track':
            return ['Functionality', 'Genome','Current track name','New track name']

    @staticmethod    
    def getOptionsBox1():
        "Returns a list of options to be displayed in the first options box"
        #return ['TF id mappings']
        return ['dummy','TF id mappings', 'Rename track']
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        if prevChoices[0]=='TF id mappings':
            return ['Transfac matrix IDs']
        elif prevChoices[0]=='Rename track':
            return '__genome__'
        else:
            return ''
        
    @staticmethod    
    def getOptionsBox3(prevChoices): 
        return ['HGNC gene symbols', 'Transfac TF ids', 'Transfac TF readable names']

    @staticmethod    
    def getOptionsBox4(prevChoices): 
        return ['All matrices (all mappings)']

    @staticmethod    
    def getOptionsBox5(prevChoices): 
        return ['Plain text mapping']
    
    #@staticmethod    
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']

    @staticmethod
    def getDemoSelections():
        return ['TF id mappings', 'Transfac matrix IDs', 'Transfac TF ids', 'All matrices (all mappings)', 'Plain text mapping']
        
    @classmethod
    def testToolUsingDemo(cls):
        cls.execute( cls.getDemoSelections() )
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
        if choices[2]=='Transfac TF ids':
            mappingFn = 'pwm2TFids.shelf'
            mapping = safeshelve.open(Tool1.MAPPING_SHELVES_PATH + os.sep + mappingFn )
        elif choices[2]== 'Transfac TF readable names':
            mappingFn = 'pwm2TFnamesNew.shelf'
            mapping = safeshelve.open(Tool1.MAPPING_SHELVES_PATH + os.sep + mappingFn )
        elif choices[2]== 'HGNC gene symbols':
            mappingFn = 'PWM_to_HGNC.txt'
            mapping = dict([line.strip().split() for line in open(Tool1.MAPPING_SHELVES_PATH + os.sep + mappingFn).readlines()])
        else:
            raise Exception(choices[2])
            
        if galaxyFn==None:
            for key in sorted(mapping.keys()):
                print key + ':' + ','.join(mapping[key]) + os.linesep,
        else:
            mappingStaticFile = GalaxyRunSpecificFile(['mapping.txt'], galaxyFn)
            f = mappingStaticFile.getFile()
            for key in sorted(mapping.keys()):
                if type(mapping[key]) in (list,tuple):
                    mapping[key] = ','.join(mapping[key])
                f.write( key + ':' + mapping[key] + os.linesep )
            f.close()
            print mappingStaticFile.getLink('View/download mapping')
            
            
    @staticmethod
    def isPublic():
        return False
    #
    #@staticmethod
    #def getToolDescription():
    #    return ''
    #    
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
    
#Tool1.testToolUsingDemo()


class Tool1TfMappings(TfMappings):
    
    @staticmethod
    def getToolName():
        return "TF mappings"

    #@staticmethod
    #def getSubClass(prevChoices):
    #    if prevChoices is None or len(prevChoices)==0:
    #        return Tool1
    #    elif prevChoices[0]=='TF id mappings':
    #        return Tool1TfMappings
        
    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"        
        #if prevChoices is None or len(prevChoices)==0:
        #    return ['Functionality', 'test']
        #elif prevChoices[0]=='TF id mappings':
        return ['Functionality','Map from','Map to','Mappings to include','Output format of mapping']
        #elif prevChoices[0]=='Rename track':
        #    return ['Functionality', 'Genome','Current track name','New track name']

    @staticmethod    
    def getOptionsBox1():
        "Returns a list of options to be displayed in the first options box"
        #return ['TF id mappings']
        return ['dummy','TF id mappings', 'Rename track']
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        #if prevChoices[0]=='TF id mappings':
        return ['Transfac matrix IDs']
        #elif prevChoices[0]=='Rename track':
        #    return '__genome__'
        #else:
        #    return ''

    @staticmethod    
    def getOptionsBox3(prevChoices): 
        return {'A':False, 'B':True, 'C':False}

