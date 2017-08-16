

from quick.webtools.GeneralGuiTool import GeneralGuiTool
from gold.statistic.AllStatistics import STAT_CLASS_DICT
from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.application.UserBinSource import UserBinSource
#from gold.application.StatRunner import StatJob        
from os import sep, makedirs
from gold.util.CommonFunctions import createOrigPath
from quick.util.CommonFunctions import ensurePathExists
from quick.util.GenomeInfo import GenomeInfo
import time
from config.Config import NONSTANDARD_DATA_PATH
from quick.application.GalaxyInterface import GalaxyInterface
from gold.application.StatRunner import *
#This is a template prototyping GUI that comes together with a corresponding web page.
#

class CollapseOverlappingCategorySegments(GeneralGuiTool):
    
    
    @staticmethod
    def getToolName():
        return "Collapse overlapping category segments to track"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['select genome', 'select track', 'Select Computing method', 'Select Category(value)', 'Select number of samples', 'Select output option', 'Write path to output-file']
    
    
    
    @staticmethod    
    def getOptionsBox1():
        return '__genome__'
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        return '__track__'
    
    @staticmethod    
    def getOptionsBox3(prevChoices):
        return ['mostCommonCat', 'freqOfCat', ]
    
    @staticmethod    
    def getOptionsBox4(prevChoices):
        if prevChoices[2] == 'mostCommonCat':
            return None
        return ''
    
    @staticmethod    
    def getOptionsBox5(prevChoices):
        if prevChoices[2] == 'mostCommonCat':
            return None
        return ''
    
    @staticmethod    
    def getOptionsBox6(prevChoices):
        
        return ['Write to History item', 'Write to Standardised file']
    
    @staticmethod    
    def getOptionsBox7(prevChoices):
        if prevChoices[-2] == 'Write to Standardised file':
            
            return prevChoices[1]
    
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        
        start = time.time()
        genome = choices[0]
        trackName = choices[1].split(':')
        outFn = galaxyFn
        if choices[5] == 'Write to Standardised file':
            outFn = createOrigPath(genome, choices[-1].split(':'), 'collapsed_result.bedgraph')
            ensurePathExists(outFn[:outFn.rfind('/')+1])
                
        combineMethod = choices[2]
        category = choices[3] if choices[3] else ''
        numSamples = choices[4] if choices[4] else '1'
        
        analysisDef = 'dummy [combineMethod=%s] %s [numSamples=%s] -> ConvertToNonOverlappingCategorySegmentsPythonStat' % \
                        (combineMethod, '[category=%s]' % category if category != '' else '', numSamples) #'Python'
                                                  
        for regSpec in  GenomeInfo.getChrList(genome):
            res = GalaxyInterface.runManual([trackName], analysisDef, regSpec, '*', genome, username=username, \
                                            printResults=False, printHtmlWarningMsgs=False)
            
            from gold.origdata.TrackGenomeElementSource import TrackViewGenomeElementSource
            from gold.origdata.BedComposer import CategoryBedComposer
            for resDict in res.values():
                trackView = resDict['Result']
                tvGeSource = TrackViewGenomeElementSource(genome, trackView, trackName)
                CategoryBedComposer(tvGeSource).composeToFile(outFn)
        
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        return None
    
    #@staticmethod
    #def isPublic():
    #    return False
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
    @staticmethod
    def getResetBoxes():
        return [1]
    
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
    #
    @staticmethod    
    def getOutputFormat(choices):
        return 'bedgraph'
    