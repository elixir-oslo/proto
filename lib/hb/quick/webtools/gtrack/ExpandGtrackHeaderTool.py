import os

from gold.origdata.GtrackHeaderExpander import expandHeadersOfGtrackFileAndWriteToFile, \
    expandHeadersOfGtrackFileAndReturnComposer, \
    EXPANDABLE_HEADERS, NOT_GUARANTEED_EXPANDABLE_HEADERS, VALUE_NOT_KEPT_HEADERS
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class ExpandGtrackHeaderTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Expand GTrack headers"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return [('Select input source:', 'source'), \
                ('Select GTrack file:', 'history'), \
                ('Type or paste in tabular file:', 'input'), \
                ('Select how to handle whitespace:', 'whitespace'), \
                ('Select a specific genome?', 'selectGenome'), \
                ('Genome build:', 'genome'), \
                ('Header output:', 'allHeaders')]

    @staticmethod    
    def getOptionsBoxSource():
        return ['Tabular file from history', 'Tabular file from input box']

    @staticmethod    
    def getOptionsBoxHistory(prevChoices):
        if prevChoices.source == 'Tabular file from history':
            return '__history__', 'gtrack'

    @staticmethod    
    def getOptionsBoxInput(prevChoices):
        if prevChoices.source == 'Tabular file from input box':
            return '', 10
            
    @staticmethod
    def getOptionsBoxWhitespace(prevChoices):
        if prevChoices.source == 'Tabular file from input box':
            return ['Change whitespace when needed', 'Keep whitespace exact']
    
    @staticmethod    
    def getOptionsBoxSelectGenome(prevChoices):
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '''
        return ['No', 'Yes']
    
    @staticmethod    
    def getOptionsBoxGenome(prevChoices):
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '''
        if prevChoices.selectGenome == 'Yes':
            return "__genome__"

    @staticmethod
    def getOptionsBoxAllHeaders(prevChoices): 
        return ['Only non-default headers', 'All headers']

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
        
        genome = choices.genome if choices.selectGenome == 'Yes' else None
        onlyNonDefault = choices.allHeaders == 'Only non-default headers'
        
        
        try:
            if choices.history:
                inFn = ExternalTrackManager.extractFnFromGalaxyTN(choices.history.split(':'))
                expandHeadersOfGtrackFileAndWriteToFile(inFn, galaxyFn, genome, onlyNonDefault)
            else:
                if choices.whitespace == 'Keep whitespace exact':
                    input = choices.input
                else:
                    input = ''
                    for line in choices.input.split(os.linesep):
                        line = line.strip()
                        if (line.startswith('###') and len(line) > 3 and line[3] != '#') \
                            or not line.startswith('#'):
                            line = line.replace(' ', '\t')
                        else:
                            line = line.replace('\t', ' ')
                        input += line + os.linesep
            
                composer = expandHeadersOfGtrackFileAndReturnComposer('', genome, strToUseInsteadOfFn=input)
                composer.composeToFile(galaxyFn, onlyNonDefault=onlyNonDefault)
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
        
        genome = choices.genome if choices.selectGenome == 'Yes' else None
        
        if genome == '':
            return 'Please select a genome build.'
        
        if choices.source == 'Tabular file from history':
            return GeneralGuiTool._checkHistoryTrack(choices, 'history', genome, 'GTrack')
        else:
            if choices.input == '':
                return 'Please type or paste a GTrack file into the input box.'
        
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
        core.paragraph('The GTrack format requires a set of header lines to be a valid GTrack file. '
                       '(See the "Show GTrack specification" tool for the specification of the format.) '
                       'This tools tries to generate missing GTrack header lines based on the contents '
                       'of the GTrack file selected. The "fixed" GTrack file is returned as a new '
                       'history element.')
        core.divider()
        
        core.smallHeader('The following header lines are affected by this tool')
        core.paragraph('Header lines that are guaranteed to be properly generated:')
        core.unorderedList([x.capitalize() for x in EXPANDABLE_HEADERS])
        core.paragraph('Header lines that are generated, but not guaranteed to get the correct value:')
        core.unorderedList([x.capitalize() for x in NOT_GUARANTEED_EXPANDABLE_HEADERS])
        core.paragraph('Header lines that may change as part of the expansion (but are part of the '
                       'extended GTrack definition, and thus superfluous):')
        core.unorderedList([x.capitalize() for x in VALUE_NOT_KEPT_HEADERS])
        core.divider()
        
        core.smallHeader('GTrack subtypes')
        core.paragraph('If the header "subtype url" is specified, the corresponding subtype '
                       'is read and the headers defined by the subtype are explicitly included. '
                       'Also if the input file contains any headers from the extended specification, '
                       'GTrack subtype information may be added to the output file. '
                       'The following GTrack subtypes are automatically detected '
                       'from the contents of the input file: ')

        from gold.origdata.GtrackComposer import StdGtrackComposer
        core.unorderedList(str(HtmlCore().link(x, x)) for x in StdGtrackComposer.GTRACK_PRIORITIZED_SUBTYPE_LIST)
        core.divider()
        
        core.smallHeader('Genome')
        core.paragraph('Some GTrack files require a specified genome to be valid, e.g. if bounding regions '
                       'are specified without explicit end coordinates.')
        core.divider()
        
        core.smallHeader('Notice')
        core.paragraph('This tool requires that the GTrack file already has a column specification '
                       'line. If your file does not have this, please use the "Convert tabular file to '
                       'GTrack" tool, where you can specify the column specification line. That tool '
                       'also carries out the same header expansion as this tool.')
        core.divider()
        
        core.smallHeader('Example')
        core.paragraph('Input file')
        core.styleInfoBegin(styleClass='debug')
        core.append(
'''##1-indexed: true
##end inclusive: true
###seqid  start  end   value
chrM      100    165   0
chrM      200    2900  1
chrM      3000   3900  1''')
        core.styleInfoEnd()
        
        core.paragraph('Output file (with only non-default headers)')
        core.styleInfoBegin(styleClass='debug')
        core.append(
'''##gtrack version: 1.0
##track type: valued segments
##value type: binary
##uninterrupted data lines: true
##sorted elements: true
##no overlapping elements: true
##1-indexed: true
##end inclusive: true
###seqid  start  end   value
chrM      100    165   0
chrM      200    2900  1
chrM      3000   3900  1''')
        core.styleInfoEnd()
        
        core.paragraph('Output file (with all headers)')
        core.styleInfoBegin(styleClass='debug')
        core.append(
'''##gtrack version: 1.0
##track type: valued segments
##value type: binary
##value dimension: scalar
##undirected edges: false
##edge weights: false
##edge weight type: number
##edge weight dimension: scalar
##uninterrupted data lines: true
##sorted elements: true
##no overlapping elements: true
##circular elements: false
##1-indexed: true
##end inclusive: true
###seqid  start  end   value
chrM      100    165   0
chrM      200    2900  1
chrM      3000   3900  1''')
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
        '''The format of the history element with the output of the tool.
        Note that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.
        '''
        return 'gtrack'
    
