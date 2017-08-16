from quick.webtools.GeneralGuiTool import GeneralGuiTool
from gold.statistic.AllStatistics import STAT_CLASS_DICT
from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.application.UserBinSource import UserBinSource
#from gold.application.StatRunner import StatJob        
from os import sep
from quick.util.GenomeInfo import GenomeInfo
import time
from config.Config import NONSTANDARD_DATA_PATH
from quick.application.GalaxyInterface import GalaxyInterface
from gold.application.StatRunner import *
#This is a template prototyping GUI that comes together with a corresponding web page.
#

class Tool1(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Multiply number"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['select genome', 'select track']
    
    @staticmethod    
    def getOptionsBox1():
        return '__genome__'
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        return '__track__'
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        start = time.time()
        genome = choices[0]
        trackName = choices[1].split(':')
        #outFn = open(NONSTANDARD_DATA_PATH+'/hg19/Private/Sigven/resultat.bed','w')
        analysisDef = '-> ConvertToNonOverlappingCategorySegmentsPythonStat' #'Python'
        for regSpec in  GenomeInfo.getChrList(genome):
            res = GalaxyInterface.runManual([trackName], analysisDef, regSpec, '*', genome, username=username, \
                                            printResults=False, printHtmlWarningMsgs=False)

            from gold.origdata.TrackGenomeElementSource import TrackViewGenomeElementSource
            from gold.origdata.BedComposer import CategoryBedComposer
            for resDict in res.values():
                tvGeSource = TrackViewGenomeElementSource(genome, resDict['Result'], trackName)
                CategoryBedComposer(tvGeSource).composeToFile(outFn)
                
        #print 'run with Stat=%s, took(secs): ' % analysisDef, time.time()-start
        
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
    #@staticmethod
    #def getResetBoxes():
    #    return [1]
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
    #
    @staticmethod    
    def getOutputFormat(choices):
        return 'bed'
    
class SubTool1(Tool1):
    pass
