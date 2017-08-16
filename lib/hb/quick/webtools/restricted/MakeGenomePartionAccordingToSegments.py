from quick.webtools.GeneralGuiTool import GeneralGuiTool
from gold.origdata.GenomeElementSource import GenomeElementSource
from gold.origdata.GenomeElementSorter import GenomeElementSorter
from quick.application.ExternalTrackManager import ExternalTrackManager
from gold.util.CommonFunctions import createCollectedPath
from quick.util.Wrappers import GenomeElementTvWrapper
from gold.track.Track import PlainTrack
from gold.track.GenomeRegion import GenomeRegion
from gold.origdata.BedGenomeElementSource import BedGenomeElementSource #, BedCategoryGenomeElementSource, BedValuedGenomeElementSource
from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
from gold.util.RandomUtil import random
from quick.util.GenomeInfo import GenomeInfo
import numpy
import os
import time
#This is a template prototyping GUI that comes together with a corresponding web page.
#

class MakeGenomePartionAccordingToSegments(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Expand BED segments to cover whole genome"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        #can have two syntaxes: either a list of stings or a list of tuples where each tuple has two items(Name of box on webPage, name of getOptionsBox)
        return ['select genome','select Input source','choose history item', 'choose track']

    @staticmethod    
    def getOptionsBox1():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return '__genome__'
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return ['history','track']
    
    @staticmethod    
    def getOptionsBox3(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        if prevChoices[1] == 'history':
            return ('__history__','bed','valued.bed', 'category.bed' )#'gtrack'
            
    
        
    @staticmethod    
    def getOptionsBox4(prevChoices):
        if prevChoices[1] == 'track':
            return '__track__'
    
    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
    
    @classmethod
    def makeExtraColumnsStr(cls, extraColumns, genomeElem):
        extraVals = []
        for property, dType in extraColumns:
            value = getattr(genomeElem, property)
            
                    
            if property == 'edges':
                extraVals.append(';'.join(value))
                    
            elif property == 'weights':
                ids = extraVals[-1].split(';')
                extraVals[-1] = ';'.join([ ids[index]+'='+str(x) for index, x in enumerate(value) ])
            elif dType == bool:
                if property == 'strand':
                    extraVals.append('+' if value else '-')
                else:
                    extraVals.append('1' if value else '0')
                    
            elif dType == list:
                extraVals.append(','.join(value))
            
            else:
                extraVals.append(str(value))
        return extraVals
    @classmethod
    def findValueType(cls, value):
        if type(value).__name__ in ['string_', 'str']:
            if len(value)>1:
                return 'category'
            return 'character'
        
        elif type(value).__name__ in ['bool_', 'bool']:
            return 'binary'
        else:
            return 'number'
  
    @classmethod 
    def WriteExpandedElementsToFile(cls, geSource, chrSizeDict, outputFile, headLinesStr, writeHeaderFlag=False):
        prevGe = geSource.next()
        extraColumns = [(property, type(getattr(prevGe, property))) for property in ['val', 'strand', 'id', 'edges', 'weights'] if getattr(prevGe, property) is not None]
        
        if writeHeaderFlag:
            if not headLinesStr:
                extraColumnNames = [v[0] for v in extraColumns]
                headLinesStr ='##track type: '+('linked ' if 'edge' in extraColumnNames else '')+('valued ' if 'val' in extraColumnNames else '')+'segments'+'\n'
                if headLinesStr.find('valued')>=0:
                    headLinesStr+='##value type: '+ cls.findValueType(prevGe.val) + '\n'
                headLinesStr+='###'+'\t'.join(['seqid', 'start', 'end']+extraColumnNames).replace('\tval', '\tvalue')
            else:
                headLinesStr+='\n'+geSource.getColSpecLine()
            print>>outputFile, headLinesStr
            #print>>outputFile, extraColumns, cls.makeExtraColumnsStr(extraColumns, prevGe), type(prevGe.val).__name__
        
        chrom, start, end, vals = prevGe.chr, min(0, prevGe.start), prevGe.end, cls.makeExtraColumnsStr(extraColumns, prevGe)
        try:
            while True:
            
                ge = geSource.next()
                border = 0
                if ge.chr == chrom:
                    border = int((end+ge.start)/2)
                    print>>outputFile, '\t'.join([chrom, str(start), str(border)] + vals) 
                else:
                    print>>outputFile, '\t'.join([chrom, str(start), str(chrSizeDict[chrom])  ] + vals) 
                chrom, start, end, vals = ge.chr, border, ge.end, cls.makeExtraColumnsStr(extraColumns, ge)
        except StopIteration:
            print>>outputFile, '\t'.join([chrom, str(start), str(chrSizeDict[chrom]) ] + vals)        
        
    @classmethod   
    def execute(cls, choices, galaxyFn=None, username=''):
        
        outputFile =  open(galaxyFn, 'w')
        genome = choices[0]
        histItem = choices[2]
        trackItem = choices[3]
        chromRegsPath = GenomeInfo.getChrRegsFn(genome)
        
        chrSizeDict =  dict([ ( chrom, GenomeInfo.getChrLen(genome, chrom)) for chrom in GenomeInfo.getChrList(genome)])
        geSource = headLinesStr = None
        if choices[1] == 'history':
            
            trackType = choices[2].split(':')[1]
            username = ''.join([chr(random.randint(97,122)) for i in range(6)]) 
            tempFn = createCollectedPath(genome, [], username+'_'.join([str(v) for v in time.localtime()[:6]])+'.'+trackType)
            fnSource = ExternalTrackManager.extractFnFromGalaxyTN(choices[2].split(':'))
            open(tempFn,'w').write(open(fnSource,'r').read())
            
            
            if trackType in ['valued.bed', 'category.bed', 'bed']:
                geSource = GenomeElementSorter(BedGenomeElementSource(tempFn, genome=genome)).__iter__()
            
            #elif trackType == 'gtrack':
            #    geSource = GenomeElementSorter(GtrackGenomeElementSource(tempFn, genome=genome)).__iter__()
            #    headLinesStr = geSource.getHeaderLines().replace('##','\n##')
            
            cls.WriteExpandedElementsToFile(geSource, chrSizeDict, outputFile, headLinesStr, writeHeaderFlag=True)
            os.remove(tempFn)
        
        else:
            writeHeaderFlag = True
            for chrom in GenomeInfo.getChrList(genome):
                gRegion = GenomeRegion(genome, chrom, 0, chrSizeDict[chrom])
                plTrack = PlainTrack(trackItem.split(':'))
                geSource = GenomeElementTvWrapper(plTrack.getTrackView(gRegion)).__iter__()
                cls.WriteExpandedElementsToFile(geSource, chrSizeDict, outputFile, headLinesStr, writeHeaderFlag)
                writeHeaderFlag = False    
        outputFile.close()
        
    
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
        return 'gtrack'
    #
