from quick.application.GalaxyInterface import GalaxyInterface
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.MultiTrackMixin import MultiTrackMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class AnalyzeMultiTrackRelations(GeneralGuiTool, MultiTrackMixin, UserBinMixin):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Analyze relations between multiple tracks"

    @classmethod
    def getInputBoxNames(cls):
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).
        '''
        return cls.getMultiTrackInputBoxNames() + \
               [('Select analysis', 'Analysis'),
                ('Lower-order relations to preserve in null model', 'preserveRelations'),
                ('Track properties to preserve in null model', 'preserveProperties'),
                ('Number of MC samples', 'numResamplings')] + \
               cls.getInputBoxNamesForUserBinSelection()

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None


    @staticmethod
    def getOptionsBoxAnalysis(prevChoices):
        #return ['Base pair overlap', 'Track inclusions']
        return ['Base pair coverage of all track combinations', \
                'Inclusion structure between tracks', \
                'Observed versus expected overlap with various relations preserved', \
                'Factors of observed versus expected overlap with various relations preserved', \
                'Hypothesis testing on multi-track relations', \
                'Coverage depth of multiple tracks along the genome']

    @staticmethod
    def getOptionsBoxPreserveRelations(prevChoices):
        #if prevChoices:
        #    return repr(prevChoices), 2, True

        if prevChoices.Analysis == 'Hypothesis testing on multi-track relations':
            return ['Do not preserve any pair-wise relations', \
                    'Preserve pair-wise relation between Track 1 and Track 3', \
                    'Preserve pair-wise relation between Track 2 and Track 3']

    @staticmethod
    def _hypothesisTestingIsSelcted(choices):
        return choices.Analysis == 'Hypothesis testing on multi-track relations'

    @classmethod
    def getOptionsBoxPreserveProperties(cls, prevChoices):
        if not (cls._hypothesisTestingIsSelcted(prevChoices) and prevChoices.PreserveRelations != None):
            return None

        if prevChoices.PreserveRelations == 'Do not preserve any pair-wise relations':
            tracks = 'T1 and T2'
            plural = 's'
        elif prevChoices.PreserveRelations == 'Preserve pair-wise relation between Track 1 and Track 3':
            tracks = 'T2'
            plural = ''
        elif prevChoices.PreserveRelations == 'Preserve pair-wise relation between Track 2 and Track 3':
            tracks = 'T1'
            plural = ''
        else:
            raise Exception(prevChoices.PreserveRelations )
        return [entry%(plural,tracks) for entry in ['For randomized track%s (%s), preserve segment and inter-segment lengths', \
                                                    'For randomized track(%s) (%s), preserve segment lengths']]

    @staticmethod
    def _getRandomizationAnalysisOption(choices):
        rtc = 'PermutedSegsAndIntersegsTrack' if 'inter-segment' in choices.PreserveProperties else 'PermutedSegsAndSampledIntersegsTrack'
        if choices.PreserveRelations == 'Do not preserve any pair-wise relations':
            randTrackClassTemplate = rtc+'_'+rtc
        elif choices.PreserveRelations == 'Preserve pair-wise relation between Track 1 and Track 3':
            randTrackClassTemplate = '_'+rtc
        elif choices.PreserveRelations == 'Preserve pair-wise relation between Track 2 and Track 3':
            randTrackClassTemplate = rtc+'_'
        else:
            raise
        return '[assumptions=%s]' % randTrackClassTemplate

    @staticmethod
    def getOptionsBoxNumResamplings(prevChoices):
        if prevChoices.Analysis == 'Hypothesis testing on multi-track relations':
            return ['2','10','100','1000']

    @staticmethod
    def getNamedTuple():
        from collections import namedtuple
        return namedtuple('ChoiceTuple', ['Genome','Track1Source','Track1','Track2Source','Track2','Track3Source','Track3','Track4Source','Track4','Track5Source','Track5','Track6Source','Track6','Analysis','PreserveRelations', 'PreserveProperties', 'NumResamplings', 'CompareIn', 'Bins', 'CustomRegion', 'BinSize', 'HistoryBins'])

    @staticmethod
    def getDemoSelections():
        from collections import namedtuple
        ChoiceTuple = namedtuple('ChoiceTuple', ['Genome','Track1Source','Track1','Track2Source','Track2','Track3Source','Track3','Track4Source','Track4','Track5Source','Track5','Track6Source','Track6','Analysis','PreserveRelations', 'PreserveProperties', 'NumResamplings', 'CompareIn', 'Bins', 'CustomRegion', 'BinSize', 'HistoryBins'])
        #prevChoices = ChoiceTuple('hg18', 'Track', 'Sample data:Track formats:Valued segments (case-control)', 'Track', 'Sample data:Track formats:Segments', 'Track', 'Sample data:Track formats:Valued segments (number)', 'None', 'None', 'None', 'None', 'None', 'None', 'Base pair coverage of all track combinations','None', 'None', 'None', 'Chromosomes', 'chr1', 'None', 'None', 'None')
        prevChoices = ChoiceTuple('hg18', 'Track', 'Sample data:Track formats:Valued segments (case-control)', 'Track', 'Sample data:Track formats:Segments', 'Track', 'Sample data:Track formats:Valued segments (number)', 'None', 'None', 'None', 'None', 'None', 'None', 'Base pair coverage of all track combinations','None', 'None', 'None', 'Custom specification', 'None', 'chr1:1-100k', '*', 'None')
        return prevChoices


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        genome = choices.Genome
        #trackNames = [choices[choiceIndex].split(':') for choiceIndex in [2,4,6]]
        #trackNames = [x.split(':') for x in [choices.Track1, choices.Track2, choices.Track3]]
        trackNames = cls.getAllChosenTracks(choices)
        print trackNames
        #for tnIndex, choiceIndex in zip(range(3),[2,4,6]):
        #    tn = choices[choiceIndex].split(':')
        #    trackNames[tnIndex] = tn
            #trackNames[tnIndex] = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, tn) \
            #    if ExternalTrackManager.isGalaxyTrack(tn) \
            #    else tn

        #analysisDef = 'dummy [trackNameIntensity=%s]-> ThreeWayBpOverlapStat' % '|'.join(trackNames[2])
        #Do not preserve any pair-wise relations', 'Preserve pair-wise relation between Track 1 and Track 3', 'Preserve pair-wise relation between Track 2 and Track 3']
        #['Base pair coverage of all track combinations', 'Inclusion structure between tracks', 'Observed versus expected overlap with various relations preserved', 'Hypothesis testing on multi-track relations']
        if choices.Analysis == 'Base pair coverage of all track combinations':
            analysisDef = 'dummy -> ThreeWayBpOverlapStat'
        elif choices.Analysis == 'Inclusion structure between tracks':
            analysisDef = 'dummy -> ThreeWayTrackInclusionBpOverlapStat'
        elif choices.Analysis == 'Observed versus expected overlap with various relations preserved':
            pass
        elif choices.Analysis == 'Factors of observed versus expected overlap with various relations preserved':
            analysisDef = 'Dummy [rawStatistic=ThreeWayExpectedWithEachPreserveCombinationBpOverlapStat]  [referenceResDictKey=preserveNone] -> GenericFactorsAgainstReferenceResDictKeyStat'
        elif choices.Analysis == 'Hypothesis testing on multi-track relations':
            randOption = cls._getRandomizationAnalysisOption(choices)
            numResamplingsOption = '[numResamplings=%s]' % choices.NumResamplings
            #assert len(trackNames) == 3, trackNames #currently, due to ThreeTrackBpsCoveredByAllTracksStat
            #analysisDef = 'dummy [tail=different] [rawStatistic=ThreeTrackBpsCoveredByAllTracksStat] %s %s -> RandomizationManagerStat' % (randOption, numResamplingsOption)
            resDictKey = '1'*(len(trackNames))
            analysisDef = 'dummy [tail=different] [rawStatistic=SingleValExtractorStat] [childClass=ThreeWayBpOverlapStat] [resultKey=%s] %s %s -> RandomizationManagerStat' % (resDictKey, randOption, numResamplingsOption)
            print analysisDef
        elif choices.Analysis == 'Coverage depth of multiple tracks along the genome':
            analysisDef = 'dummy -> ThreeWayCoverageDepthStat'
        else:
            raise Exception(choices.Analysis)
        analysisDef = 'dummy [extraTracks=%s] ' % '&'.join(['|'.join(tn) for tn in trackNames[2:] ]) + analysisDef
        #GalaxyInterface.run(trackNames[0], trackNames[1], analysisDef, regSpec, binSpec, genome, galaxyFn, trackNames[2], printRunDescription=False)
        GalaxyInterface.run(trackNames[0], trackNames[1], analysisDef, regSpec, binSpec, genome, galaxyFn, printRunDescription=False)
        #userBinSource, fullRunArgs = GalaxyInterface._prepareRun(None, None, analysisDef, 'chr1:1-1m', '*', genome)
        #result = AnalysisDefJob(analysisDef, trackNames[0], trackNames[1], userBinSource, **fullRunArgs).run()
        #GalaxyInterface._handleRunResult(result, '', userBinSource, genome, galaxyFn)

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        return None

    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True
    #
    #@staticmethod
    #def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    #@staticmethod
    #def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    #@classmethod
    #def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getOutputFormat(choices):
    #    '''
    #    The format of the history element with the output of the tool. Note
    #    that html output shows print statements, but that text-based output
    #    (e.g. bed) only shows text written to the galaxyFn file.In the latter
    #    case, all all print statements are redirected to the info field of the
    #    history item box.
    #    '''
    #    return 'html'
