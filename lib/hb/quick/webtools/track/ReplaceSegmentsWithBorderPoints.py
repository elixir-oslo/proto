import os

from gold.origdata.BedGenomeElementSource import BedGenomeElementSource #, BedCategoryGenomeElementSource, BedValuedGenomeElementSource
from gold.origdata.GenomeElementSorter import GenomeElementSorter
from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
from gold.track.GenomeRegion import GenomeRegion
from gold.track.Track import PlainTrack
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.util.GenomeInfo import GenomeInfo
from quick.util.Wrappers import GenomeElementTvWrapper
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class ReplaceSegmentsWithBorderPoints(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Replace segments with border points"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        #can have two syntaxes: either a list of stings or a list of tuples where each tuple has two items(Name of box on webPage, name of getOptionsBox)
        return ['select genome','select Input source','choose history item', 'choose track', 'Hist Input']

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
        return ['--select--','history','track']
    
    @staticmethod    
    def getOptionsBox3(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        if prevChoices[1] == 'history':
            return ('__history__','gtrack','bed','valued.bed', 'category.bed', 'wig')
            
    
        
    @staticmethod    
    def getOptionsBox4(prevChoices):
        if prevChoices[1] == 'track':
            return '__track__'
    

    @staticmethod    
    def getOptionsBox5(prevChoices):
        if prevChoices[1] == 'history':
            return (prevChoices[2], 2, True)
        elif prevChoices[1] == 'track':
            return (prevChoices[3], 2, True)
        return (GenomeInfo.getChrRegsFn(prevChoices[0]),  2, True)
    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
        
    #@staticmethod    
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']

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
        ge = geSource.next()
        extraColumns = [(property, type(getattr(ge, property))) for property in ['val', 'strand', 'id', 'edges', 'weights'] if getattr(ge, property) is not None]
        
        if writeHeaderFlag:
            if not headLinesStr:
                extraColumnNames = [v[0] for v in extraColumns]
                headLinesStr ='##track type: '+('linked ' if 'edge' in extraColumnNames else '')+('valued ' if 'val' in extraColumnNames else '')+'points'+'\n'
                if headLinesStr.find('valued')>=0:
                    headLinesStr+='##value type: '+ cls.findValueType(ge.val) + '\n'
                headLinesStr+='###'+'\t'.join(['seqid', 'start']+extraColumnNames).replace('\tval', '\tvalue')
            else:
                headLinesStr+='\n'+geSource.getColSpecLine()
            print>>outputFile, headLinesStr
            #print>>outputFile, extraColumns, cls.makeExtraColumnsStr(extraColumns, prevGe), type(prevGe.val).__name__
        
        vals = cls.makeExtraColumnsStr(extraColumns, ge)
        print>>outputFile, '\n'.join(['\t'.join([ge.chr, str(ge.start)] + vals), '\t'.join([ge.chr, str(ge.end-1)] + vals) ])

        
        while True:
            try:
                ge = geSource.next()
                vals = cls.makeExtraColumnsStr(extraColumns, ge)
                print>>outputFile, '\n'.join(['\t'.join([ge.chr, str(ge.start)] + vals), '\t'.join([ge.chr, str(ge.end-1)] + vals) ])
            except StopIteration:
                break    
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):

        outputFile =  open(galaxyFn, 'w')
        genome = choices[0]
        histItem = choices[2]
        trackItem = choices[3]
        chromRegsPath = GenomeInfo.getChrRegsFn(genome)
        
        chrSizeDict =  dict([ ( chr, GenomeInfo.getChrLen(genome, chr)) for chr in GenomeInfo.getChrList(genome)])
        geSource = headLinesStr = None
        if choices[1] == 'history':
            
            trackType = choices[2].split(':')[1]
            
            from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
            tempFn  = GalaxyRunSpecificFile(['fromHistory.'+trackType],galaxyFn).getDiskPath(True)
            
            fnSource = ExternalTrackManager.extractFnFromGalaxyTN(choices[2].split(':'))
            open(tempFn,'w').write(open(fnSource,'r').read())
        
            if trackType in ['valued.bed', 'category.bed', 'bed']:
                geSource = GenomeElementSorter(BedGenomeElementSource(tempFn, genome=genome)).__iter__()
            
            elif trackType == 'gtrack':
                geSource = GenomeElementSorter(GtrackGenomeElementSource(tempFn, genome=genome)).__iter__()
                headLinesStr = geSource.getHeaderLines().replace('##','\n##')
            
            cls.WriteExpandedElementsToFile(geSource, chrSizeDict, outputFile, headLinesStr, writeHeaderFlag=True)
            os.remove(tempFn)
        
        else:
            writeHeaderFlag = True
            for chr in GenomeInfo.getChrList(genome):
                gRegion = GenomeRegion(genome, chr, 0, chrSizeDict[chr])
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
        '''The format of the history element with the output of the tool.
        Note that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.
        '''
        return 'gtrack'
    
