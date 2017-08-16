from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.util.GenomeInfo import GenomeInfo
from config.Config import NONSTANDARD_DATA_PATH, ORIG_DATA_PATH, PARSING_ERROR_DATA_PATH, NMER_CHAIN_DATA_PATH
from quick.util.CommonFunctions import ensurePathExists
from gold.util.CommonFunctions import createDirPath
import shutil, os
from collections import OrderedDict


class RemoveGenomeTool(GeneralGuiTool):
    ALL_PATHS = OrderedDict([('collectedTracks', NONSTANDARD_DATA_PATH),
                             ('standardizedTracks', ORIG_DATA_PATH),
                             ('parsingErrorTracks', PARSING_ERROR_DATA_PATH),
                             ('nmerChains', NMER_CHAIN_DATA_PATH),
                             ('preProcessedTracks (noOverlaps)', createDirPath('', '', allowOverlaps=False)),
                             ('preProcessedTracks (withOverlaps)', createDirPath('', '', allowOverlaps=True))])

    @staticmethod
    def getToolName():
        return "Remove genome"

    @staticmethod
    def getInputBoxNames():
        return [('Genome', 'genome'),
                ('From which paths to remove the genome', 'paths')]

    @staticmethod    
    def getOptionsBoxGenome():
        return "__genome__"
    
    @classmethod
    def getOptionsBoxPaths(cls, prevChoices):
        return OrderedDict([(key, True) for key in cls.ALL_PATHS.keys()])
    
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
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history. If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.gtr
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
            
        print 'Executing... starting to remove ' + choices[0] + os.linesep

        paths = [cls.ALL_PATHS[key] for key,val in choices.paths.iteritems() if val]

        for p in paths:
            genome = choices.genome
            origPath = os.sep.join([ p, genome ])
            trashPath = os.sep.join([ p, ".trash", genome ])

            if os.path.exists(origPath):
                print 'Moving ' + genome + ' to .trash in folder: ' + p + os.linesep
                ensurePathExists(trashPath)
                shutil.move(origPath, trashPath)


    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        if not choices.genome:
            return 'Please select a genome'

        if not any([val for val in choices.paths.values()]):
            return 'Please select at least one path'
    
    #@staticmethod
    #def isPublic():
    #    return False
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    @staticmethod
    def getToolDescription():
        return 'This tool will remove a genome and associated tracks. '+\
               '(Note: Genome is not deleted, but moved to .trash directories)'
    
    @staticmethod
    def isDynamic():
        return False

    #@staticmethod
    #def isHistoryTool():
    #    return True
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
    #@staticmethod
    #def validateAndReturnErrors(choices):
    #    '''
    #    Should validate the selected input parameters. If the parameters are not valid,
    #    an error text explaining the problem should be returned. The GUI then shows this
    #    to the user and greys out the execute button. If all parameters are valid, the method
    #    whould return None, which enables the execute button.
    #    '''
    #    return None
