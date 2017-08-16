from quick.webtools.GeneralGuiTool import GeneralGuiTool
from gold.statistic.AllStatistics import STAT_CLASS_DICT
from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.application.UserBinSource import UserBinSource
from quick.application.ExternalTrackManager import ExternalTrackManager
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
# This is a template prototyping GUI that comes together with a corresponding
# web page.

class FindSegmentNeighbourhoods(GeneralGuiTool):
    

    
    @staticmethod
    def getToolName():
        return "Find segments with neighbors"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['select genome', 'select source of input', 'Select track', 'Select Treshold to nearest neighbour', 'Select output option', 'Write path to output-file']
    
    
    
    @staticmethod    
    def getOptionsBox1():
        return '__genome__'
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        return ['----- Select -----','track','history']
    
    @staticmethod    
    def getOptionsBox3(prevChoices):
        if prevChoices[-2] == 'track':
            return '__track__'
        elif prevChoices[-2] == 'history':
            return ('__history__', 'bed','bedgraph','gtrack')
    
    @staticmethod    
    def getOptionsBox4(prevChoices):
        return ''
    
    
    
    @staticmethod    
    def getOptionsBox5(prevChoices):
        
        return ['Write to History item', 'Write to Standardised file']
    
    @staticmethod    
    def getOptionsBox6(prevChoices):
        if prevChoices[-2] == 'Write to Standardised file':
            
            return prevChoices[2]
    
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        from gold.origdata.TrackGenomeElementSource import TrackViewListGenomeElementSource
        from gold.origdata.GtrackComposer import StdGtrackComposer
        
        genome = choices[0]
        if choices[1] == 'track':
            trackName = choices[2].split(':')
        else:
            trackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, choices[2].split(':'))
            
        outFn = galaxyFn
        if choices[4] == 'Write to Standardised file':
            outFn = createOrigPath(genome, choices[-1].split(':'), 'collapsed_result.bedgraph')
            ensurePathExists(outFn[:outFn.rfind('/')+1])
               
        threshold = choices[3]
        analysisDef = 'dummy [threshold=%s] -> ForEachSegmentDistToNearestInSameTrackStat' % threshold #'Python'
        res = GalaxyInterface.runManual([trackName], analysisDef, '*', '*', genome, username=username, \
                                        printResults=False, printHtmlWarningMsgs=False)
                
        tvGeSource = TrackViewListGenomeElementSource(genome, [x['Result'] for x in res.values()], trackName)    
        StdGtrackComposer(tvGeSource).composeToFile(outFn)
            
        
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
    