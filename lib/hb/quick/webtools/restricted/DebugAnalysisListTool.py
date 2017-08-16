from quick.webtools.GeneralGuiTool import GeneralGuiTool
from gold.description.AnalysisList import ANALYSIS_SPECS
from quick.application.ProcTrackOptions import ProcTrackOptions
from quick.application.UserBinSource import UserBinSource

import os
#This is a template prototyping GUI that comes together with a corresponding web page.
#

class DebugAnalysisListTool(GeneralGuiTool):
    STD_PREFIX_TN = ['Sample data', 'Track types']
    NO_TRACK_SHORTNAME = '-- No track --'
    @staticmethod
    def getToolName():
        return "Debug analysis list"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        #can have two syntaxes: either a list of stings or a list of tuples where each tuple has two items(Name of box on webPage, name of getOptionsBox)
        return ['Select analysis list category','Select analysis','Full analysis def','Select genome','Show Track1 simplified','Track1','Show Track2 simplified','Track2','regSpec','binSpec']

    @staticmethod    
    def getOptionsBox1():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return sorted(ANALYSIS_SPECS.keys())
    
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        category = prevChoices[0]
        return sorted(ANALYSIS_SPECS[category])
    
        
    @staticmethod    
    def getOptionsBox3(prevChoices):
        if prevChoices[0] != None:
            line = prevChoices[1].replace('[',os.linesep+'[')
            return line,8,False
            

    @staticmethod    
    def getOptionsBox4(prevChoices):
        return '__genome__'
        
    
    @classmethod    
    def getOptionsBox5(cls, prevChoices): 
        return ['yes', 'no']
        

    @classmethod    
    def getOptionsBox6(cls, prevChoices): 
        #if prevChoices[0]:
        #    cls.updateCacheDict(prevChoices[0])
        
        if prevChoices[4] =='yes' :    
            genome = prevChoices[3]
            prefixTN = cls.STD_PREFIX_TN
            trackList = ProcTrackOptions.getSubtypes(genome, prefixTN, True)
            #if cls._cacheDict.get('track1') in trackList:
            #    trackList.remove(cls._cacheDict.get('track1'))
            #    trackList.insert(0, cls._cacheDict.get('track1'))
            return trackList
        else:
            return '__track__','history'
        
    @classmethod    
    def getOptionsBox7(cls, prevChoices): 
        return ['yes', 'no']
        
    
    @classmethod    
    def getOptionsBox8(cls, prevChoices): 
        if prevChoices[6]=='yes' :
            
            genome = prevChoices[3]
            prefixTN = cls.STD_PREFIX_TN
            trackList = ProcTrackOptions.getSubtypes(genome, prefixTN, True)
            #if cls._cacheDict.get('track2') in trackList:
            #    trackList.remove(cls._cacheDict.get('track2'))
            #    trackList.insert(0, cls._cacheDict.get('track2'))
            return [cls.NO_TRACK_SHORTNAME] + trackList
        else:
            return '__track__','history'
        
    @staticmethod    
    def getOptionsBox9(prevChoices):
        return 'chr1:1-10m'

    @staticmethod    
    def getOptionsBox10(prevChoices):
        return '5m'

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        from gold.application.LogSetup import setupDebugModeAndLogging
        setupDebugModeAndLogging()
        
        analysisDef = choices[2].replace(os.linesep,'')
        #from gold.application.StatRunner import AnalysisDefJob

        print 'Preparing arguments'
        genome = choices[3]
        
        prefixTN1 = cls.STD_PREFIX_TN if choices[4] == 'yes' else []
        tn1 = prefixTN1 + choices[5].split(':') 
        prefixTN2 = cls.STD_PREFIX_TN if choices[6] == 'yes' else []
        tn2 = prefixTN2 + choices[7].split(':')
        if tn2[-1] == cls.NO_TRACK_SHORTNAME:
            tn2 = None
        #from gold.track.GenomeRegion import GenomeRegion
        #region = GenomeRegion(genome, 'chr1',1000,2000)
        #region2 = GenomeRegion(genome, 'chr1',5000,6000)
        
        #kwArgs = {}
        regVal = choices[8]
        binSpecVal = choices[9]
        #ubSource = UserBinSource(regVal, binSpecVal, genome=genome)
        from quick.application.GalaxyInterface import GalaxyInterface
        
        print tn1, tn2
        GalaxyInterface.runManual([tn1, tn2], analysisDef, regVal, binSpecVal, genome, galaxyFn, username=username)
        #ubSource = GalaxyInterface._getUserBinSource(regVal, binSpecVal, genome=genome)
        ##region = list(ubSource)[0]
        #
        #res = AnalysisDefJob(analysisDef, tn1, tn2, ubSource).run()
        #from quick.application.GalaxyInterface import GalaxyInterface
        #GalaxyInterface._viewResults([res],galaxyFn)
        

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
        return [2]
    #
    @staticmethod
    def getToolDescription():
        return '''Tool used to debug a faulty or newly developed statistics.
Calls only a specific entry of AnalysisList and turns on forwarding of exceptions, so that the real error can be found.
If a hidden exception is still expected, it can be revealed by putting the following decorator around a method:
from gold.util.CommonFunctions import repackageException
from gold.util.CustomExceptions import ShouldNotOccurError
@repackageException(Exception, ShouldNotOccurError)        

        '''
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
        '''The format of the history element with the output of the tool.
        Note that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.
        '''
        return 'html'
    #
