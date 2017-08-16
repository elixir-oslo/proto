from quick.webtools.GeneralGuiTool import GeneralGuiTool


#This is a template prototyping GUI that comes together with a corresponding web page.
#

class CreateDnaBasedCustomTrackTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Generate bp-level track from DNA sequence"

    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Genome: ','Sliding window size: ','Custom expression: ', 'Indexing scheme'] #, 'Create track as: ', 'Track name: ']

    @staticmethod
    def getOptionsBox1():
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)
        '''
        return '__genome__'

    @staticmethod
    def getOptionsBox2(prevChoices):
        return '21'

    @staticmethod
    def getOptionsBox3(prevChoices):
        return '', 5

    @staticmethod
    def getOptionsBox4(prevChoices):
        return ['Index 0 is left-most position of sliding window', 'Index 0 is midpoint of sliding window']

    #@staticmethod
    #def getOptionsBox5(prevChoices):
    #    return ['History element', 'HyperBrowser track']
    #
    #@staticmethod
    #def getOptionsBox6(prevChoices):
    #    return '' if prevChoices[4] == 'HyperBrowser track' else None

    @staticmethod
    def getDemoSelections():
        from urllib import quote
        return ['phagelambda','21', quote('sum([g[i]+c[i] for i in winIndexes])'), 'Index 0 is left-most position of sliding window', 'History element', '']
        #return ['', 'testMit','21', 'sum([g[i]+c[i] for i in winIndexes])', 'Index 0 is left-most position of sliding window', 'Private:ToInsteadAppearInHistory']

    @classmethod
    def execute(cls, choices, galaxyFn, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        from quick.application.GalaxyInterface import GalaxyInterface

        genome = choices[0]
        winSize = choices[1]
        expression = choices[2]
        indexScheme = choices[3]
        assert indexScheme in ['Index 0 is left-most position of sliding window', 'Index 0 is midpoint of sliding window']
        midPointIsZero = (indexScheme == 'Index 0 is midpoint of sliding window')
        #if midPointIsZero:
            #print 'MIDPOINT!!'
        #else:
            #print choices[3]

        #if choices[4] == 'HyperBrowser track':
        #    trackName = choices[5]
        #else:
        trackName = 'galaxy:hbfunction:%s:Create track from DNA sequence' % galaxyFn

        # with open(galaxyFn, 'w+') as outputFile:
        print GalaxyInterface.getHbFunctionOutputBegin(galaxyFn, withDebug=True)

        GalaxyInterface.createDnaBasedCustomTrack(genome, trackName, winSize, expression, midPointIsZero)

        infoMsg = 'A custom track has been created by applying the expression "%s" on DNA sequence of a sliding window of size %s along the genome (%s).' % (expression, winSize,indexScheme)
        print GalaxyInterface.getHbFunctionOutputEnd(infoMsg, withDebug=True)


    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (also if the text isempty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        genome, errorStr = CreateDnaBasedCustomTrackTool._getGenomeChoice(choices, genomeChoiceIndex=0)
        if errorStr:
            return errorStr

        winSize = choices[1]
        expression = choices[2]
        from quick.application.GalaxyInterface import GalaxyInterface
        return GalaxyInterface.validateDnaBasedExpressionAndReturnError(winSize, expression)

    @staticmethod
    def getToolDescription():
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.paragraph('Creates a function track based on a custom expression applied on a sliding windows across the genome.')
        core.divider()
        core.paragraph('''For each position in the selected genome, the supplied custom expression is evaluated for the DNA sequence of a window of selected size around the region. Details on the expression format:''')
        core.paragraph( str(HtmlCore().unorderedList(['The DNA sequence of this window is available in a variable "s". Thus s[0] will give the bp letter at position 0', '''A binary vector (list) named "a" is available, where the value of a[i] is 1 if the base pair at position i is A, if not, the value is 0. ("a[i]" is thus identical to the expression "1 if s[i]=='a' else 0". Similarly, there are vectors c,g,t,n. )''', 'The variable "winSize" gives the window size', 'The variable "winIndexes" gives a list of all index positions in the window (thus, winIndexes is equivalent to "range(len(s))").', 'All 1-letter variables are usable if defined in the expression.', 'The following words (2 or more letters) are allowed: sum, max, min, if, else, for, in, len, range', 'The expression must follow python/numpy syntax.'])) )
        core.divider()
        core.paragraph('One can choose whether index 0 should be the left-most position of sliding window (with n-1 being right-most), or whether index 0 should be midpoint, that is the same position that gets assigned the computed value (so that left-most is index "-n/2" and right-most is "n/2").')
        core.divider()
        core.paragraph('''Example of custom expression, computing GC content in a sliding window: <br>''')
        core.append(CreateDnaBasedCustomTrackTool._exampleText('sum([g[i]+c[i] for i in winIndexes])'))
        #core.paragraph('''A full example of how this tool can be used is given through a %s.''' % str(HtmlCore().link('Galaxy Page', 'http://hyperbrowser.uio.no/test/u/vegard/p/create-track-from-dna-sequence')))
        #core.paragraph('''<a href=http://hyperbrowser.uio.no/test/u/vegard/p/create-track-from-dna-sequence target=_top>See full example</a> of how to use this tool.''')

        return str(core)

    @staticmethod
    def getFullExampleURL():
        return 'u/hb-superuser/p/generate-bp-level-track-from-dna-sequence'

    @staticmethod
    def isPublic():
        return True

    @staticmethod
    def getOutputFormat(choices=None):
        return 'hbfunction'
