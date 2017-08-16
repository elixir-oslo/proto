from collections import OrderedDict
from copy import copy

from gold.application.DataTypes import getSupportedFileSuffixesForPointsAndSegments
from gold.util.CommonFunctions import parseShortenedSizeSpec
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.webtools.GeneralGuiTool import GeneralGuiTool


#This is a template prototyping GUI that comes together with a corresponding web page.
#

class ExpandBedSegmentsTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Expand or contract points/segments"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        #can have two syntaxes: either a list of stings or a list of tuples where each tuple has two items(Name of box on webPage, name of getOptionsBox)
        return [('Genome build:', 'genome'), \
                ('Point or segment track from history:', 'history'), \
                ('Before expanding, treat track as:', 'conversion'), \
                ('Upstream flank (in bps):', 'upstream'), \
                ('Downstream flank (in bps):', 'downstream'), \
                ('Handle segments crossing chromosome borders by:', 'chrBorderHandling')]

    @staticmethod
    def getOptionsBoxGenome():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return '__genome__'

    @staticmethod
    def getOptionsBoxHistory(prevChoices):
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)
        '''
        return tuple(['__history__'] + getSupportedFileSuffixesForPointsAndSegments())

    _TRACK_TYPE_CONVERSION_OPTIONS_POINTS = OrderedDict([("Original format ('Points')", 'points')])
    _TRACK_TYPE_CONVERSION_OPTIONS_SEGMENTS = \
        OrderedDict([("Original format ('Segments')", 'segments'),\
                     ("The upstream end point of every segment (converted from 'Segments')", 'upstream'),\
                     ("The middle point of every segment (converted from 'Segments')", 'middle'),\
                     ("The downstream end point of every segment (converted from 'Segments')", 'downstream')])

    _TRACK_TYPE_CONVERSION_OPTIONS = copy(_TRACK_TYPE_CONVERSION_OPTIONS_POINTS)
    _TRACK_TYPE_CONVERSION_OPTIONS.update(_TRACK_TYPE_CONVERSION_OPTIONS_SEGMENTS)

    @staticmethod
    def getOptionsBoxConversion(prevChoices):
        if prevChoices.history:
            basicTF = ExpandBedSegmentsTool._getBasicTrackFormat(prevChoices, 'history', 'genome')[-1]
            if basicTF.lower().endswith('points'):
                return ExpandBedSegmentsTool._TRACK_TYPE_CONVERSION_OPTIONS_POINTS.keys()
            elif basicTF.lower().endswith('segments'):
                return ExpandBedSegmentsTool._TRACK_TYPE_CONVERSION_OPTIONS_SEGMENTS.keys()
            else:
                return []

    @staticmethod
    def getOptionsBoxUpstream(prevChoices):
        if prevChoices.history:
            return '0', 1

    @staticmethod
    def getOptionsBoxDownstream(prevChoices):
        if prevChoices.history:
            return '0', 1

    @staticmethod
    def getOptionsBoxChrBorderHandling(prevChoices):
        if prevChoices.history:
            return ['Cropping','Removing']

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

        galaxyTn = choices.history.split(':')
        inFn = ExternalTrackManager.extractFnFromGalaxyTN(galaxyTn)
        suffix = ExternalTrackManager.extractFileSuffixFromGalaxyTN(galaxyTn)

        treatTrackAs = cls._TRACK_TYPE_CONVERSION_OPTIONS[choices.conversion]

        GalaxyInterface.expandBedSegments(inFn, galaxyFn, choices.genome, \
                                          parseShortenedSizeSpec(choices.upstream), parseShortenedSizeSpec(choices.downstream), \
                                          treatTrackAs, removeChrBorderCrossing=(choices.chrBorderHandling=='Removing'), suffix=suffix)


    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''

        errorStr = ExpandBedSegmentsTool._checkTrack(choices)
        if errorStr:
            return errorStr

        basicTF = ExpandBedSegmentsTool._getBasicTrackFormat(choices, 'history', 'genome')[-1]
        if not any(x in basicTF.lower() for x in ['points', 'segments']):
            return 'Please select a history track with points or segments'

        try:
            parseShortenedSizeSpec(choices.upstream)
        except:
            return 'The upstream flank size is incorrectly specified: "%s". Please integer numbers, ' % choices.upstream + \
                   'or the shortened format, e.g. "20k" or "1m".'

        try:
            parseShortenedSizeSpec(choices.downstream)
        except:
            return 'The downstream flank size is incorrectly specified: "%s". Please integer numbers, ' % choices.downstream + \
                   'or the shortened format, e.g. "20k" or "1m".'

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
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.paragraph('This tool expands the segments of a file in one or both directions. '+ \
                       'It can also flatten a segment to its start, middle or end point before expading. '+ \
                       'If a strand column is specified, upstream and downstream expansion are defined in relation '+ \
                       'to the strand direction.')
        core.unorderedList(['Select the genome',
                            'Select the file you to expand. ',
                            'Select whether you want to treat the track as segments, or as start, middle or end points. ' + \
                            'Such conversion is done before any expansion or contraction is carried out.',
                            'Type in the number of base pairs you want to expand the segments in upstream and downstream direction. ' + \
                            'Contraction is performed by specifying negative values. ' + \
                            'A shortened format, specifying mega- and kilobases with "k" and "m", respectively, is supported.',
                            'Select whether you would like to remove segments that, after expansion, crosses chromosome border, or just crop them.',
                            'Click execute.' ])
        return str(core)
        return ''



    #
    #@staticmethod
    #def getToolIllustration():
    #    return None

    @staticmethod
    def getFullExampleURL():
        return 'u/hb-superuser/p/expand-bed-segments'

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
        if choices.history:
            inputFormat = ExternalTrackManager.extractFileSuffixFromGalaxyTN(choices.history.split(':'))
            return inputFormat if inputFormat != 'point.bed' else 'bed'
    #
