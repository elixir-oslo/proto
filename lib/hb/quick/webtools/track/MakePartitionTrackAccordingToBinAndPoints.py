from quick.webtools.GeneralGuiTool import GeneralGuiTool
from gold.statistic.AllStatistics import STAT_CLASS_DICT
from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.application.UserBinSource import UserBinSource

from quick.extra.TrackExtractor import TrackExtractor
import time
from quick.application.GalaxyInterface import GalaxyInterface
from gold.application.StatRunner import *
from gold.util.CustomExceptions import InvalidFormatError
from quick.util.GenomeInfo import GenomeInfo
from gold.origdata.GenomeElementSource import GenomeElementSource
from gold.origdata.GenomeElementSorter import GenomeElementSorter
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.util.Wrappers import GenomeElementTvWrapper
from gold.track.Track import PlainTrack
from gold.track.GenomeRegion import GenomeRegion
from gold.origdata.BedGenomeElementSource import BedGenomeElementSource
from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource

class MakePartitionTrackAccordingToBinAndPoints(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Make partition track according to bin and points"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['select genome', 'Choose source of points data', 'select track', 'select Binning' ]
    
    
    
    @staticmethod    
    def getOptionsBox1():
        return '__genome__'
    
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return ['--select--','history','track']
    
    @staticmethod    
    def getOptionsBox3(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        if prevChoices[1] == 'history':
            return ('__history__','gtrack','bed','valued.bed', 'wig')
        elif prevChoices[1] == 'track':
            return '__track__'
            
    
    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    '''Returns a list of options to be displayed in the first options box
    #    Alternatively, the following have special meaning:
    #    '__genome__'
    #    '__track__'
    #    ('__history__','bed','wig','...')
    #    '''
    #    return ['--select--','history','Track']
    
    @staticmethod    
    def getOptionsBox4(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return ('__history__','gtrack','bed','valued.bed', 'wig')
    
    #@staticmethod    
    #def getOptionsBox5(prevChoices): 
    #    '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
    #    prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
    #    '''
    #    return prevChoices[2],1,True
            
    
    @classmethod   
    def PrintResultToHistItem(cls, outFn, geSource, preProcTN1, genome, username):
        analysisDef = 'dummy ->SplitToCorrespondingSubBinsBasedOnBreakpointsStat'
        #outFile = open(outFn,'w')
        with open(outFn,'w') as outFile:
            print>>outFile, '##track type: valued segments\n###seqid\tstart\tend\tvalue\tstrand'
            for ge in geSource:
                regSpec = '%s:%i-%i' %(ge.chr, ge.start+1, ge.end) #+1 since assumed 1-indexed, end-inclusive
    
                #userBinSource, fullRunArgs = GalaxyInterface._prepareRun(preProcTN1, None, analysisDef, regSpec, '*', genome)
                #res = AnalysisDefJob(analysisDef, preProcTN1, None, userBinSource, **fullRunArgs).run(printProgress=False)
                #trackName
                res = GalaxyInterface.runManual([preProcTN1], analysisDef, regSpec, '*', genome, username=username, \
                                                printResults=False, printProgress=False, printHtmlWarningMsgs=False)
    
                for region,resDict in res.items():
                    print>>outFile, resDict['Result']
                    #tv = resDict['Result']
                    #TrackExtractor._extract(tv, ':'.join(preProcTN1).replace(' ','_'), region, outFn, append=True, globalCoords=True, addSuffix=False)
                
            
        
        #open(outFn,'a').write('FINITO! ')        
            
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        from quick.application.ExternalTrackManager import ExternalTrackManager
        
        genome = choices[0]
        preProcTN1 = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, choices[2].split(':')) if choices[1] == 'history' else choices[2].split(':')
        chrSizeDict =  dict([ ( chrom, GenomeInfo.getChrLen(genome, chrom)) for chrom in GenomeInfo.getChrList(genome)])
        
        
        trackType = choices[3].split(':')[1]
        fnSource = ExternalTrackManager.extractFnFromGalaxyTN(choices[3].split(':'))
        
        if trackType in ['valued.bed', 'category.bed', 'bed']:
            geSource = GenomeElementSorter(BedGenomeElementSource(fnSource, genome=genome)).__iter__()
            
        elif trackType == 'gtrack':
            geSource = GenomeElementSorter(GtrackGenomeElementSource(fnSource, genome=genome)).__iter__()
            #headLinesStr = geSource.getHeaderLines().replace('##','\n##')
        else:
            raise InvalidFormatError('The Binning must be of the following formats: gtrack, valued.bed, category.bed ,bed ...')
            
            
        cls.PrintResultToHistItem( galaxyFn, geSource, preProcTN1, genome, username)
        

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
    #    return []
    #
    #@staticmethod
    #def getToolDescription():
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #@staticmethod
    #def isBatchTool():
    #    return False
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
    #
    @staticmethod    
    def getOutputFormat(choices):
        return 'gtrack'#
