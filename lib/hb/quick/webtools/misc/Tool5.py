from quick.webtools.GeneralGuiTool import GeneralGuiTool

# This is a template prototyping GUI that comes together with a corresponding
# web page.

class Tool5(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Tool for simulating multiple track overlap"

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
        return ['Num experiments', 'Num elements per experiment', 'Num possible elements', 'Num HighProbElements', 'Prop. sampled from highProb', 'Fixed num sampled from highProb', 'Last TN part']
    
    @staticmethod    
    def getOptionsBox1():
        return ''
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        return ''
    
    @staticmethod    
    def getOptionsBox3(prevChoices):
        return ''
    
    @staticmethod    
    def getOptionsBox4(prevChoices):
        return ''
    
    @staticmethod    
    def getOptionsBox5(prevChoices):
        return ''

    @staticmethod    
    def getOptionsBox6(prevChoices):
        return ''

    @staticmethod    
    def getOptionsBox7(prevChoices):
        return ''

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        genome = 'hg19'
        lastTnPart = choices[6]
        autoTnName = '_'.join([''.join(x) for x in zip('npe,nhe,psh,fsh'.split(','), choices[2:6])])
        tn = ['Private','GK','VdrDepthSim',lastTnPart+'_'+autoTnName]

        cls.writeTrackData(choices, genome, tn)
        cls.standardizeTrackData(genome, tn)
        cls.preProcessTrackData(genome, tn, username)
        cls.analyseTrackData(genome, tn, username, galaxyFn)
    
    @staticmethod
    def standardizeTrackData(genome, tn):
        import quick.extra.StandardizeTrackFiles as StandTrackFiles
        arguments = [genome, ':'.join(tn), 'SplitFileToSubDirs'] + ['direction=coll_to_std']
        print 'Running standardizer with these arguments: ' + str(arguments)
        StandTrackFiles.runParserClass(arguments, printUsageWhenError=False)
    
    @staticmethod
    def preProcessTrackData(genome, tn,username):
        from gold.origdata.PreProcessTracksJob import PreProcessAllTracksJob
        PreProcessAllTracksJob(genome, tn, username=username, mergeChrFolders=True).process()
        
    @staticmethod
    def analyseTrackData(genome, baseTn, username, galaxyFn):        
        from quick.application.GalaxyInterface import GalaxyInterface
        print GalaxyInterface.getSubTrackNames(genome, baseTn, deep=False, username=username)
        allTns = [baseTn+[leafTn[0]] for leafTn in GalaxyInterface.getSubTrackNames(genome, baseTn, deep=False, username=username)[0] if leafTn!=None]
        mainTns = allTns[:2]
        extraTracks = '&'.join(['^'.join(tn) for tn in allTns[2:]])
        analysisDef = '[extraTracks=%s] -> ThreeWayCoverageDepthStat' %extraTracks
        print allTns, mainTns
        GalaxyInterface.runManual(mainTns, analysisDef, 'chr1:1-150m', '*', genome, galaxyFn=galaxyFn, username=username, \
                  printResults=True, printProgress=True, printHtmlWarningMsgs=True, applyBoundaryFilter=False, printRunDescription=True)
    
    @staticmethod
    def writeTrackData(choices, genome, tn):
        from gold.util.RandomUtil import random
        from gold.util.CommonFunctions import createCollectedPath
        from quick.util.CommonFunctions import ensurePathExists

        trackFn = createCollectedPath(genome, tn, 'simulatedTracks.category.bed')
        ensurePathExists(trackFn)
        trackFile = open(trackFn, 'w')
        #determinePossibilities
        numPossiblePositions = int(choices[2])
        spacingBetweenPositions = 1e3
        possiblePositions = [i*spacingBetweenPositions for i in range(1,int(numPossiblePositions))]
        numHighProbPositions = int(choices[3])
        highProbPossiblePositions = possiblePositions[0:numHighProbPositions]
        lowProbPossiblePositions = possiblePositions[numHighProbPositions:]
        
        largestPossiblePosition = possiblePositions[-1]
        print 'largestPossiblePosition: ', largestPossiblePosition/1e6, 'M'
        assert largestPossiblePosition<1.5e8 #just due to hardcoded analysis region below..
        
        
        sizePerPosition=591 #empirical across all VDR binding sites..
        print 'Total BpCoverage: ', len(possiblePositions) * sizePerPosition
        
        #make samples
        numExperiments = int(choices[0])
        proportionFromHighProbPositions = float(choices[4])
        fixedNumFromHighProbPositions = int(choices[5])
        #numPositionsPerExperiment = [3000]*9
        numPositionsPerExperiment = [int(x) for x in choices[1].split(',')] #[3073, 7118, 5290, 3059, 4051, 1021, 200, 610, 573]
        for experimentIndex in range(numExperiments):
            #sampledPositions = random.sample(possiblePositions, numPositionsPerExperiment[experimentIndex])
            numHighProbSamples = int(numPositionsPerExperiment[experimentIndex]*proportionFromHighProbPositions) + fixedNumFromHighProbPositions
            numLowProbSamples = numPositionsPerExperiment[experimentIndex]- numHighProbSamples
            print 'numHighProbSamples: %i, out of numHighProbPossiblePositions: %i' % (numHighProbSamples, len(highProbPossiblePositions))
            sampledPositions = random.sample(highProbPossiblePositions, numHighProbSamples ) \
                            + random.sample(lowProbPossiblePositions, numLowProbSamples )
            sampledSegments = [(position,position+sizePerPosition) for position in sampledPositions]
            for seg in sampledSegments:
                trackFile.write('\t'.join(['chr1','%i'%seg[0], '%i'%seg[1], 'T%i'%experimentIndex]) + '\n' )

        trackFile.close()

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
    #@staticmethod
    #def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
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
