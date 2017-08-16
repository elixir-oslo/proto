import zipfile

from quick.webtools.GeneralGuiTool import GeneralGuiTool


#This is a template prototyping GUI that comes together with a corresponding web page.
#

class GenerateRandomFastaFile(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Generate Markov background sequence"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        #can have two syntaxes: either a list of stings or a list of tuples where each tuple has two items(Name of box on webPage, name of getOptionsBox)
        return ['FASTA file from history', 'Order of Markov model', 'Number of random files to generate']

    @staticmethod    
    def getOptionsBox1():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return ('__history__','fasta')
    
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return '4'
    
        
    @staticmethod    
    def getOptionsBox3(prevChoices):
        return '1'

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']

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
        import subprocess
        import os
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
        from config.Config import HB_SOURCE_CODE_BASE_DIR
        from quick.application.ExternalTrackManager import ExternalTrackManager
        
        
        tempInStaticFile = GalaxyRunSpecificFile(['tempIn.txt'], galaxyFn)
        outStaticFile = GalaxyRunSpecificFile(['tempOut.fasta'], galaxyFn)
        #print os.getcwd()
        inFn = ExternalTrackManager.extractFnFromGalaxyTN( choices[0].split(':') )
        #print inFn
        tempOutFn = outStaticFile.getDiskPath(True)
        #print tempOutFn
        os.chdir(HB_SOURCE_CODE_BASE_DIR + '/third_party/nonpython')
        #print outStaticFile.getLink('output')
        markovOrder = int(choices[1])

        seqs = []     
        for line in open(inFn):
            if line.startswith('>'):
                seqs.append( [line[1:].strip(),[]] )
            else:
                seqs[-1][1].append(line.strip())
        for seq in seqs:
            seq[1] = ''.join(seq[1])
            
        pureSequence = ''.join( [seq[1] for seq in seqs])
        totalSeqLen = len(pureSequence)
        #pureSequence = ''.join([line.replace('\n','') for line in open(inFn) if not line.startswith('>')])
        tempInStaticFile.writeTextToFile(pureSequence)
        numSamples = int(choices[2])
        
        if numSamples>1:
            zipOutStatic = GalaxyRunSpecificFile(['randomFastas.zip'], galaxyFn)                
            zipOut = zipfile.ZipFile(zipOutStatic.getDiskPath(True),'w')
            
        for iteration in range(numSamples):
            if numSamples>1:
                fastaOutStatic = GalaxyRunSpecificFile(['random','s%s.fa'%iteration], galaxyFn)
                fastaOutFn = fastaOutStatic.getDiskPath(True)
            else:
                fastaOutFn = galaxyFn
            #fastaOutStatic = GalaxyRunSpecificFile(['random%s'%iteration], galaxyFn)
            #subprocess.call('javac',shell=True)
            #subprocess.call('javac',shell=False)
            #subprocess.call('javac MarkovModel.java',shell=True)
            subprocess.call('java MarkovModel %s %s %s >%s' % (tempInStaticFile.getDiskPath(), markovOrder, totalSeqLen, tempOutFn), shell=True )
            #subprocess.call('javac third_party/nonpython/MarkovModel.java')
            #subprocess.call('java third_party/nonpython/MarkovModel.java')
            pureMarkovSequence = open(tempOutFn).readline().strip()
            pmsIndex = 0
            fastaOutF = open(fastaOutFn,'w')
            for seq in seqs:
                fastaOutF.write('>'+seq[0]+os.linesep)
                nextPmsIndex = pmsIndex+len(seq[1])
                #seq.append(pureMarkovSequence[pmsIndex:nextPmsIndex])
                fastaOutF.write( pureMarkovSequence[pmsIndex:nextPmsIndex] + os.linesep)
                pmsIndex = nextPmsIndex
            fastaOutF.close()
            assert pmsIndex == totalSeqLen == len(pureMarkovSequence), (pmsIndex, totalSeqLen , len(pureMarkovSequence))
            if numSamples>1:
                #print 'Adding %s to archive' % fastaOutFn.split('/')[-1]
                zipOut.write(fastaOutFn, fastaOutFn.split('/')[-1])

        if numSamples>1:
            zipOut.close()
            print zipOutStatic.getLink('Zipped random sequences')

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        return None
    
    #@staticmethod
    #def isPublic():
    #    return False
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
    @staticmethod
    def getResetBoxes():
        return [0,1]
    #
    @staticmethod
    def getToolDescription():
        return '''Generates random files, corresponding to the original fasta-file in the number of sequences and their lengths.
If 'number of random files to generate' is 1, the output is a new fasta-file of random sequence.
If 'number of random files to generate' is larger than 1, output is a zip-file containing all the randomly generated fasta-files.
        '''
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
        if int(choices[2]) ==1:
            return 'fasta'
        else:
            return 'html'
    #
