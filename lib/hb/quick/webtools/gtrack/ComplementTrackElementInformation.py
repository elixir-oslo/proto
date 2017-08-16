from collections import OrderedDict

from gold.origdata.GtrackComplementer import complementGtrackFileAndWriteToFile
from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool


#This is a template prototyping GUI that comes together with a corresponding web page.
#

class ComplementTrackElementInformation(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Complement GTrack columns"

    @staticmethod
    def getInputBoxNames():
        '''Returns a list of names for input boxes, implicitly also the number
        of input boxes to display on page. Each such box will call function
        getOptionsBoxK, where K is in the range of 1 to the number of boxes'''
        return ['Select a specific genome?', \
                'Genome build: ', \
                'GTrack file to be complemented: ', \
                'GTrack file with complementing information: ', \
                'Intersecting factor: ', \
                'Columns to add to the first track']

    @staticmethod    
    def getOptionsBox1():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '''
        return ['No', 'Yes']
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '''
        if prevChoices[0] == 'Yes':
            return "__genome__"

    @staticmethod    
    def getOptionsBox3(prevChoices):
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return ('__history__', 'gtrack')
    
    @staticmethod    
    def getOptionsBox4(prevChoices): 
        '''Returns a list of options to be displayed in the second options box,
        which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous
        input boxes (that is, list containing only one element for this case) 
        '''
        return ('__history__', 'gtrack')
    
    @staticmethod    
    def getOptionsBox5(prevChoices):
        '''Returns a list of options to be displayed in the second options box,
        which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous
        input boxes (that is, list containing only one element for this case)
        '''
        if prevChoices[2] and prevChoices[3]:
            fnSource = ExternalTrackManager.extractFnFromGalaxyTN(prevChoices[2].split(':'))
            fnDB = ExternalTrackManager.extractFnFromGalaxyTN(prevChoices[3].split(':'))
            
            gtrackDBColumnSpec = GtrackGenomeElementSource(fnDB).getColumnSpec().keys()
            gtrackSourceColumnSpec = GtrackGenomeElementSource(fnSource).getColumnSpec().keys()
            
            resultlist = ['Element id'] if 'id' in gtrackDBColumnSpec and 'id' in gtrackSourceColumnSpec else []
            
            commonColumns = list(set(gtrackDBColumnSpec) & set(gtrackSourceColumnSpec))
            tupleKey = True if any(x in commonColumns for x in ['start', 'end']) else False
            resultlist += ['Positional information'] if tupleKey else [] 
            
            return resultlist
        
        return None
    
    @staticmethod    
    def getOptionsBox6(prevChoices):
        if prevChoices[3]:
            extraDbColumnsDict = OrderedDict()
            fnSource = ExternalTrackManager.extractFnFromGalaxyTN(prevChoices[2].split(':'))
            fnDB = ExternalTrackManager.extractFnFromGalaxyTN(prevChoices[3].split(':'))
            
            gtrackDB = GtrackGenomeElementSource(fnDB)
            gtrackSource = GtrackGenomeElementSource(fnSource)
            
            extraDbColumns = [v for v in gtrackDB.getColumns() if not v in gtrackSource.getColumns()] #list(set(gtrackDBColumnSpec) - set(gtrackSourceColumnSpec))
            for column in extraDbColumns:
                extraDbColumnsDict[column] = False
            return extraDbColumnsDict
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history. If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.gtr
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
        resultLines = []

        outputFile=open(galaxyFn,"w")
        fnSource = ExternalTrackManager.extractFnFromGalaxyTN(choices[2].split(':'))
        fnDB = ExternalTrackManager.extractFnFromGalaxyTN(choices[3].split(':'))
        intersectingFactor = 'id' if choices[4] == 'Element id' else 'position'
        
        colsToAdd = []
        colsToAddDict = choices[5]
        for key in colsToAddDict:
            if colsToAddDict[key]:
                colsToAdd.append(key)

        genome = choices[1] if choices[0] == 'Yes' else None
        
        try:
            complementGtrackFileAndWriteToFile(fnSource, fnDB, galaxyFn, intersectingFactor, colsToAdd, genome)
        except Exception, e:
            import sys
            print >> sys.stderr, e

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        genome = choices[1] if choices[0] == 'Yes' else None
        if genome == '':
            return 'Please select a genome build.'
        
        errorStr = GeneralGuiTool._checkHistoryTrack(choices, 2, genome, 'first GTrack')
        if errorStr:
            return errorStr
        errorStr = GeneralGuiTool._checkHistoryTrack(choices, 3, genome, 'second GTrack')
        if errorStr:
            return errorStr
            
        if choices[2] == choices[3]:
            return 'Please select two different GTrack files.'
        
        if len(choices[4]) == 0:
            return 'Error: the GTrack files do not contain common intersecting factors (positional information or "id" column).'
        
    
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
    @staticmethod
    def getToolDescription():
        core = HtmlCore()
        core.paragraph('This tool is used to complement the data of a GTrack '
                       'file with additional columns from another GTrack file. '
                       'Note that all data lines of the first GTrack file is '
                       'retained, but the contents of the second is only used if '
                       'the tool finds a match.')
        core.divider()
        core.smallHeader('Genome')
        core.paragraph('Some GTrack files require a specified genome to be valid, e.g. if bounding regions '
                       'are specified without explicit end coordinates.')
        
        core.divider()
        core.smallHeader('Intersecting factor')
        core.paragraph('This choice governs how a the data lines of the two '
                       'GTrack files are matched.')
        core.descriptionLine('Element ID', 'the data lines are matched on the ' +\
                             str(HtmlCore().emphasize('id')) + ' column.', emphasize=True)
        core.descriptionLine('Positional information', \
                             'the matching is done using any of the ' + \
                             '%s, %s, %s, and %s columns ' % \
                             tuple(str(HtmlCore().emphasize(x)) for x in \
                              ['genome', 'seqid', 'start', 'end']) +\
                             'that are defined in both ' +\
                             'GTrack files. Note that the match must be complete, ' +\
                             'e.g. matching both start and end if both are ' +\
                             'defined for one of the GTrack files.', emphasize=True)
        core.divider()
        core.smallHeader('Example')
        core.paragraph('File 1:')

        core.styleInfoBegin(styleClass='debug')
        core.append(
'''##track type: valued segments
###seqid  start  end  value  id
chrM      100    120  2.5    A
chrM      200    220  1.2    B''')
        core.styleInfoEnd()

        core.paragraph('File 2:')

        core.styleInfoBegin(styleClass='debug')
        core.append(
'''##track type: points
###seqid  start  strand  sth  other  id
chrM      300    +       b    yes    B
chrM      400    -       c    yes    C
chrM      500    -       a    no     A''')
        core.styleInfoEnd()

        core.paragraph('Complementing on "Element ID" and choosing the ' +\
                        'additional columns %s and %s, gives:' % \
                        tuple(str(HtmlCore().emphasize(x)) for x in ('strand', 'other')))
        
        core.styleInfoBegin(styleClass='debug')
        core.append(
'''##gtrack version: 1.0
##track type: valued segments
##uninterrupted data lines: true
##sorted elements: true
##no overlapping elements: true
###seqid  start  end  value  strand  id  other
chrM      100    120  2.5    -       A   no
chrM      200    220  1.2    +       B   yes''')
        core.styleInfoEnd()
        
        return str(core)

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
    def getOutputFormat(choices=None):
        return 'gtrack'
    #
