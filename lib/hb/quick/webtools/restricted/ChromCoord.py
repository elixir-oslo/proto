import os
from quick.webtools.GeneralGuiTool import GeneralGuiTool

class ChromPosition(object):
    def __init__(self, genome):
        #self._bedFile = bedFile
        self._genome = genome
        self._chrSizesFile = '.'.join([genome,'chrom','sizes'])
        #self._outFile = '.'.join([self._bedFile,'pos'])
        #if outFile != None:
        #   self._outFile = outFile
        self._BED = None
    
    # # def readBED(self,text):
    # #     lines = text.split('\n')
    # #     BED = []
    # #     for l in lines:
    # #        BED.append((l.split('\t')[0],[int(l.split('\t')[1]),int(l.split('\t')[2])]))
    # #        #BED[l.split('\t')[0]] = [int(l.split('\t')[1]),int(l.split('\t')[2])]
    # #     self._BED = BED
                
    def readBEDFile(self, bedFile):
        with open(bedFile,'r') as f:
             lines = f.readlines()
        
        #BED = defaultdict(list)
        BED = []
        for l in lines:
           BED.append((l.split('\t')[0],[int(l.split('\t')[1]),int(l.split('\t')[2])]))
           #BED[l.split('\t')[0]] = [int(l.split('\t')[1]),int(l.split('\t')[2])]    
        self._BED = BED
              
    def getChromPos(self):
        try:
            scriptPath = os.path.abspath(os.path.dirname(__file__)) + '/bin/fetchChromSizes.sh'
            os.system(' '.join(['sh %s' % scriptPath,\
                         self._genome, '>',\
                         self._chrSizesFile]))
        except Exception as e:
               print 'Error: ' + e.strerror
                         
        with open(self._chrSizesFile,'r') as f:
             lines = f.readlines()
        
        #os.remove(self._chrSizesFile)
        chromPos = {}
        pos = 0
        for l in lines:
            size = int(l.split('\t')[1])
            chromPos.update({l.split('\t')[0]: pos})
            pos += size
        return chromPos
    
    def produce(self, outFile = None):
        chromPos = self.getChromPos()
        result = []
        isPointBED = True
        for el in self._BED:
            pos = chromPos[el[0]]
            #self._BED[k] = [i + pos for i in self._BED[k]]
            #out.append('\t'.join([k,self._BED[k][0],self._BED[k][1]]))
            el[1]
            result.append([el[0],el[1][0] + pos,el[1][1] + pos])
            if (el[1][1] - el[1][0]) > 1:
               isPointBED = False
               
        if outFile != None:
           with open(outFile,'w') as f:
                if isPointBED:
                   f.writelines(str(l[1])+'\n' for l in result)
                else:
                   f.writelines('\t'.join([str(l[1]),str(l[2])+'\n']) for l in result)
        else:
             for l in result:
                if isPointBED:
                   print str(l[1])+'\n'
                else: 
                   print '\t'.join([str(l[1]),str(l[2])]) 
        return result
    
##########################################################################
class ChromCoord(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Chr-coordinates to coordinates without chr-specifier"

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

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('Genome', 'genome'),\
                ('BED File Data', 'bedData')]

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
    def getOptionsBoxGenome(): 
        '''
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to other
        methods. These are lists of results, one for each input box (in the
        order specified by getInputBoxOrder()).

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - The contents is the default value shown inside the text area
        - Returns: string

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.

        History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return '__genome__'
        

    @staticmethod
    #def getOptionsBox2(prevChoices): # Syntax 1 (old version)
    def getOptionsBoxBedData(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        #return ('', 4, False)
        return ('__history__','bed','point.bed')

    # # @staticmethod
    # # #def getOptionsBox3(prevChoices): # Syntax 1 (old version)
    # # def getOptionsBoxPrev(prevChoices):
    # #     #return repr(prevChoices),3,True
    # #     from proto.hyperbrowser.HtmlCore import HtmlCore
    # #
    # #     core = HtmlCore()
    # #     core.link('Download', 'ftp://something.com/')
    # #
    # #     return [['a','b','c'], [str(core),'2','3'], ['4','5','6']]

    #@staticmethod
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        c = ChromPosition(choices.genome)
        bedFile = choices.bedData.split(':')[2]
        c.readBEDFile(bedFile)
        c.produce(galaxyFn)
        

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        if not choices.genome:
           return 'You must provide a genome'
        
        #try:
        #    int(choices.genome)
        #except:
        #    return 'The first number is not an integer: '+ choices.genome

        #return '' # Greyed out, but no error message

    @staticmethod
    def getOutputFormat(choices):
        return 'txt'

#########################################################################



