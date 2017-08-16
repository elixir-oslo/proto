from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.application.ProcTrackOptions import ProcTrackOptions
from collections import OrderedDict
from config.Config import DATA_FILES_PATH
import third_party.safeshelve as safeshelve
from quick.extra.StandardizeTrackFiles import FilterOnColumnVal
from gold.util.CommonFunctions import getOrigFns
import os
#This is a template prototyping GUI that comes together with a corresponding web page.
#

class SelectDiseaseTool(GeneralGuiTool):
    GENOME = 'hg18'
    PARENT_TRACK_NAME = ['Genes and gene subsets', 'Gene subsets', 'Regulome diseases']
    DISEASE_PARENT_TO_CHILD_SHELF_FN = os.sep.join([DATA_FILES_PATH, 'disease',\
                                                    'meshParentToAllChildrenMergedOnlyDiseases.shelve'])
    
    @staticmethod
    def getToolName():
        return "Select diseases (from the Medical Subject Headings (MeSH) database) for use in custom regulome. (N.B. Only human hg18 assembly supported)."

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Select dataset of disease-gene relations','Select disease by','Select single diseases',\
                'Select disease categories','Refine selection of single diseases?',\
                'Refine disease selection (N.B. This list is not updated dynamically *)']

    @staticmethod    
    def getOptionsBox1():
        "Returns a list of options to be displayed in the first options box"
        return ['Phenopedia (for use with Bar-Joseph TF binding predictions)', \
                'Phenopedia (for use with UCSC TFBS predictions)',\
                'PubGene (for use with Bar-Joseph TF binding predictions)',\
                'PubGene (for use with UCSC TFBS predictions)']
        
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return ['Single diseases', 'Disease categories']

    @staticmethod
    def _getDiseaseTn(prevChoices):
        parts = prevChoices[0].split('(')
        subtype = [parts[0].strip(), 'All (' + parts[1]]
        return SelectDiseaseTool.PARENT_TRACK_NAME + subtype

    @staticmethod
    def _getAllDiseases(prevChoices):
        if isinstance(prevChoices[2], dict):
            return prevChoices[2].keys()
        else:
            tn = SelectDiseaseTool._getDiseaseTn(prevChoices)
            return [x for x in ProcTrackOptions.getSubtypes(SelectDiseaseTool.GENOME, tn)]
    
    @staticmethod    
    def getOptionsBox3(prevChoices):
        if prevChoices[1] != 'Single diseases':
            return None
        return OrderedDict(sorted([(x, False) for x in SelectDiseaseTool._getAllDiseases(prevChoices)]))

    @staticmethod
    def _getDiseaseCategories(prevChoices):
        allDiseases = [x.split('(')[0] for x in SelectDiseaseTool._getAllDiseases(prevChoices)]
        shelf = safeshelve.open(SelectDiseaseTool.DISEASE_PARENT_TO_CHILD_SHELF_FN, 'r')
        return [cat for cat in shelf.keys() if any([disease in allDiseases \
                                                for disease in shelf[cat]])]
    
    @staticmethod    
    def getOptionsBox4(prevChoices):
        if prevChoices[1] != 'Disease categories':
            return None
        allDiseaseCats = SelectDiseaseTool._getDiseaseCategories(prevChoices)
        return OrderedDict(sorted([(cat, False) for cat in allDiseaseCats]))
                
    @staticmethod    
    def getOptionsBox5(prevChoices):
        if prevChoices[1] != 'Disease categories':
            return None
        return ['Use all', 'Refine']
    
    @staticmethod
    def _getSelectedDiseasesDict(prevChoices):
        if prevChoices[1] != 'Disease categories':
            return None
        
        shelfFn = SelectDiseaseTool.DISEASE_PARENT_TO_CHILD_SHELF_FN
        selectedDict = prevChoices[3]
        mapping = safeshelve.open(shelfFn, 'r')
        selectedDiseases = set(reduce(lambda x, y: x+y,\
                          [[x] + mapping[x] for x in selectedDict if selectedDict[x]], []))
        return OrderedDict(sorted([(x, x.split('(')[0] in selectedDiseases) for x in \
                                    SelectDiseaseTool._getAllDiseases(prevChoices)]))
    
    @staticmethod    
    def getOptionsBox6(prevChoices):
        if prevChoices[4] != 'Refine' or prevChoices[1] != 'Disease categories':
            return None
        return SelectDiseaseTool._getSelectedDiseasesDict(prevChoices)
        
    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history. If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.gtr
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
        if choices[1] == 'Single diseases':
            selectedDiseases = [x for x in choices[2] if choices[2][x]]
        else:
            if choices[4] == 'Refine':
                selectedDiseases = [x for x in choices[5] if choices[5][x]]
            else:
                selectedDiseasesDict = cls._getSelectedDiseasesDict(choices)
                selectedDiseases = sorted([x for x in selectedDiseasesDict.keys() if selectedDiseasesDict[x]])
            
        diseaseTn = cls._getDiseaseTn(choices)
        diseaseFns = getOrigFns(cls.GENOME, diseaseTn, '.category.bed')
        
        open(galaxyFn, 'w') # In order to remove galaxy content
        if len(diseaseFns) > 0:
            for diseaseFn in diseaseFns:
                FilterOnColumnVal.parseFile(diseaseFn, galaxyFn, diseaseTn, cls.GENOME,\
                                            valCol = 3, valType=str, \
                                            valKeepFunc=lambda x:x.replace('_',' ') in selectedDiseases,\
                                            append=True)
        else:
            f = open(galaxyFn, 'w')
            f.write('Error: Did not find the disease input file for track name: %s' % tfTrackName)

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        return None
    
    @staticmethod
    def isPublic():
        return True
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    @staticmethod
    def getToolDescription():
        return '* To update the refined disease selection list, select "Use all" andt then "Refine" under "Refine selection of single diseases".'
    
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
    @staticmethod    
    def getOutputFormat(choices=None):
        return 'category.bed'
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
