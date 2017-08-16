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

class SelectTfTool(GeneralGuiTool):
    GENOME = 'hg18'
    PARENT_TRACK_NAME = ['Gene regulation', 'Transcription factor regulation']
    TRACK_DICT = {'Bar-Joseph predictions': PARENT_TRACK_NAME + ['Gene target predictions', 'Ernst et al (2010)'],
                  'UCSC prediction track': PARENT_TRACK_NAME + ['TFBS predictions', 'UCSC conserved sites']}
    TF_NAMES_TO_PWM_SHELF_FN = os.sep.join([DATA_FILES_PATH, 'tfbs', 'tfNames2pwmNames.shelf'])
    TF_CLASSES_TO_PWM_SHELF_FN = os.sep.join([DATA_FILES_PATH, 'tfbs', 'tfClasses2pwmNames.shelf'])
    
    @staticmethod
    def getToolName():
        return "Select transcription factors (TF) for use in custom regulome. (N.B. Only human hg18 assembly supported)."

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Select TF binding dataset','Select TF by','Select PWMs',\
                'Select TF names','Select TF classes','Refine selection of PWMs?',\
                'Refine PWM selection (N.B. This list is not updated dynamically *)']

    @staticmethod    
    def getOptionsBox1():
        "Returns a list of options to be displayed in the first options box"
        return ['Bar-Joseph predictions', 'UCSC prediction track']
        
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return ['Position Weight Matrix (PWM) id', 'TF name', 'TF class']

    @staticmethod
    def _getAllPwms(prevChoices):
        if isinstance(prevChoices[2], dict):
            return prevChoices[2].keys()
        else:
            tfTrackName = SelectTfTool.TRACK_DICT[prevChoices[0]]
            return [pwm for pwm in ProcTrackOptions.getSubtypes(SelectTfTool.GENOME, tfTrackName)]

    @staticmethod    
    def getOptionsBox3(prevChoices):
        if prevChoices[1] != 'Position Weight Matrix (PWM) id':
            return None
        return OrderedDict(sorted([(pwm, False) for pwm in SelectTfTool._getAllPwms(prevChoices)]))

    @staticmethod
    def _getFilteredSelections(prevChoices, shelfFn):
        allPwms = SelectTfTool._getAllPwms(prevChoices)
        shelf = safeshelve.open(shelfFn, 'r')
        return [x for x in shelf.keys() if any([pwm.upper() in allPwms for pwm in shelf[x]])]
    
    @staticmethod    
    def getOptionsBox4(prevChoices):
        if prevChoices[1] != 'TF name':
            return None
        allTfs = SelectTfTool._getFilteredSelections(prevChoices, SelectTfTool.TF_NAMES_TO_PWM_SHELF_FN)
        return OrderedDict(sorted([(tf, False) for tf in allTfs]))
        
    @staticmethod    
    def getOptionsBox5(prevChoices):
        if prevChoices[1] != 'TF class':
            return None
        allTfs = SelectTfTool._getFilteredSelections(prevChoices, SelectTfTool.TF_CLASSES_TO_PWM_SHELF_FN)
        return OrderedDict(sorted([(tf, False) for tf in allTfs]))
                
    @staticmethod    
    def getOptionsBox6(prevChoices):
        if prevChoices[1] not in ['TF name','TF class']:
            return None
        return ['Use all', 'Refine']
    
    @staticmethod
    def _getSelectedPwmsSet(prevChoices):
        if prevChoices[1] == 'TF name':
            shelfFn = SelectTfTool.TF_NAMES_TO_PWM_SHELF_FN
            selectedDict = prevChoices[3]
        elif prevChoices[1] == 'TF class':
            shelfFn = SelectTfTool.TF_CLASSES_TO_PWM_SHELF_FN
            selectedDict = prevChoices[4]
        else:
            return None
        mapping = safeshelve.open(shelfFn)
        pwms = reduce(lambda x, y: x+y,\
                          [mapping[x] for x in selectedDict if selectedDict[x]], [])
        return set([pwm.upper() for pwm in pwms])
    
    @staticmethod    
    def getOptionsBox7(prevChoices):
        if prevChoices[5] != 'Refine' or prevChoices[1] not in ['TF name','TF class']:
            return None
        selectedPwms = SelectTfTool._getSelectedPwmsSet(prevChoices)
        return OrderedDict(sorted([(pwm, pwm in selectedPwms) for pwm in \
                                    SelectTfTool._getAllPwms(prevChoices)]))

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
        
        if choices[1] == 'Position Weight Matrix (PWM) id':
            selectedPwms = [x for x in choices[2] if choices[2][x]]
        else:
            if choices[5] == 'Refine':
                selectedPwms = [x for x in choices[6] if choices[6][x]]
            else:
                selectedPwms = sorted([x for x in cls._getSelectedPwmsSet(choices)])
            
        tfTrackName = cls.TRACK_DICT[choices[0]]
        tfFns = getOrigFns(cls.GENOME, tfTrackName, '.category.bed')
        
        open(galaxyFn, 'w') # In order to remove galaxy content
        if len(tfFns) > 0:
            for tfFn in tfFns:
                FilterOnColumnVal.parseFile(tfFn, galaxyFn, tfTrackName, cls.GENOME,\
                                            valCol = 3, valType=str, \
                                            valKeepFunc=lambda x:x in selectedPwms, append=True)
        else:
            f = open(galaxyFn, 'w')
            f.write('Error: Did not find the TF input file for track name: %s' % tfTrackName)

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
        return '* To update the refined pwm selection list, select "Use all" andt then "Refine" under "Refine selection of PWMs".'
    
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
