from quick.webtools.GeneralGuiTool import GeneralGuiTool
import shelve
import os
import re
import glob
from quick.application.ExternalTrackManager import ExternalTrackManager
from collections import Counter, defaultdict, OrderedDict
from gold.track.GenomeRegion import GenomeRegion
from quick.util.GenomeInfo import GenomeInfo
from gold.track.Track import PlainTrack
from quick.util.CommonFunctions import changedWorkingDir
from config.Config import PROCESSED_DATA_PATH, DATA_FILES_PATH
from quick.application.ProcTrackOptions import ProcTrackOptions
import numpy as np
from gold.util.CommonFunctions import createOrigPath
from shutil import copytree
import urllib2
# This is a template prototyping GUI that comes together with a corresponding
# web page.

class CalculateWeekdayProfits(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Calculate weekday profits "

    @staticmethod
    def getInputBoxNames():
        
        return ['select genome', 'Select stocks', 'select day'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None
    
    @staticmethod    
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey()
        
        return '__genome__'
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        stockDict = None
        with changedWorkingDir('/usit/invitro/hyperbrowser/standardizedTracks/days/Company stocks/Historical prices/OSE/'):
            stockDict = OrderedDict([(v, False) for v in glob.glob('*')])
        return stockDict
    
    @staticmethod    
    def getOptionsBox3(prevChoices): # Alternatively: getOptionsBoxKey()
        
        return '__track__'
    
    
    
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        from quick.application.ProcTrackOptions import ProcTrackOptions
        
        from quick.application.GalaxyInterface import GalaxyInterface
        import gold.application.StatRunner
        
        analysisDef = 'dummy -> PercentageChangeStat'
        genome = choices[0]
        binSpec = '*'
        regSpec = 'Days_1900_2036:36890-41424'
        tnRoot = 'Company stocks:Historical prices:OSE:'
        stockList = [k for k, v in choices[1].items() if v]
        
        
        numStocks = 0
        totalPercent = 0.0
        for stock in stockList:
            tn = tnRoot + stock
            if ProcTrackOptions.isValidTrack(genome, tn.split(':'), fullAccess=True):
                resultDict = GalaxyInterface.runManual([tn.split(':'), choices[2].split(':')], analysisDef, regSpec, binSpec, 'days', galaxyFn, printResults=False, printProgress=False)
            
                for k, v in resultDict.items():
                    print 'increase (from jan. 2001 - jun. 2013) for ', stock, ':  ', v
                    res = v['Result']
                    if res == 0.0 or res>10000:
                        continue
                    totalPercent+= v['Result']
                    numStocks += 1
            else:
                print 'this is not a valid track', tn
        print 'Average increase (from jan. 2001 - jun. 2013):  ', totalPercent/numStocks, ' (number of stocks =', numStocks, ')'
        
        
        
        
        #if choices[3] == 'from history':
        #    regSpec = ExternalTrackManager.extractFileSuffixFromGalaxyTN(choices[4].split(':'))
        #    binSpec = ExternalTrackManager.extractFnFromGalaxyTN(choices[4].split(':'))
        #numBins = open(binSpec).read().count('\n')
        #if numBins>330000:
        #    gold.application.StatRunner.MAX_NUM_USER_BINS = numBins
        #    
        #
        #percent = float(choices[5]) if float(choices[5])<=1.0 else float(choices[5])/100.0
        #GalaxyInterface.ALLOW_OVERLAPPING_USER_BINS = True
        #resultDict = GalaxyInterface.runManual([tn1], analysisDef, regSpec, binSpec, genome, galaxyFn, printResults=False, printProgress=True)
        #overlapRegions = [k for k, v in resultDict.items() if v['Result']>=percent]
        #with open(galaxyFn,'w') as utfil:
        #    for i in overlapRegions:
        #        print>>utfil, '\t'.join([i.chr, str(i.start), str(i.end)])




    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True
    #
    #@staticmethod
    #def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    #@staticmethod
    #def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    #@staticmethod
    #def getFullExampleURL():
    #    return None
    #
    #@classmethod
    #def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    #@staticmethod    
    #def getOutputFormat(choices):
    #    '''
    #    The format of the history element with the output of the tool. Note
    #    that html output shows print statements, but that text-based output
    #    (e.g. bed) only shows text written to the galaxyFn file.In the latter
    #    case, all all print statements are redirected to the info field of the
    #    history item box.
    #    '''
    #    return 'html'
