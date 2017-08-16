import os

from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.GalaxyInterface import GalaxyInterface
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.DebugMixin import DebugMixin


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class BatchRunTool(GeneralGuiTool, DebugMixin):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Execute batch commands"

    @staticmethod
    def getInputBoxNames():
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
        return [ ('Insert batch commands (one line per run)', 'command')] +\
                DebugMixin.getInputBoxNamesForDebug()

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    #@staticmethod
    #def getOptionsBox1(): # Alternatively: getOptionsBoxKey()
    #    return '__genome__'



    @classmethod
    def getOptionsBoxCommand(cls):
        '''
        See getOptionsBox1().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return '', 14, False



    #@staticmethod
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod
    #def getOptionsBox4(prevChoices):
    #    return ['']

    @staticmethod
    def getDemoSelections():
        from urllib import quote
        return [quote(\
'''@trackName1a=Chromatin:Histone modifications:BLOC segments:MEFB1
@trackName1b=Chromatin:Histone modifications:BLOC segments:MEFF
@trackNames1=@trackName1a/@trackName1b
@trackName2=Sequence:Repeating elements:SINE

@nullModelParam1=assumptions=PermutedSegsAndSampledIntersegsTrack_
@nullModelParam2=assumptions=PermutedSegsAndIntersegsTrack_
@mcfdrParams=fdrCriterion=simultaneous,fdrThreshold=0.05,maxSamples=unlimited,globalPvalThreshold=0.005,numResamplings=10,mThreshold=20
@otherParams=randomSeed=0,tail=more,rawStatistic=TpRawSegsOverlapStat

@stat1=RandomizationManagerStat(@nullModelParam1,@mcfdrParams,@otherParams)
@stat2=RandomizationManagerStat(@nullModelParam2,@mcfdrParams,@otherParams)

mm8|chr17:3m-|5m|@trackNames1|@trackName2|@stat1/@stat2''')]

    @staticmethod
    def _removeIllegalLines(lines, username):
        if GalaxyInterface.userHasFullAccess(username):
            return lines
        else:
            return [x for x in lines if (len(x) > 0 and x[0] != '$') or \
                    x.startswith('$cluster')] # Hack to allow batch clustering

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
        cls._setDebugModeIfSelected(choices)

        batchStr = choices[0]
        batchLines = [x.strip() for x in batchStr.strip().split(os.linesep)]
        #batchLines = [x.strip() for x in choices[0].strip().split(os.linesep)]
        legalBatchLines = cls._removeIllegalLines(batchLines, username)

        if len(legalBatchLines) > 0:
            GalaxyInterface.runBatchLines(batchLines=legalBatchLines, galaxyFn=galaxyFn, \
                                          genome=None, username=username)
        else:
            return 'Your user does not have access to run these command lines.'

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        if choices[0].strip() == '':
            return ''


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

    @staticmethod
    def getToolDescription():
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''

        core = HtmlCore()
        core.paragraph('This tool is used to specify a set of analyses to be run in sequence, defined via a set of ' + \
                       str(HtmlCore().emphasize('batch command lines')) + '.')
        core.paragraph('Batch command lines can be found by ' +\
                       'clicking the "Inspect parameters of this analysis" link, either from the "Analyze genomic tracks" tool ' +\
                       'interface, or from the history element of previously run analyses. These batch run lines can then ' +\
                       'be copied to this tool and duplicated or modified if needed.')
        core.paragraph('The batch command lines are executed in sequence, that is, ' +\
                       'each batch command line is started only after the previous line has been fully executed.')

        core.divider()
        core.smallHeader('Batch command line format')
        core.styleInfoBegin(styleClass='debug', linesep=False)
        core.append('genome|regions|binsize|track1|track2|statistic')
        core.styleInfoEnd()
        core.descriptionLine('genome', 'The short name of the reference genome for the analysis (can be found in ' +\
                                        'the genome info box of the "Analyze genomic tracks" tool)', emphasize=True)
        core.descriptionLine('regions', 'The regions where the analysis should be performed, in the following format:' +\
                                        BatchRunTool._exampleText('seqid[:start-[end]],seqid[:start-[end]],...') +\
                                        str(HtmlCore().descriptionLine('seqid', 'The sequence id of the region, e.g. "chr1" for chromosome 1', \
                                                                       emphasize=True)) +\
                                        str(HtmlCore().descriptionLine('start', 'The start position of the region. If the start position ' +\
                                                                                'is omitted, the region starts at posision 1.', emphasize=True)) +\
                                        str(HtmlCore().descriptionLine('seqid', 'The end position of the region. If the end position is ' +\
                                                                                'omitted, the region ends at the end of the specified ' +\
                                                                                'sequence (e.g. chromosome 1).', emphasize=True)) +\
                                        'Note:' + str(HtmlCore().unorderedList( \
                                            ['All positions are 1-based, and end-inclusive (i.e. the first base pair ' +\
                                                'of the sequence has position 1, and the end position is included in the region). ', \
                                             str(HtmlCore().emphasize('k')) + ' and ' + str(HtmlCore().emphasize('m')) +\
                                                ' can be used for specifying thousand (kilo) and million (mega) base pairs, ' +\
                                                'respectively (e.g. "chr1:1k-2k" corresponds to "chr1:1001-2000").', \
                                             '* denotes all (standard) sequences of the reference genome, e.g. all chromosomes'])) +\
                                        'Examples: ' +\
                                        BatchRunTool._exampleText('chr1,chr2\nchr1:1001-1500\nchr2:1m-2m,chr2:3m-\n*'), emphasize=True)
        core.descriptionLine('binsize', 'The regions are further divided into smaller bins of this size. ' +\
                                        str(HtmlCore().indent( \
                                        'Note:' + str(HtmlCore().unorderedList( \
                                            [str(HtmlCore().emphasize('k')) + ' and ' + str(HtmlCore().emphasize('m')) +\
                                                ' denotes thousand and million base pairs, respectively', \
                                             '* denotes that the regions are not subdivided.'])) +\
                                        'Examples: ' +\
                                        BatchRunTool._exampleText('5000\n100k\n*'))), emphasize=True)
        core.descriptionLine('track1', 'The first track of the analysis. ' +\
                                        str(HtmlCore().indent( \
                                        'Note:' + str(HtmlCore().unorderedList( \
                                            ['Colon, ":", is used to separate the different levels of the track hierarchy', \
                                             str(HtmlCore().link('URL-encoding', 'http://www.w3schools.com/tags/ref_urlencode.asp')) + \
                                                ' is supported, as non-ASCII characters will not work', \
                                            'A special format, starting with "galaxy", is used to represent a track from history'])) +\
                                        'Examples: ' +\
                                        BatchRunTool._exampleText('Genes and gene subsets:Genes:CCDS\n' +\
                                                                  'Sequence:Repeating%20elements:SINE\ngalaxy:bed:%2Fusit%2Finvitro' +\
                                                                  '%2Fdata%2Fgalaxy%2Fgalaxy-dist-hg-stable%2Fdatabase%2Ffiles%2F028' +\
                                                                  '%2Fdataset_28276.dat:3%20-%20Extract%20track'))), emphasize=True)
        core.descriptionLine('track2', 'The second track of the analysis, specified in the same way as the first track. ' +\
                                        'If only a single track is to be analyzed, this field should be left empty', emphasize=True)
        core.descriptionLine('statistic', 'The specification of the analysis to run, and its parameters, in the following format:' +
                                        str(HtmlCore().indent( \
                                        BatchRunTool._exampleText('statisticClass(paramA=valueA,paramB=valueB,...)') +\
                                        'The exact specification possibilities, with different statistic classes and parameter values, ' +\
                                        'are diverse and extensive. However, one may easily find a particular specification by ' +\
                                        'specifying the analysis and parameters in the "Analyze genomic tracks" tool and clicking the ' +\
                                        '"Inspect parameters of this analysis" link.')), emphasize=True)

        core.divider()
        core.smallHeader('Region specification variants')
        core.paragraph('Other specifications of analysis regions are also supported, using both "regions" and "binsize" fields, as follows:')
        core.tableHeader(['regions', 'binsize (example)', 'description', ])
        core.tableLine([BatchRunTool._exampleText('__brs__'), BatchRunTool._exampleText(''), \
            'Use the bounding region of the track if only one track is specified, else use the intersection '
            'of the bounding regions of the two tracks'])
        core.tableLine([BatchRunTool._exampleText('__chrs__'), BatchRunTool._exampleText('chr1,chr2'), \
            'List of complete sequence ids of the reference genome, e.g. chromosome names'])
        core.tableLine([BatchRunTool._exampleText('__chrArms__'), BatchRunTool._exampleText('chr1q,chr2p'), \
            'List of chromosome arm names. (Note: not supported for all reference genomes)'])
        core.tableLine([BatchRunTool._exampleText('__genes__'), BatchRunTool._exampleText('ENSG00000208234,ENSG00000199674'), \
            'List of Ensembl gene ids. (Note: not supported for all reference genomes)'])
        core.tableLine([''.join([BatchRunTool._exampleText(x) for x in ['bed','gff','wig','bedgraph','gtrack']]), \
                        BatchRunTool._exampleText('/usit/invitro/data/galaxy/galaxy-dist-hg-stable/database/files/028/dataset_28276.dat'), \
                        'Internal path to a file of the specified format, containing custom regions'])
        core.tableFooter()

        core.divider()
        core.smallHeader('Multiple run expansion')
        core.paragraph('The batch command line format supports two options for automatic expansion of a single batch ' +\
                       'command line into multiple batch lines, thus supporting multiple analyses from a single line:')
        core.orderedList(['Multiple values of the ' + str(HtmlCore().emphasize('track1')) + ', ' + str(HtmlCore().emphasize('track2')) + ', and' +\
                          str(HtmlCore().emphasize('statistic')) + ' fields can be specified using the slash character, "/", as ' +\
                          'separator. If more than one field is specified this way, all combinations of the values are expanded and ' +\
                          'executed. Example expansion:' + \
                          BatchRunTool._exampleText('hg18|*|*|Genes and gene subsets:Genes:CCDS/Genes and gene subsets:Genes:Refseq||ProportionCountStat()/CountPointAllowingOverlapStat()') + \
                          'This expands to the following lines internally:' + \
                          BatchRunTool._exampleText('hg18|*|*|Genes and gene subsets:Genes:CCDS||ProportionCountStat()\n' +\
                                                    'hg18|*|*|Genes and gene subsets:Genes:CCDS||CountPointAllowingOverlapStat()\n' +\
                                                    'hg18|*|*|Genes and gene subsets:Genes:Refseq||ProportionCountStat()\n' +\
                                                    'hg18|*|*|Genes and gene subsets:Genes:Refseq||CountPointAllowingOverlapStat()'),
                          'All tracks under a specific hierarchy can be specified using the "*" character. This works for ' +\
                          'values of the ' + str(HtmlCore().emphasize('track1')) + ' and ' + str(HtmlCore().emphasize('track2')) +\
                          ' fields. This expansion is also combinatorical, in the same manner as with the "/" character, and can ' +\
                          'be freely combined with such notation. Example:' + \
                          BatchRunTool._exampleText('hg19|*|*|Genes and gene subsets:Genes:*|Chromatin:Chromatin State Segmentation:wgEncodeBroadHmmK562HMM:*|DerivedOverlapStat()') +\
                          'This batch command line will result in 30 analyses (2 gene tracks * 15 chromatin tracks).'])
        core.divider()
        core.smallHeader('Defining variables')
        core.paragraph('The batch command line format allows definition of variables using the following format:' +\
                       BatchRunTool._exampleText('@variable=value') +\
                       'To use a variable, simply enter the variable name with a starting "@" character in a batch ' +\
                       'command line. Example:' +\
                       BatchRunTool._exampleText('@trackname=Genes and gene subsets:Genes:CCDS\nhg18|*|*|@trackname||ProportionCountStat()') +\
                       'Nested variable declarations, i.e. defining a variable using previously defined variables, are also allowed. Example:' +\
                       BatchRunTool._exampleText('@TN1=Genes and gene subsets:Genes:CCDS\n' +\
                                  '@TN2=Genes and gene subsets:Genes:Refseq\n' +\
                                  '@TNs=@TN1/@TN2\n' +\
                                  'hg18|*|*|@TNs||ProportionCountStat()/CountPointAllowingOverlapStat()') +\
                       'Note:' +\
                        str(HtmlCore().unorderedList(['The variable names are case sensitive', \
                                                      '"=" characters are allowed in variable values'])))

        return str(core)

#'''
# Column format:
#
#Analysis-region Userbinsize Track1 Track2 Statistic
#
#(note that here, as in standard batch format, the Statistic must be specified as
#a statClassName. A mapping from questions to StatisticNames as needed in batch
#scripts can be found here.)
#
#(note that in contrast to the standard batch format, name of run is not
#specified in the super-batch format)
#
#Similar to standard batch-format, but with a few modifications to make it even
#faster to use:
#
#    Each column accepts entries divided by '/' When / is used in a single
#    column, runs are made for each of the options separated by / When / is used
#    in multiple columns, runs are made for each combination of options from each
#    of the columns. I.e. a cartesian product In the Statistic field, '/' will
#    also give results for every specified statistic, although this will be
#    achieved by a single run.
#
#The symbol '*' can be used to denote all subtypes of a track (e.g. repeats,*
#will mean each subtype of repeat). The same symbol (*) can also be used in the
#Statistic field, in which case it means all directly available statistics (that
#is, all Statistics that do not require any conversion of track-formats)
#
#Names are generated automatically from the values in each column (or perhaps
#instead as short IDs with a separate file mapping IDs to full selected values
#
#A file in super-batch-format will be converted to a file in standard
#batch-format by creating separate lines for each combination of options
#separated by '/', by expanding '*' in tracknames to create one line for each
#subtype, by exchanging '*' in Statistic field for all directly available
#Statistics (in the same line), and automatically creating names for the lines..
#'''
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
    @classmethod
    def isBatchTool(cls):
        '''
        Specifies if this tool could be run from batch using the batch. The
        batch run line can be fetched from the info box at the bottom of the
        tool.
        '''
        return False

    @staticmethod
    def isDebugMode():
        '''
        Specifies whether debug messages are printed.
        '''
        return True

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
