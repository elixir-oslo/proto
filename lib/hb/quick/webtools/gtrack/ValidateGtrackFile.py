from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
from gold.origdata.GtrackSorter import sortedGeSourceHasOverlappingRegions
from gold.util.CustomExceptions import InvalidFormatError
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool


#This is a template prototyping GUI that comes together with a corresponding web page.
#

class ValidateGtrackFile(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Validate GTrack file"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Select a specific genome?', 'Genome build:', 'Select GTrack file:']

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

        fnSource = ExternalTrackManager.extractFnFromGalaxyTN(choices[2].split(':'))

        core = HtmlCore()
        core.begin()

        valid = False
        try:
            core.header('Validating GTrack headers')
            core.styleInfoBegin(styleClass='debug')

            print str(core)
            core = HtmlCore()

            gtrackSource = GtrackGenomeElementSource(fnSource, choices[1] if choices[0]=='Yes' else None, printWarnings=True)

            core.append('Done')
            core.styleInfoEnd()
            core.header('Validating complete GTrack file')
            core.styleInfoBegin(styleClass='debug')

            print str(core)
            core = HtmlCore()

            try:
                for ge in gtrackSource:
                    pass
            except Exception, e:
                raise
            else:
                core.append('Done')

                core.styleInfoEnd()
                core.header('Checking for overlap')
                core.styleInfoBegin(styleClass='debug')

                print str(core)
                core = HtmlCore()

                if gtrackSource.getHeaderDict()['no overlapping elements'] and sortedGeSourceHasOverlappingRegions(gtrackSource):
                    raise InvalidFormatError("Error: genome elements are overlapping while header variable 'no overlapping elements' is True.")

                core.append('Done')
                valid = True
        except Exception, e:
            core.append(str(e))
            valid = False

        core.styleInfoEnd()

        core.divider()
        core.header('Conclusion:')
        core.styleInfoBegin(styleClass='donemessage' if valid else 'errormessage')
        core.highlight('The GTrack file has %s syntax' % ('valid' if valid else 'invalid'))
        core.styleInfoEnd()

        core.end()
        print str(core)

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

        return GeneralGuiTool._checkHistoryTrack(choices, 2, genome, 'GTrack', validateFirstLine=False)

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
        core.paragraph('Checks a GTrack file for correspondence to the GTrack specification. '
                       'For the latest version of the specification, see the "Show GTrack specification" tool.')

        core.divider()
        core.smallHeader('Genome')
        core.paragraph('If a genome build is selected, the tool will check whether all coordinates '
                       'fall within the coordinate system of the genome build (i.e. based on the sequence names and lengths). '
                       'Also, some GTrack files require a specified genome to be valid, e.g. if bounding regions '
                       'are specified without explicit end coordinates.')

        core.divider()
        core.smallHeader('Notice')
        core.paragraph('The results of the validation is output as a new history element. '
                       'A correctly run history item, i.e. one colored green, does not mean that the GTrack file '
                       'has been found valid. One must click the eye icon of the history item to see the correct '
                       'conclusion.')
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
    def getOutputFormat(choices):
       '''The format of the history element with the output of the tool.
       Note that html output shows print statements, but that text-based output
       (e.g. bed) only shows text written to the galaxyFn file.
       '''
       return 'customhtml'
