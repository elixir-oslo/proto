import os
import math
from collections import OrderedDict, namedtuple
from os.path import isfile

import third_party.safeshelve as safeshelve
import quick.extra.StandardizeTrackFiles as StandTrackFiles
from config.Config import DATA_FILES_PATH
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from gold.util.CustomExceptions import InvalidFormatError
from gold.util.CommonFunctions import getOrigFns, getOrigFn

#This is a template prototyping GUI that comes together with a corresponding web page.
#

class StandardizeTrackFilesTool(GeneralGuiTool):

    SHELVE_FN = DATA_FILES_PATH + os.sep + 'StandardizerTool.shelve'
    
    DirectionTuple = namedtuple('DirectionTuple', ('parseFileArg','inputFileTree','outputFileTree'))
    
    DIRECTION_DICT = OrderedDict([ \
                 ('Collected to standardized tracks', DirectionTuple('coll_to_std','collected','standardized')),\
                 ('Collected to collected tracks', DirectionTuple('coll_to_coll','collected','collected')),\
                 ('Standardized to collected tracks', DirectionTuple('std_to_coll','standardized','collected')),\
                 ('Standardized to standardized tracks', DirectionTuple('std_to_std','standardized','standardized')), \
                 ('Standardized to parsing error tracks', DirectionTuple('std_to_error','standardized','parsing error')),\
                 ('Parsing error to standardized tracks', DirectionTuple('error_to_std','parsing error','standardized'))])
    
    _extraParams = []
        
    @staticmethod
    def getToolName():
        return "Standardize track files"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return [ \
            ('Genome', 'genome'),\
            ('Track', 'track'),\
            ('Direction of operation','direction'),\
            ('Run recursively on all subtypes','allSubTypes'),\
            ('Depth of recursion','subTypeDepth'),\
            ('File to display', 'file'),\
            ('Input file content', 'content'),\
            ('Previous run', 'prevRun'),\
            ('Parser class name', 'parserClass')]\
            + ['Extra parameter','Value for parameter']*10\
            + [('Other keyword arguments', 'kwArgs'),\
               ('Class description', 'description')]
    
    @staticmethod
    def getInputBoxOrder():
        return ('genome','track','direction','allSubTypes','subTypeDepth','file','content','prevRun','parserClass','description',10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,'kwArgs')
    
    @staticmethod    
    def getOptionsBoxGenome(): 
        '''Returns a list of genomes'''
        return '__genome__'
        
    @staticmethod    
    def getOptionsBoxTrack(prevChoices): 
        '''Returns a list of tracks for selected genome'''
        return '__track__'
    
    @staticmethod   
    def getOptionsBoxAllSubTypes(prevChoices):
        return ['False','True']
    
    @staticmethod    
    def getOptionsBoxSubTypeDepth(prevChoices): 
        if prevChoices.allSubTypes:
            return ['1','2','3','4','5','6','7','8','9','10']
    
    @staticmethod    
    def getOptionsBoxDirection(prevChoices):
        return StandardizeTrackFilesTool.DIRECTION_DICT.keys()
    
    @staticmethod
    def _getFilePathList(prevChoices, input=True):
        if input:
            fileTree = StandardizeTrackFilesTool.DIRECTION_DICT[prevChoices.direction].inputFileTree
        else:
            fileTree = StandardizeTrackFilesTool.DIRECTION_DICT[prevChoices.direction].outputFileTree
            
        return getOrigFns(prevChoices[0], prevChoices[1].split(':'), '', fileTree=fileTree)
        
    @staticmethod    
    def getOptionsBoxFile(prevChoices):
        filePathList = StandardizeTrackFilesTool._getFilePathList(prevChoices, input=True)
        
        if len(filePathList)==0:
            return None
        
        return [v.split('/')[-1] for v in filePathList]
    
    @staticmethod
    def _getFilePath(filePathList, prevChoices):
        filePathList = [v for v in filePathList if os.path.basename(v) == prevChoices.file]
        assert len(filePathList) == 1
        return filePathList[0]
    
    @staticmethod    
    def getOptionsBoxContent(prevChoices):
        if prevChoices.file:
            fileStr = ''
        
            filePathList = StandardizeTrackFilesTool._getFilePathList(prevChoices, input=True)
            filePath = StandardizeTrackFilesTool._getFilePath(filePathList, prevChoices)
            
            if len(filePath)>0 and isfile(filePath):
                fileContent = open(filePath,'r')
                fileStr = ''.join([fileContent.readline() for i in range(10)])
            
            if fileStr != '':
                return (fileStr, 4, True)
    
    @staticmethod    
    def getOptionsBoxPrevRun(prevChoices):
        if prevChoices.file or prevChoices.allSubTypes == 'True':
            stored = StandTrackFiles.getStandTrackFileToolCache(prevChoices.genome, prevChoices.track.split(':'))
            if stored:
                return (stored, 1, True)
    
    @staticmethod    
    def getOptionsBoxParserClass(prevChoices):
        "Returns a list of options to be displayed in the first options box"
        if prevChoices.file or prevChoices.allSubTypes == 'True':
            #return [v[0] for v in getmembers(StandTrackFiles, isclass) if 'GeneralTrackDataModifier' in [c.__name__ for c in getmro(getattr(StandTrackFiles, v[0]))]]
            return StandTrackFiles.getParserClassList()
    
    @staticmethod    
    def getOptionsBoxDescription(prevChoices): 
        if prevChoices.parserClass:
            docString = StandTrackFiles.getParserClassDocString(prevChoices.parserClass)
            if docString:
                return (docString,len(docString.split('\n')),True)

    @staticmethod
    def _setExtraParams(prevChoices):
        paramList = StandTrackFiles.getFormattedParamList(prevChoices.parserClass, argStr='%s (Mandatory parameter)', kwArgStr='%s (default: %s)')
        StandardizeTrackFilesTool._extraParams = paramList
        
    @classmethod
    def _getColumnList(cls, prevChoices, index):
        if prevChoices.file or prevChoices.allSubTypes == 'True':
            if cls._extraParams == []:
                cls._setExtraParams(prevChoices)
                
            paramNum = int(math.floor((index - 9) / 2))
            
            if len(cls._extraParams) > paramNum:
                if index % 2 == 0:
                    return ''
                else:
                    return[cls._extraParams[paramNum]]
            else:
                return None
    
    @staticmethod  
    def getOptionsBox10(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 9)
    
    @staticmethod  
    def getOptionsBox11(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 10)
    
    @staticmethod  
    def getOptionsBox12(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 11)
    
    @staticmethod  
    def getOptionsBox13(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 12)
    
    @staticmethod  
    def getOptionsBox14(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 13)
    
    @staticmethod  
    def getOptionsBox15(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 14)
    
    @staticmethod  
    def getOptionsBox16(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 15)
    
    @staticmethod  
    def getOptionsBox17(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 16)
    
    @staticmethod  
    def getOptionsBox18(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 17)
    
    @staticmethod  
    def getOptionsBox19(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 18)
    
    @staticmethod  
    def getOptionsBox20(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 19)
    
    @staticmethod  
    def getOptionsBox21(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 20)
    
    @staticmethod  
    def getOptionsBox22(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 21)
    
    @staticmethod  
    def getOptionsBox23(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 22)
    
    @staticmethod  
    def getOptionsBox24(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 23)
    
    @staticmethod  
    def getOptionsBox25(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 24)
    
    @staticmethod  
    def getOptionsBox26(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 25)
    
    @staticmethod  
    def getOptionsBox27(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 26)
    
    @staticmethod  
    def getOptionsBox28(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 27)
    
    @staticmethod  
    def getOptionsBox29(prevChoices):
        return StandardizeTrackFilesTool._getColumnList(prevChoices, 28)
    
    @staticmethod    
    def getOptionsBoxKwArgs(prevChoices): 
        if prevChoices.file or prevChoices.allSubTypes == 'True':
            return ''

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
        
        extraParams = ['direction=' + cls.DIRECTION_DICT[choices.direction].parseFileArg,\
                       'allSubTypes=' + choices.allSubTypes,\
                       'subTypeDepth=' + choices.subTypeDepth]
        
        if len(cls._extraParams)>0:
            for i in range(len(cls._extraParams)):
                paramName = choices[i*2+9]
                param = paramName[:paramName.find('(')].strip()
                val = choices[i*2+10].strip()
                if val !='':
                    extraParams.append(param + '=' + val)
                    
        extraParams += [v.strip() for v in choices.kwArgs.split(',')] if choices.kwArgs.strip() != '' else []
        
        arguments = [choices.genome, choices.track, choices.parserClass] + extraParams
        print 'Running with these arguments: ', arguments
        
        StandTrackFiles.runParserClass(arguments, printUsageWhenError=False)
        
        try:
            if choices.file:
                filePathList = cls._getFilePathList(choices, input=False)
                filePath = cls._getFilePath(filePathList, choices)
                print ''
                print ''
                print '10 first lines of file: ' + filePath
                print ''
                fileObj = open(filePath,'r')
                for i in range(10):
                    print fileObj.readline().strip()#.replace('\n','<br>')
                fileObj.close()
        except:
            pass

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        if not choices.file and not choices.allSubTypes == 'True':
            return ''
    
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
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
    #
    #@staticmethod    
    #def getOutputFormat():
    #    return 'html'
    #
