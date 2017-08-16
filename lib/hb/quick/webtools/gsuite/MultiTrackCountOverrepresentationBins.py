from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteConstants
from gold.track.Track import Track
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.GalaxyInterface import GalaxyInterface
from quick.gsuite.GSuiteHbIntegration import addTableWithTabularAndGsuiteImportButtons
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.SummarizedWrapperStat import SummarizedWrapperStat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixinForSmallBins
from quick.statistic.GSuiteBinEnrichmentPValWrapperStat import GSuiteBinEnrichmentPValWrapperStat
from quick.application.UserBinSource import GlobalBinSource


class MultiTrackCountOverrepresentationBins(GeneralGuiTool, GenomeMixin,
                                            UserBinMixinForSmallBins, DebugMixin):
    '''
    This is a template prototyping GUI that comes together with a corresponding
    web page.
    '''

    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_FILE_TYPES = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]
    SUMMARY_FUNC_DEFAULT = 'avg'

    Q1 = "Show me a list of all bins and the enrichment within each bin, based on the number of segments"
    Q1_SHORT = "Enrichment in bins [number of segments]"
    Q2 = "Show me a list of all binsand the enrichment within each bin, based on the number of base pairs covered by segments"
    Q2_SHORT = "Enrichment in bins [number of base pairs]"
    Q3 = "Show me a list of all bins and the enrichment within each bin, based on the number of segments. Also compute p-values for each bin."
    Q3_SHORT = "Enrichment in bins [number of segments, p-val]"

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        #return "Determine bins (of the genome) with suite overrepresentation"
        return "Rank genomic regions based on pairwise track enrichment"

    @classmethod
    def getToolDescription(cls):
        return ''

    @classmethod
    def getInputBoxNames(cls):
        '''
        Specifies a list of headers for the input boxes, and implicitly also
        the number of input boxes to display on the page. The returned list
        can have two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase (e.g. "firstKey")
        '''

        return  [('Basic user mode', 'isBasic'), ('', 'description'), ('<p>Which analysis question do you want to run?<p>','analysisName')] +\
                [('<br><p>Select a GSuite file containing the tracks you want to analyse:</p>', 'gsuite')] +\
                cls.getInputBoxNamesForGenomeSelection() +\
                [('', 'summaryFunc')] +\
                cls.getInputBoxNamesForUserBinSelection() +\
                cls.getInputBoxNamesForDebug()

    @staticmethod
    def getOptionsBoxIsBasic():
        return False

    @staticmethod
    def getOptionsBoxDescription(prevChoices):  # Alternatively: getOptionsBox1()
        desc = '<p><b>Tool description: </b></p> <p>This tool ranks specified genomic regions (bins) based on track enrichment. ' + \
                'You will need to specify which bins you want to rank. This will typically be done by selecting <i>Custom specification</i>' + \
                ' and choosing a main region (e.g. <i>chr1, chr2</i>) and a bin size, resulting in evenly distributed bins within those regions, all having the same size.</p> ' +\
                '<p>These bins are ranked based on the average or maximum track enrichment, which can be computed either based on number of base pairs covered by segments or the number of segments within each bin.</p>' + \
                '<p>Note: if p-values are to be computed, only average enrichment is supported (not maximum track enrichment).</p>'

        #if not prevChoices.isBasic:
            #desc += ' You can instead choose to rank based on the <i>maximum</i> track enrichment inside the bin, by selecting that option in the select menu.<br><br>'

        desc += ' <br><hr><br>'

        return '__rawstr__', desc


    def getOptionsBoxAnalysisName(cls, prevChoices):
        return [cls.Q1, cls.Q2, cls.Q3]

    @staticmethod
    def getOptionsBoxGsuite(prevChoices):  # Alternatively: getOptionsBox1()
        '''
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to
        other methods. These are lists of results, one for each input box
        (in the order specified by getInputBoxOrder()).

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - The contents is the default value shown inside the text area
        - Returns: string

        Raw HTML code:          '__rawstr__', 'HTML code'
        - This is mainly intended for read only usage. Even though more
        advanced hacks are possible, it is discouraged.

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:
        ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.

        History check box list:
        ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:
        [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:
         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return ('__history__',)

    @staticmethod
    def getOptionsBoxQuestion(prevChoices):  # Alternatively: getOptionsBox1()
        return ['question 6', 'question 7', 'question 8']

    @staticmethod
    def getOptionsBoxStat(prevChoices):
        return [
                'PropOfReferenceTrackInsideTargetTrackStat',
                'PropOfReferenceTrackInsideUnionStat',
                'RatioOfIntersectionToGeometricMeanStat',
                'RatioOfOverlapToUnionStat'
                ]

    @classmethod
    def getOptionsBoxSummaryFunc(cls, prevChoices):
        # Hack: Return raw html since this select box gives short uninformative names:

        if prevChoices.analysisName == cls.Q3:
            html = "<br><p>Select how to combine the computed statistic over tracks:</p><p><select name='summaryFunc'></p>" + \
               "<option value='avg'>Take the average over all tracks  (max not allowed when computing p-values)</option>" + \
               "</select></p>"
        else:
            html = "<br><p>Select how to combine the computed statistic over tracks:</p><p><select name='summaryFunc'>" + \
                   "<option value='avg'>Take the average over all tracks</option>" + \
                   "<option value='max'>Take the maximum value over all tracks</option>" + \
                   "</select></p>"

        return '__rawstr__', html

    @staticmethod
    def getOptionsBoxPermutationStrat(prevChoices):
        '''hardcoded for now to 'PermutedSegsAndIntersegsTrack' '''
        return None

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results
        page in Galaxy history. If getOutputFormat is anything else than HTML,
        the output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''



        cls._setDebugModeIfSelected(choices)


        # First compute pvalue by running the statistic through a wrapper stat that computes the max per bin
        """
        from quick.statistic.RandomizationManagerV3Stat import RandomizationManagerV3Stat
        from quick.statistic.CollectionBinnedHypothesisWrapperStat import CollectionBinnedHypothesisWrapperStat
        analysisSpec = AnalysisSpec(CollectionBinnedHypothesisWrapperStat)
        analysisSpec.addParameter("rawStatistic", "GenericMaxBinValueStat")
        analysisSpec.addParameter('perBinStatistic', 'SummarizedStat')
        analysisSpec.addParameter('mcSamplerClass', 'NaiveMCSamplingV2Stat')
        analysisSpec.addParameter('pairwiseStatistic', 'ProportionCountStat')
        analysisSpec.addParameter('summaryFunc', choices.summaryFunc)
        analysisSpec.addParameter('evaluatorFunc','evaluatePvalueAndNullDistribution')
        analysisSpec.addParameter('tail', 'right-tail')
        analysisSpec.addParameter('assumptions', 'RandomGenomeLocationTrack')
        analysisSpec.addParameter('maxSamples', 10)

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        tracks = [Track(x.trackName) for x in gsuite.allTracks()]

        regSpec, binSpec = cls.getRegsAndBinsSpec(choices)

        analysisBins = GalaxyInterface._getUserBinSource(regSpec,
                                                         binSpec,
                                                         choices.genome)
        results = doAnalysis(analysisSpec, analysisBins, tracks)

        print "<p>Max stat results:</p>"

        print results.getGlobalResult()
        """
        # Stat question 4
        summaryFunc = choices.summaryFunc if choices.summaryFunc else cls.SUMMARY_FUNC_DEFAULT
        statTxt = "Average"
        if(summaryFunc == "max"): statTxt = "Maximum"

        statDesc = 'number of <b>segments</b> per base'
        if choices.analysisName == cls.Q2:
            statDesc = 'number of <b>base pairs covered by segments</b>'


        core = HtmlCore()
        core.begin()
        core.header("Enrichment of GSuite tracks across regions")
        core.divBegin(divClass='resultsExplanation')
        core.paragraph('The following is a list of all regions (bins) and the <b>' + statTxt.lower() + '</b> ' + statDesc + ' across the tracks within each region.')
        core.divEnd()


        if choices.analysisName == cls.Q3:

            # Compute p-value per bin
            analysisSpec = AnalysisSpec(GSuiteBinEnrichmentPValWrapperStat)
            analysisSpec.addParameter('rawStatistic', 'BinSizeStat')
            #analysisSpec.addParameter('pairwiseStatistic', 'ProportionElementCountStat')
            #analysisSpec.addParameter('pairwiseStatistic', 'ProportionElementCountStat')
            #analysisSpec.addParameter('summaryFunc', summaryFunc)
            gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
            tracks = [Track(x.trackName) for x in gsuite.allTracks()]
            regSpec, binSpec = cls.getRegsAndBinsSpec(choices)
            from quick.statistic.GenericRelativeToGlobalStat import GenericRelativeToGlobalStatUnsplittable
            #analysisSpec.addParameter("globalSource", GenericRelativeToGlobalStatUnsplittable.getGlobalSource('test', choices.genome, False))
            analysisSpec.addParameter("globalSource", 'userbins')
            analysisBins = GalaxyInterface._getUserBinSource(regSpec,
                                                             binSpec,
                                                             choices.genome)
            results_pval = doAnalysis(analysisSpec, analysisBins, tracks)

        #print results_pval

        analysisSpec = AnalysisSpec(SummarizedWrapperStat)
        analysisSpec.addParameter('rawStatistic', 'SummarizedWrapperStat')

        countStat = 'ProportionElementCountStat'
        if choices.analysisName == cls.Q2:
            countStat = 'ProportionCountStat'

        # analysisSpec.addParameter('pairwiseStatistic', 'ProportionCountStat')
        analysisSpec.addParameter('pairwiseStatistic', countStat)
        analysisSpec.addParameter('summaryFunc', summaryFunc)
        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        tracks = [Track(x.trackName) for x in gsuite.allTracks()]

        regSpec, binSpec = cls.getRegsAndBinsSpec(choices)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec,
                                                         binSpec,
                                                         choices.genome)
        results = doAnalysis(analysisSpec, analysisBins, tracks)

        prettyResults = {}
        #print results

        for key, val in results.iteritems():
            if "Result" in val.keys():

                if choices.analysisName == cls.Q3:
                    prettyResults[key] = (val["Result"], results_pval[key]["Result"])
                else:
                    prettyResults[key] = (val["Result"])
            else:
                prettyResults[key] = "No result"

        topTrackTitle = results.keys()[0]
        """
        core.paragraph('''
            Suite data is coinciding the most in bin %s
        ''' % ('test'))
        """

        columnNames = ['Bin', 'Representation within the bin']
        if choices.analysisName == cls.Q3:
            columnNames.append('p-value')

        core.divBegin()
        if choices.analysisName == cls.Q1:
            shortQuestion = cls.Q1_SHORT
        elif choices.analysisName == cls.Q2:
            shortQuestion = cls.Q2_SHORT
        else:  # Q3
            shortQuestion = cls.Q3_SHORT

        visibleRows = 20
        makeTableExpandable = len(prettyResults) > visibleRows

        addTableWithTabularAndGsuiteImportButtons(
            core, choices, galaxyFn, shortQuestion, tableDict=prettyResults,
            columnNames=columnNames, sortable=True, presorted=0, expandable=makeTableExpandable)

        core.divEnd()
        core.end()


        print str(core)

        #print results



    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are
        not valid, an error text explaining the problem should be returned. The
        GUI then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are
        valid, the method should return None, which enables the execute button.
        '''

        errorString = GeneralGuiTool._checkGSuiteFile(choices.gsuite)
        if errorString:
            return errorString

        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        errorString = GeneralGuiTool._checkGSuiteRequirements(
            gSuite,
            allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
            allowedFileFormats=cls.GSUITE_ALLOWED_FILE_TYPES,
            allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES)

        if errorString:
            return errorString

        if choices.genome:
            errorString = cls.validateUserBins(choices)
            if errorString:
                return errorString

        return None

    @staticmethod
    def isDynamic():
        '''
        Specifies whether changing the content of texboxes causes the page to
        reload.
        '''
        return True

    @staticmethod
    def isDebugMode():
        '''
        Specifies whether the debug mode is turned on.
        '''
        return False

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'

    @staticmethod
    def isPublic():
        return True


    @staticmethod
    def getToolIllustration():
        '''
        Specifies an id used by StaticFile.py to reference an illustration file
        on disk. The id is a list of optional directory names followed by a file
        name. The base directory is STATIC_PATH as defined by AutoConfig.py. The
        full path is created from the base directory followed by the id.
        '''
        return ['illustrations', 'tools', 'enriched-regions.png']
