import os
from copy import copy
from gold.util.CommonFunctions import parseShortenedSizeSpec
from gold.origdata.BedGenomeElementSource import BedGenomeElementSource
from gold.origdata.BedComposer import BedComposer
from gold.origdata.GESourceWrapper import ListGESourceWrapper
from quick.application.AutoBinner import AutoBinner
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.webtools.GeneralGuiTool import GeneralGuiTool

#This is a template prototyping GUI that comes together with a corresponding web page.
#

class SplitSegmentsTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Split BED segments into subsegments of equal size"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Segment track from history','Bin size in bps (k and m denoting thousand and million bps, respectively)']

    @staticmethod    
    def getOptionsBox1():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return '__history__', 'bed', 'category.bed', 'valued.bed'
    
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return '100k'
    
        
    #@staticmethod    
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
    
    @staticmethod
    def splitGEs(geSource, binSize):
        for ge in geSource:
            geBins = AutoBinner([ge], int(binSize))
            for bin in geBins:
                geCopy = ge.getCopy()
                geCopy.start = bin.start
                geCopy.end = bin.end
                yield geCopy

    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
        binSize = parseShortenedSizeSpec(choices[1])
        geSource = BedGenomeElementSource(ExternalTrackManager.extractFnFromGalaxyTN(choices[0].split(':')))
        splittedGeSource = ListGESourceWrapper(geSource, list(SplitSegmentsTool.splitGEs(geSource, binSize)))
        BedComposer(splittedGeSource).composeToFile(galaxyFn)
        
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        errorMsg = SplitSegmentsTool._checkTrack(choices, trackChoiceIndex=0, genomeChoiceIndex=None, filetype='BED')
        if errorMsg:
            return errorMsg
        
        try:
            parseShortenedSizeSpec(choices[1])
        except:
            return 'Bin size is not in correct format: %s' % choices[1]
        
    @staticmethod
    def isPublic():
        return True
    
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
    @staticmethod
    def getToolDescription():
        return '''
This tool splits the regions of a BED file into sub-regions of the same size, if
possible. Regions that are smaller than the specified size are returned as they
are. The same applies to the last sub-region of a large region if it is not
exactly the specified size. A BED file with the sub-regions are returned.'''
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
        if choices[0]:
            inputFormat = ExternalTrackManager.extractFileSuffixFromGalaxyTN(choices[0].split(':'))
            return inputFormat
    
