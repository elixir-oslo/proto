from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.AutoBinner import AutoBinner
from quick.util.CommonFunctions import createHyperBrowserURL
from quick.webtools.GeneralGuiTool import GeneralGuiTool


#This is a template prototyping GUI that comes together with a corresponding web page.
#

class NmerInspectTool(GeneralGuiTool):
    MAX_NUMBER_OF_BINS = 200
    
    @staticmethod
    def getToolName():
        return 'Inspect k-mer frequency variation'

    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Genome build: ', 'K-mer (any length): ', 'Region of the genome: ']
    
    @staticmethod    
    def getOptionsBox1(): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return '__genome__'
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        return ''

    @staticmethod    
    def getOptionsBox3(prevChoices):
        return '*'

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']

    @classmethod   
    def _calcBinSize(cls, nmer, analysisRegions):
        expectedCountPerBin = 10

        if len(nmer) < 15:
            totalBps = sum(x.getTotalBpSpan() for x in analysisRegions)
            minimumBinSize = totalBps / cls.MAX_NUMBER_OF_BINS
            #print 'BP: ', analysisRegion.getTotalBpSpan(), cls.MAX_NUMBER_OF_BINS
            #print 'next: ', minimumBinSize, expectedCountPerBin * 4**( len(nmer) ) 
            return max(minimumBinSize, expectedCountPerBin * 4**( len(nmer) ) ) 
        else:
            #will cover whole chroms anyway.. avoid any numeric issues..
            return None
    
    #@staticmethod    
    #def _calcNumBinsGW(genome, binSize):
    #    assert genome=='hg18'
    #    if binSize is None:
    #        return 24
    #    else:
    #        return 3*10**9 / binSize

    @staticmethod
    def getDemoSelections():
        #return ['sacCer1','aca','chr1']
        return ['hg18','aca','chr1:1-1m']
        
    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''

        from quick.application.UserBinSource import parseRegSpec

        genome = choices[0]
        nmer = choices[1].lower()
        regSpec = choices[2]
        analysisRegions = parseRegSpec(regSpec, genome)
        
        binSize = cls._calcBinSize(nmer, analysisRegions)
        binSpec = '*' if binSize is None else str( binSize ) 
        numBins = len( AutoBinner(analysisRegions, binSize) )
        
        from quick.application.GalaxyInterface import GalaxyInterface
        from quick.util.GenomeInfo import GenomeInfo
        trackName1 = GenomeInfo.getPropertyTrackName(genome, 'nmer') + [str(len(nmer))+'-mers',nmer]
        trackName2 = ['']
        analysisDef = 'Counts: The number of track1-points -> CountPointStat'
        #regSpec = '*'
        #print 'Using binSize: ',binSpec
        #print 'TN1: ',trackName1
        from proto.hyperbrowser.HtmlCore import HtmlCore
        print str(HtmlCore().styleInfoBegin(styleClass='debug'))
        GalaxyInterface.run(trackName1, trackName2, analysisDef, regSpec, binSpec, genome, galaxyFn)
        print str(HtmlCore().styleInfoEnd())

        plotFileNamer = GalaxyRunSpecificFile(['0','CountPointStat_Result_gwplot.pdf'], galaxyFn)
        textualDataFileNamer = GalaxyRunSpecificFile(['0','CountPointStat_Result.bedgraph'], galaxyFn)
        
        core = HtmlCore()
        core.paragraph('Inspect k-mer frequency variation as a %s or as underlying %s.</p>' % ( plotFileNamer.getLink('plot'), textualDataFileNamer.getLink('textual data') ))
        core.divider()
        core.paragraph('The occurrence frequency of your specified k-mer ("%s") has been computed along the genome, within your specified analysis region ("%s").' % (nmer, regSpec))
        core.paragraph('The analysis region was divided into %i bins, based on calculations trying to find appropriate bin size (get enough data per bin and restrict maximum number of bins).' % numBins)
        
        trackName1modified = trackName1[0:-2] + trackName1[-1:]
        preSelectedAnalysisUrl = createHyperBrowserURL(genome, trackName1modified, [''], analysis='Counts', method='__custom__', region=regSpec, binsize=binSpec)
        core.divider()
        core.paragraph('If you do not find the inferred bin size to be appropriate, you can set this manually in a ' + str(HtmlCore().link('new analysis', preSelectedAnalysisUrl)) + '.')
        print str(core)
                
    @staticmethod
    def isPublic():
        return True
    #
    @staticmethod
    def getToolDescription():
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.paragraph('Inspect the frequency variation of occurrences of a given k-mer in a specified region along the selected genome. The tool tries to determine appropriate binning of the specified region, and outputs the number of k-mer occurrences per bin as a plot and as underlying textual data.')
        core.divider()
        core.highlight('K-mer')
        core.paragraph('A string based on only the following characters: a, c, g, t, A, C, G, T. Eventual use of case has no effect.')
        core.divider()
        core.highlight('Region of the genome')
        core.paragraph('Region specification as in UCSC Genome browser. * means whole genome. k and m denotes thousand and million bps, respectively. E.g chr1:1-20m')
        return str(core)
        
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        
        if choices[0] in [None, '']:
            return 'Please select a genome build'
        
        nmer = choices[1]
        if nmer.strip() == '':
            return 'Please type in a k-mer'
        from gold.extra.nmers.NmerTools import NmerTools
        if not NmerTools.isNmerString(nmer):
            return NmerTools.getNotNmerErrorString(nmer)
            
        try:
            from quick.application.UserBinSource import parseRegSpec
            regs = parseRegSpec(choices[2], choices[0])
        except Exception, e:
            return str(e)
            
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    return True

    @staticmethod    
    def getOutputFormat(choices=None):
        return 'customhtml'
